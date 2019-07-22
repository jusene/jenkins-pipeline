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

                stage('构建docker镜像') {
                    datetime = sh(returnStdout: true,script: 'date +%s')
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/ops/Dockerbuild.git"
                    sh "python build.py -a ${APPNAME} -p ${PROJECT} -v ${VERSION} -e ${BRANCH} -d ${DIR} -t ${datetime}"
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

