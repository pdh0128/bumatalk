from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
class Mongo:
    client = MongoClient(host=os.getenv("MONGO_HOST"," mongodb"), port=int(os.getenv("MONGO_PORT", 27017)))
    db = client['Bumatalk']

    async def insertStudent(self, name, text, url):
        col = self.db['student']
        if col.find_one({"name": name, "url" : url}) :
            # 이미 있음
            student_id = col.update_one({"url": url}, {"$set": {"text": text}})
        else : student_id = col.insert_one({"name": name, "text": text, "url": url})
        return student_id

    async def getStudent(self, url):
        col = self.db['student']
        student_id = col.find_one({"url": url})
        return student_id

    async def getStudentByName(self, name):
        col = self.db['student']
        student_id = col.find_one({"name": name})
        return student_id

    async def insertTeacher(self, name, text, url):
        col = self.db['teacher']
        if col.find_one({"name": name, "url": url}):
            # 이미 있음
            teacher_id = col.update_one({"url": url}, {"$set": {"text": text}})
        else:
            teacher_id = col.insert_one({"name": name, "text": text, "url": url})
        return teacher_id

    async def getTeacher(self, url):
        col = self.db['teacher']
        teacher_id = col.find_one({"url": url})
        return teacher_id

    async def getTeacherByName(self, name):
        col = self.db['teacher']
        teacher_id = col.find_one({"name": name})
        return teacher_id

    async def insertUser(self, userid, **kwargs):
        col = self.db['user']
        kwargs["userid"] = userid
        if col.find_one({"userid": userid}):
            # 이미 있음
            mongoUserid = col.update_one({"userid": userid}, {"$set": kwargs})
        else:
            mongoUserid = col.insert_one(kwargs)
        return mongoUserid

    async def getUser(self, userid):
        col = self.db['user']
        if col.find_one({"userid": userid}):
            user = col.find_one({"userid": userid}, {"_id": 0, "userid": 0})
            return user
        else:
            return "사용자 정보가 없습니다."


    async def deleteUser(self, userid):
        col = self.db['user']
        if col.find_one({"userid": userid}):
            mongoUserid = col.delete_one({"userid": userid})
        else:
            mongoUserid = -1
        return mongoUserid
