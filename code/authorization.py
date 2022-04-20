import requests
import re
import js2py
# disable the warnings
import urllib3
from ddddocr import DdddOcr
urllib3.disable_warnings()

class Authorization:
	def __init__(self, username, raw_password):
		self.username = username
		self.raw_password = raw_password
		self.login_url = 'https://authserver.nju.edu.cn/authserver/login'
		self.captcha_url = 'https://authserver.nju.edu.cn/authserver/captcha.html'
		
		self.login_data = {
			'username': username,
			'password': '',
			'lt': '',
			'dllt': 'userNamePasswordLogin',
			'captchaResponse': '',
			'execution': '',
			'_eventId': 'submit',
			'rmShown': 1
		}
		self.sess = requests.session()
		self.sess.headers['User-Agent'] = 'cpdaily/9.0.14  wisedu/9.0.14'

	def prepare_login_data(self):
		login_res = self.sess.get(self.login_url)
		text = login_res.text

		# Resolve data
		try:
			lt = re.search('(?<=name=\"lt\"\svalue=\").*(?=\")', text).group()
			execution = re.search('(?<=name=\"execution\"\svalue=\").*(?=\")', text).group()
			salt = re.search('(?<=pwdDefaultEncryptSalt\s=\s\").*(?=\")', text).group()

			# Encrypt password
			js_url = 'https://authserver.nju.edu.cn/authserver/custom/js/encrypt.js'
			encryptJS = self.sess.get(js_url).text
			context = js2py.EvalJs()
			context.execute(encryptJS)
			password = context.encryptAES(self.raw_password, salt)
		except Exception as e:
			return (False, 'Can\'t parse login data "{}"'.format(e))

		# Resolve captcha
		try:
			captcha_bytes = self.sess.get(self.captcha_url).content
			ocr = DdddOcr(show_ad=False)
			captcha = ocr.classification(captcha_bytes)
		except Exception as e:
			return (False, 'Can\' get captcha "{}"'.format(e))

		# Update data
		self.login_data.update({
			'password': password,
			'lt': lt,
			'execution': execution,
			'captchaResponse': captcha,
		})

		if password and execution and lt and captcha:
			return (True, 'Data prepared successfully')
		else:
			return (False, 'Data preparation failed: password={}, execution={}, lt={}, captcha={}'.format(password, execution, lt, captcha))

	def login(self):
		self.sess.cookies.clear()
		status, msg = self.prepare_login_data()

		# Prepare data successfully
		if status:
			login_res = self.sess.post(self.login_url, data=self.login_data, allow_redirects=False)

			# Get ticket
			if 'location' in login_res.headers and 'index.do' in login_res.headers['location']:
				return (True, 'Login successfully')
			else:
				err = re.search('(?<=(errorMsg" style="display: none;">)).*?(?=</span>)', login_res.text).group()
				return (False, 'Login failed with unknown reason. Error: {}'.format(err))
		else:
			return (False, 'Prepare data failed\n{}'.format(msg))
		