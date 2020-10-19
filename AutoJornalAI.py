import os
import dotenv
import openpyxl
import dateparser
from datetime import datetime, timedelta
from cloudmersive_convert_api_client import ConvertDocumentApi, ApiClient, Configuration
from cloudmersive_convert_api_client.rest import ApiException



dotenv.load_dotenv()
FILENAME = 'asistencia-jornales-cdcc.xlsx'
SHEETNAME = 'Biol'
CLOUDMERSIVE_API_KEY = os.getenv('CLOUDMERSIVE_API_KEY')
CELL_DATA = {

	'WEEK1': 'B12', # format is '<number> al <number> de <month>' or '<number> de <month1> al <number> de <month2>'
	'WEEK2': 'K12', # format is same as 'week1'

	### NOT USED ###
	'NAME': 'B8',
	'STUDENT_NUMBER': 'I8', # format is '#Est: <number>'
	'TOTAL_HOURS1': 'C20', # format is '<number> hrs'
	'TOTAL_HOURS2': 'K20', # format is same as total_horas2_cell
	'MONDAY1_CLOCKIN1': 'B15', # format is 'hh:mm' (12-hour)
	### NOT USED ###

}



class AutoJornalAI:

	def __init__(self, filename, sheetname, cell_data, cloudmersive_api_key):
		self.filename = filename # contains .xlsx extension
		self.workbook = openpyxl.load_workbook(self.filename)
		self.sheet = self.workbook[sheetname]
		self.cell_data = cell_data
		self.cloudmersive_api_key = cloudmersive_api_key
		self.new_filename = None # will not contain extension (for easier development)
		

	def parse_and_add_weeks(self, weekstring, week_amount):
		'''
		Receives a human-readable date range and returns an updated date range

		@param weekstring: string in human-readable date range format (cases explained below)
		@return: string in human-readable date range format
		'''

		count = weekstring.count('de')
		week_split = weekstring.split(' ')


		# Extract fields from `weekstring`
		if count == 1:

			# Case: '<number> al <number> de <month>'
			day1 = week_split[0]
			day2 = week_split[2]
			month = week_split[4]
			start = dateparser.parse(day1 + ' ' + month)
			end = dateparser.parse(day2 + ' ' + month)

		elif count == 2:

			# Case: '<number> de <month1> al <number> de <month2>'
			day1 = week_split[0]
			month1 = week_split[2]
			day2 = week_split[4]
			month2 = week_split[6]
			start = dateparser.parse(day1 + ' ' + month1)
			end = dateparser.parse(day2 + ' ' + month2)

		else:

			raise ValueError('Unsupported week phrase format.')


		# Update dates by `week_amount` weeks
		start += timedelta(days = 7 * week_amount)
		end += timedelta(days = 7 * week_amount)


		# Format into human-readable string
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


	def modify_weeks(self, week_amount=2):
		'''
		Add `week_amount` weeks to the weeks read.

		@param week_amount: int of weeks to add to each week field
		@return: None
		'''

		# Retrieve current week1 and week2 values
		week1 = self.sheet[self.cell_data['WEEK1']].value
		week2 = self.sheet[self.cell_data['WEEK2']].value
		print('\t- First week:', week1)
		print('\t- Second week:', week2)

		# Increment each one by (`week_amount` weeks)
		uweek1 = self.parse_and_add_weeks(week1, week_amount)
		uweek2 = self.parse_and_add_weeks(week2, week_amount)

		# Edit week cells
		self.sheet[self.cell_data['WEEK1']].value = uweek1
		self.sheet[self.cell_data['WEEK2']].value = uweek2
		print('\t- Updated first week:', uweek1)
		print('\t- Updated second week:', uweek2)

		# Update `new_filename` variable
		filename, ext = self.filename.split('.')
		today = datetime.today().strftime('%Y-%m-%d')
		self.new_filename = filename + f'-updated-{today}' # FILENAME-updated-YYY-MM-DD


	def to_xlsx(self):
		'''
		Makes a copy of the modified .xlsx file.

		@return: str, generated file's name
		'''

		if self.new_filename is None:
			raise AttributeError('No workbook has been loaded/modified yet.')
		
		self.workbook.save(self.new_filename + '.xlsx')
		print(f'Saved as {self.new_filename + ".xlsx"}!')
		return self.new_filename + '.xlsx'


	def convert(self, from_ext='xlsx', to_ext='pdf'):
		'''
		Converts a given jornal file from one format to another.

		@param from_ext: str, extension of input format (only 'xlsx' and 'html' are valid for now)
		@param to_ext: str, extension of output format (only 'pdf' and 'html' are valid for now)
		@return: str, generated file's name
		'''

		if self.new_filename is None:
			raise AttributeError('No workbook has been loaded/modified yet.')


		# Setup API Instance
		configuration = Configuration()
		configuration.api_key['Apikey'] = self.cloudmersive_api_key
		# configuration.api_key_prefix['Apikey'] = 'Bearer'
		api_instance = ConvertDocumentApi(ApiClient(configuration))


		# Decide which method to use according to from/to combination
		# NOTE: An option is to use `convert_document_autodetect_to_pdf` or similar
		if from_ext == 'xlsx' and to_ext == 'pdf':
			convert_fn = api_instance.convert_document_xlsx_to_pdf
		elif from_ext == 'xlsx' and to_ext == 'html':
			convert_fn = api_instance.convert_document_xlsx_to_html
		elif from_ext == 'html' and to_ext == 'pdf':
			convert_fn = api_instance.convert_document_html_to_pdf
		else:
			raise ValueError(f'Unsupported configuration of from_ext ({from_ext}) and to_ext ({to_ext}) values.')


		# Generate converted file
		try: 

			# should probably test first with `self.filename`, which is the original source document
			api_response = convert_fn(self.new_filename + '.' + from_ext) # str response wrapped in b''

			if to_ext == 'pdf':
				api_response = api_response[2:-1] # remove b''
				api_response = api_response.encode('utf-8') # convert to bytes

			# print(api_response, type(api_response))

			with open(self.new_filename + '.' + to_ext, 'wb') as f:
				f.write(api_response)

			print(f'Saved as {self.new_filename}.{to_ext}!')
			return self.new_filename + '.' + to_ext

		except ApiException as e:
			print('Error when calling convert function: %s\n' % e)



def main():
	print('Welcome to AutoJornalAI!')
	updater = AutoJornalAI(FILENAME, SHEETNAME, CELL_DATA, CLOUDMERSIVE_API_KEY)
	updater.modify_weeks(week_amount=2)
	xlsx_filename = updater.to_xlsx()
	# pdf_filename1 = updater.convert(from_ext='xlsx', to_ext='pdf')
	html_filename = updater.convert(from_ext='xlsx', to_ext='html')
	pdf_filename2 = updater.convert(from_ext='html', to_ext='pdf')



if __name__ == '__main__':
	pass
