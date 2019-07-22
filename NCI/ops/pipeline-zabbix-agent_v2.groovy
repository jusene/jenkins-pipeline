node("master") {
    try {
        stage("拉取部署代码库") {
            git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/ops/NCD.git"
        }

        stage("安装agent") {
            sh "ansible ${HOSTS} -m shell -a \"rpm -Uvh http://repo.zabbix.com/zabbix/3.4/rhel/6/x86_64/zabbix-agent-3.4.4-1.el6.x86_64.rpm\""
        }

        stage("上传配置文件") {
            sh "ansible ${HOSTS} -m copy -a \"src=./files/zabbix_agentd.conf dest=/etc/zabbix/zabbix_agentd.conf mode=0644\""
        }

        stage("启动agent服务") {
            sh "ansible ${HOSTS} -m service -a \"name=zabbix-agent state=started enabled=true\""
        }

    } catch(err) {
        echo "Caught: ${err}"
    } finally {     
        cleanWs()
    }
}
