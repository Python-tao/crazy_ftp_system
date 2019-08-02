
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from conf import settings

import json




account_dic = {
    'id': 'Tom',
    'password': 'abc',
    'enroll_date': '2016-01-02',
    'expire_date': '2021-01-01',
    'home_dir':'Tom',
    'storage_quota':200,
    'status': 0 # 0 = normal, 1 = locked, 2 = disabled
}

# old_order_list=[
# ['2019-06-18','Iphone',5800],
# ['2019-06-19','Bike',800],
# ]






# json_file_addr="{}\{}\{}.json".format(settings.DATABASE['path'],settings.DATABASE['name'],settings.DATABASE['db_table'])
account_file_addr="{}\{}\{}.json".format(settings.ACCOUNT_BASE['path'],settings.ACCOUNT_BASE['name'],account_dic['id'])
# order_file_addr="{}\{}\{}.json".format(settings.OLD_ORDER_BASE['path'],settings.OLD_ORDER_BASE['name'],'Jerry')


print(account_file_addr)


def make_account():
    '''
    初始化用户数据库，
    返回：在accounts目录下的json文件。
    '''
    with open(account_file_addr, 'w') as f:
        a=json.dump( account_dic,f)


def read_account():
    '''
    读取用户账户信息。
    返回json文件的内容。
    :return:
    '''
    with open(account_file_addr, 'r') as f:
        print(json.load(f))

# def check_accounts_exist():
#     print(os.path.isfile(json_file_addr))
#     return

make_account()
read_account()
