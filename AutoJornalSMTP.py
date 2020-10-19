import os
import dotenv
import yagmail



dotenv.load_dotenv()
FROM_EMAIL = os.getenv('FROM_EMAIL')
APP_PASSWORD = os.getenv('APP_PASSWORD')



class AutoJornalSMTP:

	def __init__(self, from_email=FROM_EMAIL, app_password=APP_PASSWORD):
		self.from_email = from_email
		self.app_password = app_password


	def send(self, to_email, subject, content):
		try:
			email = yagmail.SMTP(self.from_email, self.app_password)
			email.send(to_email, subject, content)
		except:
			raise Exception(f'Could not send email to {to_email}!')



def main():

	to_email = 'vhernandezcastro@gmail.com'
	subject = 'こんにちは from Víctor'
	content = ['Kendrick me está mirando', 'test.txt']

	email_sender = AutoJornalSMTP()
	email_sender.send(to_email, subject, content)
	


if __name__ == '__main__':
	pass
