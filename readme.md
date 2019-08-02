# 主题：crazt_ftp_system

包括ftp_client和ftp_server两个子项目，分别使用了socket和socketserver模块，
其中服务器端支持多客户端的并发访问功能。
客户端支持显示下载文件的进度条功能。
每个用户都有自己的家目录，可以在家目录下创建目录。但是不能切换到家目录以外的目录。
实现了上传文件和下载文件，具有md5校验功能，具有可用空间额度控制功能。
账户登录认证，ls命令，lls命令，cd切换目录，
mkdir创建目录，pwd显示工作目录等功能。
兼容linux和window环境。


# ftp_client
```
　　客户端程序，创建本地socket，连接ftp服务器端socket，提供客户端交互界面。
```
# ftp_server
```
    服务器端程序，创建服务器socket，监听在本地某个端口，等待客户端的连接。
```
