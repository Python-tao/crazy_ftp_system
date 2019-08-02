#Author:xyt
import os
import sys
import json
import time
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from core import db_handler
from conf import settings
# from core import logger




def login_required(func):
    '''验证用户是否登录的装饰器
    传入参数：
        func,为装饰器标记下的原函数。
        *args，这是原函数的传入参数。此处是user_data用户状态信息。
    执行操作：
        首先使用args[0],获取参数组中的第一个元素，此处就算user_data用户状态信息的字典变量，
        然后使用get('is_authenticated')，判断is_authenticated键中的值是否为True，如果是，
        就运行被装饰函数，并把原参数传入。
        如果is_authenticated键中的值未假，就退出程序。


    '''

    def wrapper(*args,**kwargs):

        if args[0].get('is_authenticated'):
            return func(*args,**kwargs)
        else:
            exit("User is not authenticated.")
    return wrapper



def acc_auth(account,password):
    '''
    判断输入的用户密码是否与数据库中的密码匹配的函数。


    输入参数：
        account: credit account number，用户输入的信用卡的账户
        password: credit card password，用户输入的信用卡的密码
    创建的变量：
        db_api， 把file_execute模块的内存地址赋值给db_api，用意是使用一套统一的‘语法’，覆盖后端各种数据库查询命令的差异。
        db，db_api，也就是file_execute处理完后，正常会返回一个数据库json文件，
        exp_time_stamp,账号的过期期限，此处转换为数值型，然后于当前时间，如果当前时间大于有效期时间，说明已经过期。
    特殊的方法:


    执行操作：
        接收到了用户输入的信用卡的账号密码。
        然后调用db_api,此处传给api是一个语句‘select * from accounts where account=1234’ 以及用户输入的账户。
        db_api仅仅是file_execute函数的别名。
        此处传入的语句，用途有两个：
            使处理函数知道这个是select，查询操作。
            把用户输入的账户id，传给处理函数，比如：用户输入的账号id：1234。
        然后db_api开始处理，主要是操作数据库json文件。
            如果账号存在，就返回账号的数据库json文件，并赋值给data变量。
            如果账号不存在，直接退出整个程序，不用返回。
        接下来，把数据库中的密码data['password']和用户输入的密码比较是否一致，如果一致，
        就判断账号是否已经过期。
            如果过期，就提示用户。
            如果没有，就说明了用户以及通过了认证，并且返回json数据。
    返回值：
        if passed the authentication , retun the account object, otherwise ,return None
        如果密码匹配并且没有过期，就返回data，即用户数据库json文件。
        如果密码错误或者过期，就打印错误提示。

    '''
    # db_api = db_handler.db_handler()
    # db = db_api("select * from accounts where account=%s" % account)
    data = db_handler.file_db_handle("select * from accounts where account=%s" % account)

    #print(db)
    if data:
        if data['password'] == password:

            exp_time_stamp = time.mktime(time.strptime(data['expire_date'], "%Y-%m-%d"))
            if time.time() > exp_time_stamp:
                print("\033[31;1mAccount [%s] has expired,please contact the back to get a new card!\033[0m" % account)
            else:  # passed the authentication
                return data
        else:
            print("\033[31;1mAccount ID or password is incorrect!\033[0m")
    else:
        print("\033[31;1mAccount ID or password is incorrect!\033[0m")

















def acc_login(user_data,**log_obj):
    '''
    account login func
    :user_data: user info db , only saves in memory
    账户登陆函数
    输入参数：
        user_data:为内存中的用户的临时账户状态信息文件，为字典类型。此时为未登陆状态。
        log_obj：日志模块的数据。
    创建参数：
        retry_count，用于统计输入账户，密码次数，也就是登陆次数。
        account，用户的信用卡号码。或者说是json数据库的文件名。
        password，用户账户密码。
        auth，通过了验证的用户的账号数据库json文件的内容。
    具体操作：
        提示用户输入账户id和密码。
        把输入的账户名，密码传给一个acc_auth函数处理认证的过程。acc_auth函数处理完后，如果成功会返回数据库json文件的值。
        auth的值，如果认证通过，auth就是用户的账号数据库json文件。如果没有通过，就为空。
        后续操作：
            如果auth有值，则为ture，于是设置用户状态为已登陆，用户id为该用户输入的id，并返回用户的账号数据库json文件
            如果auth为空，就进行重试。如果重试超过3次，就退出程序，并记录日志。
    返回值：
        如果认证成功，就返回auth,用户的账号数据库json文件.并且会更新user_data的认证状态以及用户账户名。
        否则，没有返回值，直接退出程序。
    '''
    retry_count = 0
    while user_data['is_authenticated'] is not True and retry_count < 3 :
        account = input("\033[32;1maccount:\033[0m").strip()#用户的账户名
        password = input("\033[32;1mpassword:\033[0m").strip()#用户的密码
        auth = acc_auth(account, password)
        if auth: #not None means passed the authentication，不是空，代表通过了认证。
            user_data['is_authenticated'] = True    #状态信息文件的登陆状态。
            user_data['account_id'] = account   #状态信息文件的用户的账户名。
            user_data['user_type'] = auth['user_type']   #状态信息文件的用户的账户名。
            return auth
        retry_count +=1
    else:
        # log_obj.error("account [%s] too many login attempts" % account) #如果重试次数过多就记录日志并退出。
        print("账号：{}，尝试登陆的次数过多！".format(account))
        exit()
