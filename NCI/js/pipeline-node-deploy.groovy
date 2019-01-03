node('master') {
    try{
        if ( "${ROLLBACK}" ) {
            stage('拉取部署代码') {
                git branch: "master", credentialsId: '891746d8-70de-4910-a0ee-d1b4c110adf6', url: "http://192.168.55.156:8090/ops/NCD.git"
            }

            stage("回滚版本${ROLLBACK}") {
                sh "python deploy_node.py -a ${APPNAME} -r ${APPNAME} -e ${BRANCH} -u http://192.168.55.156:88 -t ${ROLLBACK} -d ${DIR}"
            }
        } else {
            echo "Build App ${APPNAME}"

            stage('拉取项目代码') {
                git branch: "${BRANCH}", credentialsId: '891746d8-70de-4910-a0ee-d1b4c110adf6', url: "${GIT_URL}"
                env.check_to_tag = "$TAG"
                sh '[ -n "${check_to_tag}" ] && git checkout ${check_to_tag} || echo "checkout ${check_to_tag} is not exist or none!"'
            }

            stage('npm install') {
                sh "npm install"
            }
            
            stage('Do Package打包') {
                sh "tar -czvf ${APPNAME}.tar.gz *"
            }

            stage('传输包到存储服务器') {
                //commitChangeset = sh(returnStdout: true, script: 'git rev-parse HEAD | cut -c 1-7').trim()
                datetime = sh(returnStdout: true,script: 'date +%F_%H:%M:%S')
                sh "ssh root@127.0.0.1 'mkdir -p /ddhome/package/${PROJECT}/${VERSION}/FE/${BRANCH}/${datetime}'"
                sh "scp ${APPNAME}.tar.gz root@127.0.0.1:/ddhome/package/${PROJECT}/${VERSION}/FE/${BRANCH}/${datetime}"
                sh "chown -R www.www /ddhome/package"
            }

            stage('拉取部署代码') {
                git branch: "master", credentialsId: '891746d8-70de-4910-a0ee-d1b4c110adf6', url: "http://192.168.55.156:8090/ops/NCD.git"
            }
        
            stage("发布${BRANCH}环境"){
                sh "python deploy.py -a ${APPNAME} -p ${PROJECT} -v ${VERSION} -d ${DIR} -f ${FIRST} -n ${NODEJS_NAME} -e ${BRANCH} -u http://192.168.55.156:88 -t ${datetime}"
            }
        }   
    } catch(err) {
         echo "Caught: ${err}"
    } finally {
         cleanWs()
    }
}
