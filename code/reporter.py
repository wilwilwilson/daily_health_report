import json
from datetime import datetime

class Reporter:
	def __init__(self, sess, force=False, location='中国江苏省南京市栖霞区仙林大道'):
		self.get_list_url = 'http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/getApplyInfoList.do'
		self.report_url = 'https://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do'
		self.sess = sess
		self.location = location
		self.force = force

		check_login_status_url = 'https://authserver.nju.edu.cn/authserver/index.do'

		if '安全退出' not in sess.get(check_login_status_url).text:
			raise ValueError('Invalid session "sess"')

	def get_list(self):
		try:
			get_list_res = self.sess.get(self.get_list_url)
			self.report_list = json.loads(get_list_res.text)['data']
			return (True, 'Get report list successfully')
		except Exception as e:
			return(False, 'Get report list failed "{}"'.format(e))

	def report(self):
		# No report list
		if not(self.__dict__.get('report_list', None)):
			self.get_list()

		# Report has already finished
		if self.report_list[0]['TBZT'] == '1' and not(self.force):
			return (False, 'Report has already finished')

		# Get rna time
		zjhs_str = '{} 11'.format(datetime.today().strftime('%Y-%m-%d'))
		WID = self.report_list[0]['WID']

		params = {
			'WID': WID,
			'CURR_LOCATION': self.location,
			'IS_TWZC': '1',
			'IS_HAS_JKQK': '1',
			'JRSKMYS': '1',
			'JZRJRSKMYS': '1',
			'SFZJLN': '0',
			'ZJHSJCSJ': zjhs_str
		}
		report_res = self.sess.get(self.report_url, params=params, verify=False, allow_redirects=False)
		try:
			# Check wheter report successfully
			res = json.loads(report_res.text)
			self.get_list()
			if self.report_list[0]['TBZT'] == '1':
				return (True, 'Report successfully')
		except Exception as e:
			return (False, 'Report failed: "{}"'.format(e))