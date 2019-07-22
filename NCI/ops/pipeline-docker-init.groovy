node("master") {
    try {
        stage("拉取部署代码库") {
            git branch: "master", credentialsId: '9852bbe8-3935-47a5-b24c-d684c89387d2', url: "http://192.168.55.156:8090/ops/NCD.git"
        }
        
        stage("安装docker-ce") {
            sh "ansible ${HOSTS} -m yum -a \"name=yum-utils,device-mapper-persistent-data,lvm2\""
            sh "ansible ${HOSTS} -a \"yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo\""
            sh "ansible ${HOSTS} -m yum -a \"name=docker-ce\""
        }

        stage("设置镜像仓库和本地库") {
            sh "ansible ${HOSTS} -m file -a \"path=/etc/docker state=directory\""
            sh "ansible ${HOSTS} -m copy -a \"src=./files/daemon.json dest=/etc/docker/daemon.json\""
        }

        stage("加入本地dns解析与加入ca信任") {
            sh "ansible ${HOSTS} -m copy -a \"src=./files/resolv.conf dest=/etc/resolv.conf\""
            sh "ansible ${HOSTS} -m file -a \"path=/etc/docker/certs.d/reg.ops.com state=directory recurse=true\""
            sh "ansible ${HOSTS} -m copy -a \"src=./files/ca.crt dest=/etc/docker/certs.d/reg.ops.com/ca.crt\""
        }

        stage("修改graph") {
            sh "ansible ${HOSTS} -m file -a \"path=/ddhome/local/data/docker state=directory recurse=true\""
            sh "ansible ${HOSTS} -m lineinfile -a \"path=/usr/lib/systemd/system/docker.service regexp='^ExecStart=' line='ExecStart=/usr/bin/dockerd --graph=/ddhome/local/data/docker -H unix://'\""
            sh "ansible ${HOSTS} -a \"systemctl daemon-reload\""
        }

        stage("启动docker") {
            sh "ansible ${HOSTS} -m service -a \"name=docker state=started enabled=yes\""
        }

        stage("登录docker registry") {
            sh "ansible ${HOSTS} -a \"docker login reg.ops.com -u admin -p dd@2019\""
        }
    } catch(err) {
        echo "Caught: ${err}"
    } finally {     
        cleanWs()
    }
}