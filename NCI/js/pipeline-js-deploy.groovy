try{
    if ( "${ROLLBACK}" ) {
        node('master') {
            stage('拉取部署代码') {
                git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/ops/NCD.git"
            }
            
            if ("${BRANCH}" == 'master') {
                env.BRANCH = 'prod'
            }

            stage("回滚版本${ROLLBACK}") {
                sh "python deploy.py -a ${APPNAME} -r ${APPNAME} -e ${BRANCH} -u http://192.168.55.156:88 -t ${ROLLBACK} -d ${DIR}"
            }
        }
    } else {
            echo "Build App ${APPNAME}"
            // 打包
            node('slave-02') {
                stage('拉取项目代码') {
                    git branch: "${BRANCH}", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "${GIT_URL}"
                    env.check_to_tag = "$TAG"
                    sh '[ -n "${check_to_tag}" ] && git checkout ${check_to_tag} || echo "checkout ${check_to_tag} is not exist or none!"'
                }
                if ("${BRANCH}" == 'master') {
                    env.BRANCH = 'prod'
                }

                stage('npm install') {
                    sh "npm install --registry http://192.168.66.95:8090"
                }

                stage('npm run build前端编译') {
                    sh "npm run build --registry http://192.168.66.95:8090"
                }

                stage('Do Package打包') {
                    sh "cd dist; tar -czvf ${APPNAME}.tar.gz *"
                }

                stage('传输包到存储服务器') {
                    //commitChangeset = sh(returnStdout: true, script: 'git rev-parse HEAD | cut -c 1-7').trim()
                    datetime = sh(returnStdout: true,script: 'date +%F_%H:%M:%S')
                    sh "ssh root@192.168.66.94 'mkdir -p /ddhome/package/${PROJECT}/${VERSION}/FE/${BRANCH}/${datetime}'"
                    sh "scp ${PACKAGE_DIR}/${APPNAME}.tar.gz root@192.168.66.94:/ddhome/package/${PROJECT}/${VERSION}/FE/${BRANCH}/${datetime}"
                    sh "ssh root@192.168.66.94 'chown -R nginx /ddhome/package'"
                }
            }

            // 发布
            node('master') {
                stage('拉取部署代码') {
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/ops/NCD.git"
                }

                stage("发布${BRANCH}环境"){
                    sh "python deploy.py -a ${APPNAME} -p ${PROJECT} -v ${VERSION} -d ${DIR} -e ${BRANCH} -u http://192.168.66.94:88 -t ${datetime}"
                }
            }
        }   
} catch(err) {
     echo "Caught: ${err}"
} finally {
    node('master') {
        cleanWs()
    }
    node('slave-02') {
        cleanWs()
    }
}

