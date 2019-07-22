try{
    if ( "${ROLLBACK}" ) {
            node('master') { 
                stage('拉取部署代码') {
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/ops/NCD.git"
                }

                if ("${BRANCH}" == 'master') {
                    env.BRANCH = 'prod'
                }

                 stage("发布kubernetes环境") {
                        sh "python deploy_k8s.py -a ${RUN_APPNAME} -p ${PROJECT} -e ${BRANCH} -t ${ROLLBACK}"
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

                stage('构建docker镜像') {
                    datetime = sh(returnStdout: true,script: 'date +%s')
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/ops/Dockerbuild.git"
                    sh "python build.py -a ${RUN_APPNAME} -p ${PROJECT} -v ${VERSION} -e ${BRANCH} -t ${datetime}"
            }
        }
    
            // 发布
                node('master') {
                    stage("拉取部署代码") {
                        git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/ops/NCD.git"
                    }
                    stage("发布kubernetes环境") {
                        sh "python deploy_k8s.py -a ${RUN_APPNAME} -p ${PROJECT} -e ${BRANCH} -t ${datetime}"
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

