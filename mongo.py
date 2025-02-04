from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
class Mongo:
    client = MongoClient(host=os.getenv("MONGO_HOST"," mongodb"), port=int(os.getenv("MONGO_PORT", 27017)))
    db = client['Bumatalk']

    def insertStudent(self, name, text, url):
        col = self.db['student']
        if col.find_one({"name": name, "url" : url}) :
            # 이미 있음
            student_id = col.update_one({"url": url}, {"$set": {"text": text}})
        else : student_id = col.insert_one({"name": name, "text": text, "url": url})
        return student_id

    def getStudent(self, url):
        col = self.db['student']
        student_id = col.find_one({"url": url})
        return student_id

    def getStudentByName(self, name):
        col = self.db['student']
        student_id = col.find_one({"name": name})
        return student_id

    def insertTeacher(self, name, text, url):
        col = self.db['teacher']
        if col.find_one({"name": name, "url": url}):
            # 이미 있음
            teacher_id = col.update_one({"url": url}, {"$set": {"text": text}})
        else:
            teacher_id = col.insert_one({"name": name, "text": text, "url": url})
        return teacher_id

    def getTeacher(self, url):
        col = self.db['teacher']
        teacher_id = col.find_one({"url": url})
        return teacher_id

    def getTeacherByName(self, name):
        col = self.db['teacher']
        teacher_id = col.find_one({"name": name})
        return teacher_id
