# __author__ = "XYT"
# 全局配置文件。
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)



ACCOUNT_BASE = {
    'engine': 'file_storage',  # support mysql,postgresql in the future
    'name': 'accounts',
    'path': "%s/db" % BASE_DIR,         #用户账户文件路径。
    'file_dir':"%s/data" % BASE_DIR,    #上传下载文件的路径。
    'server_host':'localhost',          #服务器端的ip
    'server_port':9999                  #服务器端的端口

}









