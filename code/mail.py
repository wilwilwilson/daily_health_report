# -*- coding: UTF-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.header import Header
 
def send(username='', password='', host='smtp.exmail.qq.com', content='打卡成功提醒', status=True):
	mail_host = host
	mail_user = username
	mail_pass = password
	
	sender = username
	receivers = [username]
	 
	message = MIMEText(content, 'plain', 'utf-8')
	message['From'] = Header('打卡成功提醒' if status else '打卡失败提醒', 'utf-8')
	message['To'] =  Header(mail_user, 'utf-8')
	 
	subject = '打卡成功提醒邮件' if status else '打卡失败提醒邮件'
	message['Subject'] = Header(subject, 'utf-8')

	try:
	    smtpObj = smtplib.SMTP() 
	    smtpObj.connect(mail_host, 25)
	    smtpObj.login(mail_user,mail_pass)  
	    smtpObj.sendmail(sender, receivers, message.as_string())
	    return (True, 'Mail sent successfully')
	except Exception as e:
	    return (False, 'Mail sending failed "{}"'.format(e))

if __name__ == '__main__':
	send(username='example@mail.com', password='example')