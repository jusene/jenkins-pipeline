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
                    sh "python deploy_multi.py -a ${RUN_APPNAME} -p ${PROJECT} -v ${VERSION} -e ${BRANCH} -u http://192.168.66.94:88 -t ${ROLLBACK}"
                }
            } 

    } else {

            echo "Build App ${RUN_APPNAME}"

            // 打包
            node('slave-01') {
                stage('拉取项目代码') {
                    git branch: "${BRANCH}", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "${GIT_URL}"
                    env.check_to_tag = "$TAG"
                    sh '[ -n "${check_to_tag}" ] && git checkout ${check_to_tag} || echo "checkout ${check_to_tag} is not exist or none!"'
                }

                def s1 = "${BRANCH}"

                if  ( s1 == 'master' ) {
                    env.BRANCH = 'prod'
                } else {
                    if (s1.startsWith('dev')) {
                        env.BRANCH = 'dev'
                    } else if (s1.startsWith('test')) {
                        env.BRANCH = 'test'
                    } else if (s1.startsWith('pre')){
                        env.BRANCH = 'pre'
                    } else {
                        echo "unkown branch"
                    }
                }


                stage('Do Package打包') {
                    if ("${PROJECT}" == 'iot') {
                        sh "mvn clean install -Dmaven.test.skip=true -pl iot-beans,iot-facade,iot-common,${RUN_APPNAME} -f pom.xml"
                    } else {
                        sh "mvn clean install -Dmaven.test.skip=true -f pom.xml"
                    }
                }

                stage('传输包到存储服务器') {
                    //commitChangeset = sh(returnStdout: true, script: 'git rev-parse HEAD | cut -c 1-7').trim()
                    datetime = sh(returnStdout: true,script: 'date +%F_%H:%M:%S')
                    sh "ssh root@192.168.66.94 'mkdir -p /ddhome/package/${PROJECT}/${VERSION}/BE/${BRANCH}/${datetime}'"
                    sh "find . -name '*-zjhw.jar' -type f | xargs -t -i scp {} root@192.168.66.94:/ddhome/package/${PROJECT}/${VERSION}/BE/${BRANCH}/${datetime}"
                    if ("${PROJECT}" == 'bigdata') {
                        sh "find . -name '*.sh' -type f | xargs -t -i chmod +x {}"
                        sh "ssh root@192.168.66.94 'mkdir -p /ddhome/package/${PROJECT}/${VERSION}/BIN/${BRANCH}/${datetime}'"
                        sh "cd ./spring-cloud-huayun-labs/huayun-lab-auth/target; tar -czvf huayun-lab-auth.tar.gz bin"
                        sh "scp ./spring-cloud-huayun-labs/huayun-lab-auth/target/huayun-lab-auth.tar.gz root@192.168.66.94:/ddhome/package/${PROJECT}/${VERSION}/BIN/${BRANCH}/${datetime}"
                        sh "cd ./spring-cloud-huayun-labs/huayun-lab-report/target; tar -czvf huayun-lab-report.tar.gz bin"
                        sh "scp ./spring-cloud-huayun-labs/huayun-lab-report/target/huayun-lab-report.tar.gz root@192.168.66.94:/ddhome/package/${PROJECT}/${VERSION}/BIN/${BRANCH}/${datetime}"
                        sh "cd ./spring-cloud-huayun-labs/huayun-lab-data/target; tar -czvf huayun-lab-data.tar.gz bin"
                        sh "scp ./spring-cloud-huayun-labs/huayun-lab-data/target/huayun-lab-data.tar.gz root@192.168.66.94:/ddhome/package/${PROJECT}/${VERSION}/BIN/${BRANCH}/${datetime}"
                    }
                    sh "ssh root@192.168.66.94 'chown -R nginx /ddhome/package'"
                }
            }
            // 发布
            node('master') {
                stage('拉取部署代码') {
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/ops/NCD.git"
                }

                stage("发布${BRANCH}环境"){
                    sh "python deploy_multi.py -a ${RUN_APPNAME} -p ${PROJECT} -v ${VERSION} -e ${BRANCH} -u http://192.168.66.94:88 -t ${datetime}"
                } 
            }
    }
} catch (err) {
         echo "Caught: ${err}"
} finally {
    node('master') {
        cleanWs()
    }
    node('slave-01') {
        cleanWs()
    }        
}

