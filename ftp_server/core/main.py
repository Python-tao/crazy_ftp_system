import socketserver
import json,os,time,hashlib
import os
import sys
BASE_DIR = os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )
sys.path.append(BASE_DIR)

from core import db_handler,size_check
from conf import settings



class MyTCPHandler(socketserver.BaseRequestHandler):




    def auth(self,*args):
        '''验证用户身份和密码'''
        cmd_dic=args[0]
        remote_name=cmd_dic['username']
        remote_pass=cmd_dic['password']
        response_data = {}
        self.account_data = db_handler.file_db_handle("select * from accounts where account=%s" % remote_name)
        if self.account_data:
            if self.account_data['password'] == remote_pass:
                exp_time_stamp = time.mktime(time.strptime(self.account_data['expire_date'], "%Y-%m-%d"))
                if time.time() > exp_time_stamp:
                    print(
                        "\033[31;1m账户 [%s] 已经过期，请联系管理员更新有效期!\033[0m" % self.account_data['id'])
                else:#通过了认证，返回用户的账户信息数据。
                    response_data={'res_type':0,'res_data':self.account_data}
                    self.homedir = self.rootdir + '/' +self.account_data['home_dir']
            else:
                response_data = {'res_type':1,'res_data':"密码不正确！"}
                print("\033[31;1m密码不正确！\033[0m")
        else:
            response_data = {'res_type': 2, 'res_data': "用户ID不存在！"}
            print("\033[31;1m用户ID不存在！\033[0m")
        self.request.send(json.dumps(response_data).encode("utf-8"))
        print("send",json.dumps(response_data).encode("utf-8") )




    def put(self,*args):
        '''接收客户端文件'''
        cmd_dic = args[0]
        filename = cmd_dic["filename"]
        filesize = cmd_dic["size"]
        abs_filename=self.rootdir+'/'+cmd_dic["current_dir"]+'/'+filename
        checker=size_check.Size_Checker()
        current_dir_size=checker.check_size_func(self.homedir)
        checker.file_size=0
        if current_dir_size+filesize < self.account_data['storage_quota']:
            print("当前用户目录的空间:{},上传的文件的大小:{}.".format(current_dir_size,filesize))
            if os.path.isfile(abs_filename):
                f = open(abs_filename +'.'+str(time.time()).split('.')[0][-4:],"wb")
            else:
                f = open(abs_filename , "wb")

            response_data = {'res_type': 0, 'res_data': '200 ok。'}
            self.request.send(json.dumps(response_data).encode('utf-8'))#提示客户端，准备好了，可以发送。
            m = hashlib.md5()
            received_size = 0
            while received_size < filesize:
                if filesize-received_size > 1024:
                    size=1024
                else:
                    size=filesize-received_size
                    # print("last receive:", size)
                data = self.request.recv(size)
                received_size += len(data)
                m.update(data)
                f.write(data)
            else:
                new_file_md5 = m.hexdigest()
                print("file [%s] has received..." % filename)
                f.close()
                server_file_md5 = self.request.recv(1024)
                print("server file md5:", server_file_md5.decode())
                print("client file md5:", new_file_md5)
                if server_file_md5.decode() == new_file_md5:
                    response_data = {'res_type': 0, 'res_data': 'MD5校验码一致。'}
                    self.request.send(json.dumps(response_data).encode('utf-8'))#告诉客户端，校验码一致。
                    print("MD5校验码一致。")
                else:
                    response_data = {'res_type': 1, 'res_data': 'MD5校验码不一致。'}
                    self.request.send(json.dumps(response_data).encode('utf-8'))
                    print("MD5校验码不一致。")
        else:
            response_data = {'res_type': 1, 'res_data': '可用空间不足，当前目录空间：{}，可用额度：{}。'.format(current_dir_size,self.account_data['storage_quota']-current_dir_size)}
            self.request.send(json.dumps(response_data).encode('utf-8'))



    def get(self, *args):
        '''发送文件给客户端。'''
        cmd_dic = args[0]
        filename=cmd_dic["filename"]
        absfilepath=self.rootdir+'/'+cmd_dic["current_dir"]+'/'+filename
        print(absfilepath)
        if os.path.isfile(absfilepath):
            f = open(absfilepath, "rb")

            file_size = os.stat(absfilepath).st_size
            response_data = {'res_type': 0,'res_data':file_size}
            self.request.send(json.dumps(response_data).encode("utf-8"))
            self.request.recv(1024) #等待客户端回复说准备好了。
            m = hashlib.md5()
            for line in f:
                m.update(line)
                self.request.send(line)
            print("file md5", m.hexdigest())
            self.request.send(m.hexdigest().encode())#发送server端的md5值
            f.close()
            print("send done.")
        else:
            response_data = {'res_type': 1, 'res_data': '文件不存在！'}
            self.request.send(json.dumps(response_data).encode("utf-8"))
            print("无此文件，不发.")







    def ls(self,*args):
        #查看目录下文件。
        cmd_dic = args[0]
        action=cmd_dic['action']
        absdirname=self.rootdir+'/'+cmd_dic['dirname']
        if os.name=='nt':
            cmd_res=" ".join(os.listdir(absdirname))
        else:
            cmd_res = os.popen(action+' '+absdirname).read()
        print("before send size:",len(cmd_res.encode()))
        if len(cmd_res.encode()) ==0:
            cmd_res = "cmd has no output..."
        self.request.send( str(len(cmd_res.encode())).encode("utf-8"))     #先发大小给客户端
        self.request.send(cmd_res.encode("utf-8"))
        print("send done")

    def cd(self,*args):
        #切换目录
        cmd_dic = args[0]
        action = cmd_dic['action']
        absdirname = self.rootdir + '/' + cmd_dic['dirname']
        if os.path.isdir(absdirname):
            response_data={'res_type':0}
        else:
            response_data={'res_type':1}

        self.request.send(json.dumps(response_data).encode("utf-8"))
        print("send done")

    def mkdir(self,*args):
        #创建目录。
        cmd_dic = args[0]
        action = cmd_dic['action']
        absdirname = self.rootdir + '/' + cmd_dic['dirname']
        if os.path.isdir(absdirname):
            response_data={'res_type':1,'res_data':'目录已存在。'}
        else:
            if os.mkdir(absdirname)==None:
                print("创建成功")
                response_data = {'res_type': 0, 'res_data': cmd_dic['dirname']}
            else:
                print('创建失败')
                response_data = {'res_type': 2,'res_data':'目录创建失败。'}
        print(response_data)
        self.request.send(json.dumps(response_data).encode("utf-8"))
        print("send done")

    def handle(self):
        #主交互函数。
        self.rootdir = settings.ACCOUNT_BASE['file_dir']

        while True:
            try:
                self.data = self.request.recv(1024).strip()
                print("IP:{},PORT:{} wrote:".format(self.client_address[0],self.client_address[1]))
                print(self.data)
                if not self.data:
                    print("客户端{}已断开".format(self.client_address[1]))
                    break
                cmd_dic = json.loads(self.data.decode())
                action = cmd_dic["action"]
                if hasattr(self,action):
                    func = getattr(self,action)
                    func(cmd_dic)

            except ConnectionResetError as e:
                print("err",e)
                break
def run():
    HOST, PORT = settings.ACCOUNT_BASE['server_host'], settings.ACCOUNT_BASE['server_port']
    # Create the server, binding to localhost on port 9999
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    print("Crazy FTP is running...")
    server.serve_forever()
    def func():
        print("ddd")


