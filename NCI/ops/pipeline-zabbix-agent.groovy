node("master") {
    try {
        stage("拉取部署代码库") {
            git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/ops/NCD.git"
        }

        stage("创建zabbix用户") {
	      sh "ansible ${HOSTS} -m group -a \"name=zabbix state=present\""
            sh "ansible ${HOSTS} -m user -a \"name=zabbix shell=/sbin/nologin group=zabbix\""
        }

        stage("yum安装依赖包") {
            sh "ansible ${HOSTS} -m yum -a \"name=gcc,pcre-devel,wget state=latest\""
        }

        stage("源码安装zabbix_agent") {
            sh "ansible ${HOSTS} -a \"wget http://192.168.66.98:8000/ops/lnmp_soft/zabbix-3.4.4.tar.gz -P /ddhome/tools\""
            sh "ansible ${HOSTS} -a \"chdir=/ddhome/tools tar -xf zabbix-3.4.4.tar.gz\""
            sh "ansible ${HOSTS} -a \"chdir=/ddhome/tools/zabbix-3.4.4 ./configure --enable-agent\""
            sh "ansible ${HOSTS} -a \"chdir=/ddhome/tools/zabbix-3.4.4 make -j 4\""
            sh "ansible ${HOSTS} -a \"chdir=/ddhome/tools/zabbix-3.4.4 make install\""
        }

        stage("拷贝启动脚本") {
            sh "ansible ${HOSTS} -m shell -a \"cp /ddhome/tools/zabbix-3.4.4/misc/init.d/fedora/core/zabbix_agentd /etc/init.d/\""
        }

        stage("上传配置文件") {
            sh "ansible ${HOSTS} -m copy -a \"src=./files/zabbix_agentd.conf dest=/usr/local/etc/zabbix_agentd.conf mode=0644\""
        }

        stage("启动agent服务") {
            sh "ansible ${HOSTS} -m service -a \"name=zabbix_agentd state=started enabled=true\""
        }

    } catch(err) {
        echo "Caught: ${err}"
    } finally {     
        cleanWs()
    }
}
