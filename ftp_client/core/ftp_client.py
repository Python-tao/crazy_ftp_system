_author__ = "Alex Li"
import socket
import json,hashlib,time
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from conf import  settings



user_data = {
    'account_id':None,
    'is_authenticated':False,
    'current_dir':None,     #当前的工作路径。
    'account_data':None
}


# 显示进度条
def view_bar(num, total):
    rate = num / total
    rate_num = int(rate * 100)
    number = int(50 * rate)
    r = '\r[%s%s]%d%%' % ("#" * number, " " * (50 - number), rate_num,)
    # print("\r {}".format(r), end=" ")  # \r回到行的开头
    print(" {}".format(r), end=" ")  # \r回到行的开头







class FtpClient(object):
    def __init__(self,event):
        self.client = socket.socket()
        self.event=event
    def help(self):
        #命令帮助菜单
        msg = '''
        ls
        lls
        pwd
        cd ../..
        get filename
        put filename
        mkdir dirname
        bye
        '''
        print(msg)
    def connect(self,ip,port):
        self.client.connect((ip, port))

    def authenticate(self):
        #验证用户密码。
        self.account = input("\033[32;1maccount:\033[0m").strip()  # 用户的账户名
        password = input("\033[32;1mpassword:\033[0m").strip()  # 用户的密码
        msg_dic={
            'action':'auth',
            'username':self.account,
            'password':password
        }
        self.client.send(json.dumps(msg_dic).encode("utf-8"))
        print("send", json.dumps(msg_dic).encode("utf-8"))
        server_response = self.client.recv(1024)
        res_dic = json.loads(server_response.decode())
        return res_dic




    def interactive(self):
        #与用户进行交互的程序。
        retry_count = 0
        while user_data['is_authenticated'] is not True and retry_count < 3:
            auth=self.authenticate()
            if auth['res_type']==0:
                user_data['is_authenticated'] = True
                user_data['account_id'] = auth['res_data']['id']
                user_data['account_data'] = auth['res_data']
                user_data['current_dir'] = auth['res_data']['home_dir']
                break
            elif auth['res_type']==1:
                print(auth['res_data'])
            elif auth['res_type'] == 2:
                print(auth['res_data'])
            retry_count+=1
        else:
            print("账号：{}，尝试登陆的次数过多！".format(self.account))
            exit()

        print("{}用户，你好，欢迎进入Crazy FTP service，请输入你的命令。。".format(user_data['account_id']))

        while user_data['is_authenticated'] is True:

            cmd = input("[{}/]>>".format(user_data['current_dir'])).strip()
            if len(cmd) ==0:continue
            cmd_str = cmd.split()[0]
            if hasattr(self,"cmd_%s" % cmd_str):
                func = getattr(self,"cmd_%s" % cmd_str)
                func(cmd)
            else:
                self.help()

    def cmd_ls(self,*args):
        #查看服务器文件目录下的文件列表。
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            dirname = user_data['current_dir']+'/'+cmd_split[1]
        else:
            dirname = user_data['current_dir']
        msg_dic={
            "action": "ls",
            "dirname":dirname
        }
        self.client.send(json.dumps(msg_dic).encode("utf-8"))
        print("send", json.dumps(msg_dic).encode("utf-8"))
        cmd_res_size = self.client.recv(1024)  ##接受命令结果的长度
        # print("命令结果大小:", cmd_res_size)
        received_size = 0
        received_data = b''
        while received_size < int(cmd_res_size.decode()):
            data = self.client.recv(1024)
            received_size += len(data)
            received_data += data
        else:
            print("当前FTP目录:{}，其内容为：".format(dirname))
            print(received_data.decode())
    def cmd_lls(self,*args):
        '''查看本地下载目录的内容。'''
        local_file_dir = settings.ACCOUNT_BASE['file_dir']

        if os.name == 'nt':
            cmd_res = " ".join(os.listdir(local_file_dir))
        else:
            cmd_res = os.popen('ls'+' '+local_file_dir+'-l').read()
        print('本地目录:{},的内容为：'.format(local_file_dir))
        print(cmd_res)


    def cmd_cd(self,*args):
        #切换目录
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            if cmd_split[1]=='..':
                list_dir_name=user_data['current_dir'].split('/')
                if len(list_dir_name)>1:
                    list_dir_name.pop()
                    if len(list_dir_name)==1:
                        dirname =list_dir_name[0]
                    else:
                        dirname="/".join(list_dir_name)
                else:
                    print('这个没有父目录。')
                    dirname = user_data['current_dir']
            elif cmd_split[1].isalnum():
                dirname = user_data['current_dir'] + '/' + cmd_split[1]
            else:
                dirname = user_data['current_dir']

        else:
            dirname = user_data['current_dir']

        msg_dic = {
            "action": "cd",
            "dirname": dirname
        }
        self.client.send(json.dumps(msg_dic).encode("utf-8"))
        print("send", json.dumps(msg_dic).encode("utf-8"))
        cmd_res = self.client.recv(1024)
        cmd_dic=json.loads(cmd_res.decode())
        if cmd_dic['res_type']==0:
            user_data['current_dir']=dirname
            print("当前目录为:{}".format(dirname))
        else:
            print("目录不存在:{}".format(dirname))
    def cmd_pwd(self,*args):
        #打印当工作目录路径
        cmd_split = args[0].split()
        if cmd_split[0]=='pwd':
            print('当前目录为：/{}/'.format(user_data['current_dir']))


    def cmd_mkdir(self,*args):
        #创建目录。
        cmd_split = args[0].split()

        if len(cmd_split) > 1:

            if cmd_split[1].isalnum():
                dirname = user_data['current_dir']+'/'+cmd_split[1]
                msg_dic = {
                    "action": "mkdir",
                    "dirname": dirname
                }
                self.client.send(json.dumps(msg_dic).encode("utf-8"))
                print("send", json.dumps(msg_dic).encode("utf-8"))
                cmd_res = self.client.recv(1024)
                res_dic=json.loads(cmd_res.decode())
                if res_dic['res_type'] == 0:
                    print("目录创建成功:{}".format(res_dic['res_data']))
                else:
                    print("创建失败:{}".format(res_dic['res_data']))
            else:
                print("输入的目录名称有误，不支持特殊字符。")
        else:
            print("不能创建一个空目录。")
            pass


    def cmd_bye(self,*args):
        #退出程序。
        self.client.shutdown(1)
        exit("Goodbye!")




    def cmd_put(self,*args):
        #上传文件。
        cmd_split =  args[0].split()
        if len(cmd_split) >1:
            filename = cmd_split[1]
            abs_filename=settings.ACCOUNT_BASE['file_dir']+'/'+filename
            current_dir=user_data['current_dir']

            if os.path.isfile(abs_filename):
                filesize = os.stat(abs_filename).st_size
                msg_dic = {
                    "action": "put",
                    "filename":filename,
                    "size": filesize,
                    "overridden":True,
                    "current_dir":current_dir
                }
                self.client.send( json.dumps(msg_dic).encode("utf-8")  )
                print("send file size",filesize )
                #防止粘包，等服务器确认
                server_response = self.client.recv(1024)
                res_dic=json.loads(server_response.decode())
                if res_dic['res_type']==0:
                    f = open(abs_filename,"rb")
                    m = hashlib.md5()
                    for line in f:
                        m.update(line)
                        self.client.send(line)


                    else:

                        print("file md5", m.hexdigest())
                        self.client.send(m.hexdigest().encode())  # send md5
                        f.close()
                        print("文件上传成功...")
                        server_response = self.client.recv(1024)
                        res_dic = json.loads(server_response.decode())
                        if res_dic['res_type'] == 0:
                            print(res_dic['res_data'])
                        else:
                            print(res_dic['res_data'])
                else:
                    print(res_dic['res_data'])

            else:
                print(filename,"is not exist")
    def cmd_get(self,*args):
        #下载文件。
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            filename = cmd_split[1]
            abs_file_dir=settings.ACCOUNT_BASE['file_dir']
            self.abs_filename = settings.ACCOUNT_BASE['file_dir'] + '/' + filename
            if os.path.isfile(self.abs_filename):
               print("文件:{}，在本地目录已经存在。".format(self.abs_filename))

            else:
                msg_dic = {
                    "action": "get",
                    "filename": filename,
                    "size": None,
                    "current_dir": user_data['current_dir']
                }
                self.client.send(json.dumps(msg_dic).encode("utf-8"))

                # 等服务器发送文件大小过来。


                server_response = self.client.recv(1024)
                res_dic = json.loads(server_response.decode())
                if res_dic['res_type']==0:
                    self.file_total_size=res_dic['res_data']
                    print("返回文件的大小:{}".format(self.file_total_size) )
                    self.client.send("准备好了，发吧。".encode("utf-8"))
                    received_size = 0
                    received_data = b''
                    f = open(self.abs_filename, "wb")
                    self.event.set()
                    m = hashlib.md5()
                    start_time = time.time()
                    while received_size < self.file_total_size:
                        if self.file_total_size - received_size > 1024:
                            size = 1024
                        else:
                            size = self.file_total_size - received_size
                        data = self.client.recv(size)
                        received_size += len(data)
                        m.update(data)
                        f.write(data)
                    else:
                        self.event.clear()
                        new_file_md5 = m.hexdigest()
                        print("file recv done")
                        print("耗时:{}s".format(time.time() - start_time))
                        f.close()
                        server_file_md5 = self.client.recv(1024)
                        print("server file md5:", server_file_md5.decode())
                        print("client file md5:", new_file_md5)
                        if server_file_md5.decode() == new_file_md5:
                            print("MD5校验码一致。")
                        else:
                            print("MD5校验码不一致。")
                else:
                    print(res_dic['res_data'])


    def downprogress(self, *args):
        #下载进度条。
        while True:
            if self.event.is_set():
                print("文件创建了，开始准备进度条。")
                self.filename = self.abs_filename
                self.file_size = 0
                self.file_total = self.file_total_size
                while self.file_size < self.file_total:  # 获取当前下载进度
                    time.sleep(1)
                    if os.path.exists(self.filename):
                        self.down_rate = (os.path.getsize(self.filename) - self.file_size) / 1024 / 1024
                        self.down_time = (self.file_total - self.file_size) / 1024 / 1024 / self.down_rate
                        # print("  " + str('%.2f' % self.down_rate + "MB/s"), end="")
                        self.file_size = os.path.getsize(self.filename)
                    # print("\r " + str(int(self.down_time)) + "s"," " + str('%.2f' % (self.file_size / 1024 / 1024)) + "MB", end="")
                    # print(" " + str('%.2f' % (self.file_size / 1024 / 1024)) + "MB", end="")
                    view_bar(self.file_size, self.file_total)
            else:
                self.event.wait()










