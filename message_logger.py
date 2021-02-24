from db_connect import connect
import datetime

class MessageLogger:
    def __init__(self):
        self.current_log = []
        return

    def add_msg(self, sender, msg):
        self.current_log.append((sender, msg))
        return

    @staticmethod
    def log_sql(msg, reply, language):
        data = {"question": msg,
                "answer": reply,
                "language": language,
                "date": datetime.datetime.now()}
        mydb = connect()
        mycursor = mydb.cursor()
        instruction = "INSERT INTO userBotInteraction (question, answer, language, date) VALUES (\"{question}\", \"{answer}\", \"{language}\", \"{date}\")".format(**data)
        mycursor.execute(instruction)
        mydb.commit()
        mycursor.close()
        return