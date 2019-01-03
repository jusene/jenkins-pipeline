node("master") {
    try {
        stage("拉取部署代码库") {
            git branch: "master", credentialsId: '891746d8-70de-4910-a0ee-d1b4c110adf6', url: "http://192.168.55.156:8090/ops/NCD.git"
        }
        
        stage("同步服务器系统时间和硬件时间") {
            sh "ansible ${HOSTS} -m yum -a \"name=ntpdate,crontabs,vixie-cron state=latest\""
            sh "ansible ${HOSTS} -m service -a \"name=crond state=started\""
            sh "ansible ${HOSTS} -m cron -a \"name='ntpdate time' job='/usr/sbin/ntpdate ntp1.aliyun.com && hwclock -w &> /dev/null' minute='*/5' user=root\""
        }

        stage("关闭selinux") {
            sh "ansible ${HOSTS} -m lineinfile -a \"path=/etc/selinux/config regexp='^SELINUX=' line='SELINUX=disable'\""
        }

        stage("同步服务器内核参数") {
            sh "ansible ${HOSTS} -m copy -a \"src=./files/sysctl.conf dest=/etc/sysctl.conf mode=0644\""
            sh "ansible ${HOSTS} -a \"sysctl -p\""
        }

        stage("同步服务器limits参数") {
            sh "ansible ${HOSTS} -m file -a \"path=/etc/security/limits.d/90-nproc.conf state=absent\""
            sh "ansible ${HOSTS} -m copy -a \"src=./files/limits.conf dest=/etc/security/limits.conf mode=0644\""
        }
        
        // 统一服务器风格
        stage("同步服务器banner") {
            sh "ansible ${HOSTS} -m copy -a \"src=./files/motd dest=/etc/motd mode=0644\""
        }

        stage("同步服务器PS1") {
            sh "ansible ${HOSTS} -m copy -a \"src=./files/PS1.sh dest=/etc/profile.d/PS1.sh mode=0644\""
        }
    } catch(err) {
        echo "Caught: ${err}"
    } finally {     
        cleanWs()
    }
}