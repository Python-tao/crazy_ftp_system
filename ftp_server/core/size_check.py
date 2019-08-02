#Author:xyt

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from conf import  settings

#检查目录空间大小的模块。


class Size_Checker(object):

    def __init__(self):
        self.file_size = 0

    def check_size_func(self,path):
        file_list=os.listdir(path)#将path下的所有目录列出（只列出path下的”儿子“目录，不含“孙子等”的目录）
        for file in file_list:
        #遍历文件及目录，如果是目录我再次调用该函数列出该目录下的所有文件和目录，否则计算文件大小的总和
            if os.path.isdir(os.path.join(path,file)):
                self.check_size_func(os.path.join(path,file))
            else:
                self.file_size+=os.stat(os.path.join(path,file)).st_size

        return self.file_size

# path='D:\\100_Work\\110_Work_Ongoing\\python自动化运维\\day7'
# c1=size_checker()
#
# print(c1.check_size_func(path))
#13761











# 原始版本。

# file_size = 0
# def check_size_func(path):
#     global file_size
#     file_list=os.listdir(path)#将path下的所有目录列出（只列出path下的”儿子“目录，不含“孙子等”的目录）
#     for file in file_list:
#     #遍历文件及目录，如果是目录我再次调用该函数列出该目录下的所有文件和目录，否则计算文件大小的总和
#         if os.path.isdir(os.path.join(path,file)):
#             check_size_func(os.path.join(path,file))
#         else:
#             file_size+=os.stat(os.path.join(path,file)).st_size
#     return file_size


# c2=Size_Checker()
# print(c2.check_size_func(path))
# print('##############')
# print(check_size_func(path))
