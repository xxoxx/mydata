#!/usr/bin/python
# -*- coding: utf-8 -*-

import smtplib
import mimetypes
import time
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

class Sendmail(object):
    def __init__(self,sendto,title,content):
        self.sendtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        self.sendto = sendto
        self.title = title
        self.content = content
        #print "¿ªʼ·¢̍Ԋ¼þ"
    def send(self):
        msg = MIMEMultipart()
        #txt = MIMEText(self.sendtime+'\n'+self.content,_subtype='html',_charset='utf-8')
        txt = MIMEText(self.content,_subtype='html',_charset='utf-8')
        msg.attach(txt)
        #¼ԓʼþͷ
        receiver = [self.sendto]
        msg['to'] = self.sendto
        msg['from'] = 'XXXX@163.com'
        msg['subject'] = self.title
        #·¢̍Ԋ¼þ
        try:
            server = smtplib.SMTP()
            server.connect('smtp.163.com')
            server.login('XXXXX@163.com','XXXXXXXXXXXXX')
            server.sendmail(msg['from'], receiver,msg.as_string())
            server.quit()
            print '¿¿¿¿'
        except Exception, e:
            print str(e)
if __name__ == "__main__":
    Sendmail(sys.argv[1],sys.argv[2],sys.argv[3]).send()
