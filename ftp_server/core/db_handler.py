import json,time ,os,sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)


from conf import settings

def file_execute(sql,db_path,**kwargs):
    '''
    文件操作模块。
    处理所有的数据库查询，更新等操作。

    '''
    sql_list = sql.split("from")   #把查询语句拆分成列表。
    if sql_list[0].startswith("select") and len(sql_list)> 1:#如果列表元素大于1，说明有提供数据库名。
            if os.path.isfile(db_path):
                with open(db_path, 'r') as f:
                    db_file_data = json.load(f)
                    return db_file_data
            else:
                return None
                #exit("\033[31;1mAccount [%s] does not exist!\033[0m" % val )

    elif sql_list[0].startswith("update") and len(sql_list)> 1:
            if os.path.isfile(db_path):
                account_data = kwargs.get("account_data")#待更新的用户数据文件。

                with open(db_path, 'w') as f:
                    json.dump(account_data, f)
                return True


def file_db_handle(sql,**kwargs):
    '''
    parse the db file path
    文件数据库的处理函数。
    :param conn_params: the db connection params set in settings，全局配置文件中的数据库信息参数。
    :return:返回一个文件操作的函数的内存地址。
    '''
    #print('file db:',conn_params)   #打印系统数据库参数。
    #db_path ='%s/%s' %(conn_params['path'],conn_params['name'])

    if "ATM" in sql:
        account_name = sql.split("where")[1].strip().split("=")[1].split(" ")[0]
        conn_params = settings.ATM_DATABASE  # 再次获取数据库参数信息。
        db_path = '{}/{}/{}.json'.format(conn_params['path'], conn_params['name'], account_name)
        return file_execute(sql, db_path,**kwargs)

    else:
        db_type = sql.split("from")[1].split(" ")[1]  # 获取查询的数据库信息

        if db_type == "accounts":
            account_name = sql.split("where")[1].strip().split("=")[1]
            conn_params = settings.ACCOUNT_BASE  # 再次获取数据库参数信息。
            db_path = '{}/{}/{}.json'.format(conn_params['path'], conn_params['name'], account_name)
            return file_execute(sql, db_path)

        elif db_type == "product":
            conn_params = settings.DATABASE  # 再次获取数据库参数信息。
            db_path = '{}/{}/{}.json'.format(conn_params['path'], conn_params['name'], conn_params['db_table'])
            print(db_path)
            return file_execute(sql, db_path)
        else:
            print("数据库查询语句有误。")


