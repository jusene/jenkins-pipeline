## 资源请求接口

eg： http://192.168.55.156:5000/deploy?app=iot-config&env=test

## 启动应用

gunicorn -w 4 -b 0.0.0.0:5000 api:app -D

后续会改成swagger文档