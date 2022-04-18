#-*- coding: utf-8 -*-
import base64
from authorization import Authorization
from reporter import Reporter
from fire import Fire
from mail import send
from time import sleep
from log import log

def main(username='', password='', file='', b64=False, mail_notify=False, mail_user='', mail_pass='', mail_host='smtp.exmail.qq.com', force=False, location='中国江苏省南京市栖霞区仙林大道'):
	# Load username and password from file
	if file:
		with open(file, 'r') as f:
			username, raw_password = f.read().strip().split(':')
	else:
		# Load username and password from args
		username = username
		raw_password = password

	# Base64 decode
	if b64:
		raw_password = base64.b64decode(raw_password.encode()).decode()
		mail_pass = base64.b64decode(mail_pass.encode()).decode()

	msg_hist = ''

	for _ in range(3):
		try:
			auth = Authorization(username, raw_password)
			status, msg = auth.login()
			msg_hist += log(msg, status=status) + '\n'
			# Login successfully
			if status:
				reporter = Reporter(auth.sess, force=force, location=location)
				status, msg = reporter.report()
				msg_hist += log(msg, status=status) + '\n'

				# Report successfully
				if status:
					break
		except Exception as e:
			msg_hist += log('Operation failed, retrying in 3s. "{}"'.format(e), status=False) + '\n'
			sleep(3)
	else:
		status = False

	if mail_notify:
		status, msg = send(mail_user, mail_pass, mail_host, content=msg_hist, status=status)
		msg_hist += log(msg, status) + '\n'
	return msg_hist

if __name__ == '__main__':
	Fire(main)