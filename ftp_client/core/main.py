import os
import sys,threading
BASE_DIR = os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )
sys.path.append(BASE_DIR)


from core import ftp_client


def run():
    event = threading.Event()
    ftp = ftp_client.FtpClient(event)

    ftp.connect("localhost",9999)
    # ftp.connect("192.168.88.128",9999)
    f1 = threading.Thread(target=ftp.interactive, )
    f1.start()
    ftp.downprogress()

