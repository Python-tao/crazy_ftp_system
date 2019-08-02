# __author__ = "XYT"
# 全局配置文件。
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


'''
DATABASE:
ACCOUNT_BASE：FTP账户的数据库。


'''
# DATABASE = {
#     'engine': 'file_storage',  # support mysql,postgresql in the future
#     'name': 'product',
#     'db_table':'shopping_list',
#     'path': "%s/db" % BASE_DIR
# }

ACCOUNT_BASE = {
    'engine': 'file_storage',  # support mysql,postgresql in the future
    'name': 'accounts',
    'path': "%s/db" % BASE_DIR,
    'file_dir':"%s/data" % BASE_DIR     #本地下载路径

}






'''账户交易相关的配置文件。
repay:还款
    action:操作类型，plus表示账户金额增加，
    interest:利息，
withdraw:取款
transfer：转账
consume：用户在商场消费的操作时的配置信息。

'''
# TRANSACTION_TYPE = {
#     'repay': {'action': 'plus', 'interest': 0},
#     'withdraw': {'action': 'minus', 'interest': 0.05},
#     'transfer': {'action': 'minus', 'interest': 0.05},
#     'consume': {'action': 'minus', 'interest': 0},
#
# }