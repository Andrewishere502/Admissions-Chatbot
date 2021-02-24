def connect():
	import mysql.connector
	mydb = mysql.connector.connect(
			host="localhost",
			user="andrew",
			password="wilson!",
			database="admissions_chatbot"
		)
	return mydb


if __name__ == "__main__":
	print(connect())  # nice, it returns an object ;)