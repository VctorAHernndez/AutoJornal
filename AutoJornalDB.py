import sqlite3
from datetime import date



class AutoJornalDB:

	def __init__(self, db_name):

		self.db_name = db_name
		self.c = None
		self.conn = None


	def Connect(self):
		'''Connect to the database file'''
		try:
			self.conn = sqlite3.connect(self.db_name,
				detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
			self.c = self.conn.cursor()
			return 1
		except:
			raise Exception('Could not connect to database!')


	def Close(self):
		'''Close cursor to the database'''
		try:
			self.conn.commit()
			self.c.close()
			self.conn.close()
			return 1
		except:
			raise Exception('Could not close database!')

	
	def CreateDB(self):
		'''Creates DB if it doesn't exist already'''

		try:
			self.c.execute('''
				CREATE TABLE IF NOT EXISTS user (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					name TEXT NOT NULL,
					email TEXT NOT NULL,
					app_password TEXT,
					skeleton_filename TEXT NOT NULL
				);
			''')

			self.c.execute('''
				CREATE TABLE IF NOT EXISTS report (
					id INTEGER PRIMARY KEY,
					start_date1 DATE NOT NULL,
					end_date1 DATE NOT NULL,
					start_date2 DATE NOT NULL,
					end_date2 DATE NOT NULL,
					id_user INTEGER NOT NULL,
					FOREIGN KEY(id_user) REFERENCES user(id)
				);
			''')
		except:
			raise Exception('Could not create database!')


	def CreateUser(self, name, email, app_password, skeleton_filename):
		'''Insert new user to database'''

		query = '''INSERT INTO user
				   (name, email, app_password, skeleton_filename) 
				   VALUES
				   ("%s", "%s", "%s", "%s")
		''' % (name, email, app_password, skeleton_filename)

		try:
			self.c.execute(query)
			return self.c.lastrowid
		except:
			raise Exception('Could not create user!')


	def CreateReport(self, start_date1, end_date1, start_date2, end_date2, id_user):
		'''Adds the new report to DB'''

		query = '''INSERT INTO report
				   (start_date1, end_date1, start_date2, end_date2, id_user)
				   VALUES
				   ("%s", "%s", "%s", "%s", "%s")
		''' % (start_date1, end_date1, start_date2, end_date2, id_user)

		try:
			self.c.execute(query)
			return self.c.lastrowid
		except:
			raise Exception('Could not create report!')


	def FetchLastReport(self, id_user):
		'''Returns last report of a given user'''

		query = '''SELECT * FROM report
				   WHERE id_user = %s
				   ORDER BY id DESC
		''' % (id_user)

		try:
			self.c.execute(query)
			report = self.c.fetchone()
			return report
		except:
			raise Exception('Could not fetch last report!')


	def FetchUsers(self):
		'''Returns all users'''

		query = 'SELECT * FROM user WHERE 1'

		try:
			self.c.execute(query)
			users = self.c.fetchall()

			dicts = []
			for user in users:
				dicts.append({
					'id': user[0],
					'name': user[1],
					'email': user[2],
					'app_password': user[3],
					'skeleton_filename': user[4],
				})

			return dicts
		except:
			raise Exception('Could not fetch users!')


	def FetchReports(self, id_user):
		'''Returns all reports of a given user'''

		query = '''SELECT * FROM report
				   WHERE id_user = %s
				   ORDER BY id DESC
		''' % (id_user)

		try:
			self.c.execute(query)
			reports = self.c.fetchall()
			return reports
		except:
			raise Exception('Could not fetch reports!')



def main():
	'''This should only be run once in a lifetime'''

	# Create database
	database = AutoJornalDB('AutoJornal.db')
	database.Connect()
	database.CreateDB()

	# Insert dummy data
	database.CreateUser('Héctor Carrión', 'hector.carrion@upr.edu', '', 'hector.jpg')
	database.CreateUser('Víctor A. Hernández', 'victor.hernandez17@upr.edu', '', 'victor.jpg')
	database.CreateReport(date(2020, 9, 14), date(2020, 9, 18), date(2020, 9, 21), date(2020, 9, 25), 1)
	database.CreateReport(date(2020, 9, 14), date(2020, 9, 18), date(2020, 9, 21), date(2020, 9, 25), 2)
	database.Close()



if __name__ == '__main__':
	pass
