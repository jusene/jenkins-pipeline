try{
    stage("Sonar Scan") {
        parallel backend: {
            node('slave-01') {
                stage('检测物联网后端开发代码') {
                    git branch: "dev", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/BE/iot-parent.git"
                    sh "mvn clean install -Dmaven.test.skip=true"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e dev -p iot -t backend"
                    sh "rm -rf *"
                }

                stage('检测物联网后端测试代码') {
                    git branch: "test", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/BE/iot-parent.git"
                    sh "mvn clean install -Dmaven.test.skip=true"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e test -p iot -t backend"
                    sh "rm -rf *"

                }

                stage('检测物联网后端生产代码') {
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/BE/iot-parent.git"
                    sh "mvn clean install -Dmaven.test.skip=true"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e prod -p iot -t backend"
                    sh "rm -rf *"

                }

                stage('检测大数据后端开发代码') {
                    git branch: "dev", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/BigData1/BE/bigdata-cloud2.0.git"
                    sh "mvn clean install -Dmaven.test.skip=true"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e dev -p bigdata -t backend"
                    sh "rm -rf *"
                }

                stage('检测大数据后端测试代码') {
                    git branch: "test", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/BigData1/BE/bigdata-cloud2.0.git"
                    sh "mvn clean install -Dmaven.test.skip=true"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e test -p bigdata -t backend"
                    sh "rm -rf *"

                }

                stage('检测大数据后端生产代码') {
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/BigData1/BE/bigdata-cloud2.0.git"
                    sh "mvn clean install -Dmaven.test.skip=true"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e prod -p bigdata -t backend"
                    sh "rm -rf *"

                }
            }
        },
        foretend: {
            node('slave-02') {
                stage('检测物联网user前端开发代码') {
                    git branch: "dev", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot_user_web.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e dev -p iot -t foretend -a iot_user_web"
                    sh "rm -rf *"
                }

                stage('检测物联网user前端测试代码') {
                    git branch: "test", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot_user_web.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e test -p iot -t foretend -a iot_user_web"
                    sh "rm -rf *"

                }


                stage('检测物联网user前端生产代码') {
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot_user_web.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e prod -p iot -t foretend -a iot_user_web"
                    sh "rm -rf *"

                }

                stage('检测物联网admin前端开发代码') {
                    git branch: "dev", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot-wx-web.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e dev -p iot -t foretend -a iot-wx-web"
                    sh "rm -rf *"
                }

                stage('检测物联网admin前端测试代码') {
                    git branch: "test", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot-wx-web.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e test -p iot -t foretend -a iot-wx-web"
                    sh "rm -rf *"

                }

                stage('检测物联网admin前端生产代码') {
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot-wx-web.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e prod -p iot -t foretend -a iot-wx-web"
                    sh "rm -rf *"

                }

                stage('检测物联网wx前端开发代码') {
                    git branch: "dev", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot-wx.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e dev -p iot -t foretend -a iot-wx"
                    sh "rm -rf *"
                }

                stage('检测物联网wx前端测试代码') {
                    git branch: "test", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot-wx.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e test -p iot -t foretend -a iot-wx"
                    sh "rm -rf *"

                }

                stage('检测物联网wx前端生产代码') {
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot-wx.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e prod -p iot -t foretend -a iot-wx"
                    sh "rm -rf *"
                }

                stage('检测物联网node-wx前端开发代码') {
                    git branch: "dev", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot-wx-node.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e dev -p iot -t foretend -a iot-wx-node"
                    sh "rm -rf *"
            
                }

                stage('检测物联网node-wx前端测试代码') {
                    git branch: "test", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot-wx-node.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e test -p iot -t foretend -a iot-wx-node"
                    sh "rm -rf *"

                }

                stage('检测物联网node-wx前端生产代码') {
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/IoT2/FE/iot-wx-node.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e prod -p iot -t foretend -a iot-wx-node"
                    sh "rm -rf *"

                }

                stage('检测大数据前端开发代码') {
                    git branch: "dev", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/BigData1/FE/huayun-web.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e dev -p bigdata -t foretend -a huayun-web"
                    sh "rm -rf *"
                }


                stage('检测大数据前端测试代码') {
                    git branch: "test", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/BigData1/FE/huayun-web.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e test -p bigdata -t foretend -a huayun-web"
                    sh "rm -rf *"
                }

                stage('检测大数据前端生产代码') {
                    git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/BigData1/FE/huayun-web.git"
                    sh "cp -rf ../../sonar/* ."
                    sh "python sonar.py -e prod -p bigdata -t foretend -a huayun-web"
                    sh "rm -rf *"
                }
            }
        }
    }
} catch(err) {
    echo "Caught: ${err}"
} finally {
    node('slave-01') {
        cleanWs()
    }
    node('slave-02') {
        cleanWs()
    }
}