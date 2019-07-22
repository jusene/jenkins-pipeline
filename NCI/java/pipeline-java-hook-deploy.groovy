try{
    // 打包
    node('slave-01') {
        stage('拉取项目代码') {
            git branch: "${BRANCH}", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "${GIT_URL}"
        }

        stage('删除nexus的beans和facade') {
            sh "python -c 'from celery import Celery;app=Celery(\"proj\",broker = \"amqp://rabbitadmin:rabbitadmin@192.168.55.91:5672//celery\");app.send_task(\"proj.tasks.remoteCmd\",[\"192.168.66.95,\",\"rm -rf /ddhome/bin/sonatype-work/nexus/storage/thirdparty/com/huawei/edu/beans\"]);app.send_task(\"proj.tasks.remoteCmd\",[\"192.168.66.95,\",\"rm -rf /ddhome/bin/sonatype-work/nexus/storage/thirdparty/com/huawei/edu/facade\"])'"
        }

        stage('上传jar到nexus') {                                         
            sh "mvn clean deploy -f pom.xml"
        }

        stage('清理本地beans和facade') {
            sh "python -c 'from celery import Celery;app=Celery(\"proj\",broker = \"amqp://rabbitadmin:rabbitadmin@192.168.55.91:5672//celery\");app.send_task(\"proj.tasks.remoteCmd\", [\"192.168.66.92,\",\"rm -rf /root/.m2/repository/com/huawei/edu/beans\"]);app.send_task(\"proj.tasks.remoteCmd\", [\"192.168.66.92,\",\"rm -rf /root/.m2/repository/com/huawei/edu/facade\"])'"
        }
    }
} catch (err) {
         echo "Caught: ${err}"
} finally {
    node('slave-01') {
        cleanWs()
    }        
}

