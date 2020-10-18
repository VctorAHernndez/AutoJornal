import os
from datetime import datetime, timedelta
from PIL import Image, ImageFont, ImageDraw
from AutoJornalDB import AutoJornalDB
from AutoJornalSMTP import AutoJornalSMTP



SUBJECT = 'Jornal a firmar'
BODY = '''Saludos Profesor,

Rosita nos pidió que verifiques las horas y firmes antes de enviárselas a ella.

¡Gracias!

Nota: este email fué generado automáticamente por nuestro nuevo sistema AutoJornal.
Cualquier problema favor de avisarnos: <a href="mailto:hector.carrion@upr.edu">hector.carrion@upr.edu</a>
<a href="mailto:victor.hernandez17@upr.edu">victor.hernandez17@upr.edu</a>
'''



class AutoJornal:

	def __init__(self):
		self.db_name = 'AutoJornal.db'

		self.font_path = 'fonts/SFNS.ttf'
		self.pdfs_path = 'pdfs/'
		self.skeletons_path = 'skeletons/'

		self.font_size = 40
		self.coordinates_week1 = (800, 930)
		self.coordinates_week2 = (2250, 930)
		self.color = (0, 0, 0)

		self.professor_email = 'carlos.corrada2@upr.edu'
		self.secretary_email = 'rosa.santiago5@upr.edu'
		self.subject = SUBJECT
		self.body = BODY


	def DateToString(self, start, end):
		
		if start.month == end.month:
			uday1 = start.day
			uday2 = end.day
			month = start.strftime('%B').lower()
			return f'{uday1} - {uday2} {month}'
		else:
			uday1 = start.day
			uday2 = end.day
			umonth1 = start.strftime('%b').lower()
			umonth2 = end.strftime('%b').lower()
			return f'{uday1} {umonth1} - {uday2} {umonth2}'


	def GeneratePDF(self, skeleton_filename, week1, week2):

		img = Image.open(os.path.join(self.skeletons_path, skeleton_filename))
		draw = ImageDraw.Draw(img)
		font = ImageFont.truetype(self.font_path, self.font_size)

		draw.text(self.coordinates_week1, week1, self.color, font=font)
		draw.text(self.coordinates_week2, week2, self.color, font=font)

		fn, ext = skeleton_filename.split('.')

		pdf_filename = fn + '_' + datetime.now().isoformat() + '.pdf'
		img.save(os.path.join(self.pdfs_path, pdf_filename))

		return pdf_filename


	def AddReport(self, week_amount=2):

		database = AutoJornalDB(self.db_name)
		database.Connect()
		users = database.FetchUsers()

		# For each user...
		for user in users:

			# Extract last report's date
			id_report, sd1, ed1, sd2, ed2, _ = database.FetchLastReport(user['id'])

			# Add `week_amount` weeks
			sd1 += timedelta(days = 7 * week_amount)
			ed1 += timedelta(days = 7 * week_amount)
			sd2 += timedelta(days = 7 * week_amount)
			ed2 += timedelta(days = 7 * week_amount)

			# Format dates into human-readable format
			week1_text = self.DateToString(sd1, ed1)
			week2_text = self.DateToString(sd2, ed2)
			
			# Generate updated PDF
			pdf_filename = self.GeneratePDF(user['skeleton_filename'], week1_text, week2_text)

			# Send email and insert new report in database on success (on error, delete generated PDF)
			try:
				email_sender = AutoJornalSMTP()

				content = [
					self.body,
					os.path.join(self.pdfs_path, pdf_filename)
				]

				# TODO: CHANGE 'TO_EMAIL' SELF.PROFESSOR_EMAIL
				email_sender.send(user['email'], self.subject, content)
				database.CreateReport(sd1, ed1, sd2, ed2, user['id'])
				print('Email sent to:', user['email'])
			except:
				os.remove(os.path.join(self.pdfs_path, pdf_filename))
				database.Close()
				raise Exception('Email could not be sent.')
				

		database.Close()



def main():
	pdf_generator = AutoJornal()
	pdf_generator.AddReport()



if __name__ == '__main__':
	pass
