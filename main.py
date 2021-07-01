from fastapi import FastAPI
from deta import Deta
from pydantic import BaseModel
import hashlib
import jwt
import io
import base64
import json
from datetime import datetime, timedelta
from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse

from PIL import Image 
import PIL 

# pydantic to declare body of put or post
app = FastAPI()
a = "c02ff9ee_aRR2Gi3m4xe76"
deta = Deta(a+"F8txNbk77WqghL4nKKs")


@app.get("/")
def read_root():
    return {"message": "Let's get Started"}

class User(BaseModel):
    fName: str
    lName: str
    username: str
    email: str
    password: str

@app.post("/api/signup")
def signup(user: User):
    
    userdb = deta.Base("Notecaster_User")
    
    #hash the password
    user.password = hashlib.sha256(user.password.encode()).hexdigest()
    
    createUser = {
        "fName": user.fName,
        "lName": user.lName,
        "username": user.username,
        "email": user.email,
        "password": user.password
    }
    
    try:
        newuser = userdb.insert(createUser, user.username)
    except:
        return({
            "status": 409,
            "message": "User already exists."
        })
        
    JWT_SECRET = 'UnaiSimon$$$'
    JWT_SECRET += user.username
    JWT_ALGORITHM = 'HS256'
    JWT_EXP_DELTA_SECONDS = 2628000
    payload = {'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)}        
    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    
    return({
        "status": 201,
        "message": "User created successfully.",
        "token": jwt_token,
        "key": user.username,
        "fName": user.fName,
        "lName": user.lName,
        "username": user.username,
        "email": user.email,
    })
    
    
class Login(BaseModel):
    username: str
    password: str
    
@app.post("/api/login")
def loginUser(login: Login):
    username = login.username
    password = login.password
    hashedPassword = hashlib.sha256(login.password.encode()).hexdigest()
    userdb = deta.Base("Notecaster_User")
    
    #check if username exists
    theUser = next(userdb.fetch({"username": username}))
    if len(theUser) == 0:
        return({
            "status": 404,
            "message": "Username does not exist."
        })
        
    theUser = theUser[0]
    
    #check password
    if theUser['password'] != hashedPassword:
        return({
            "status": 403,
            "message": "Password does not match."
        })
        
    #generate token
    JWT_SECRET = 'UnaiSimon$$$'
    JWT_SECRET += theUser['username']
    JWT_ALGORITHM = 'HS256'
    JWT_EXP_DELTA_SECONDS = 2628000
    payload = {'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)}        
    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    
    return({
        "status": 200,
        "message": "Successfully Logged In.",
        "token": jwt_token,
        "fName": theUser['fName'],
        "lName": theUser['lName'],
        "username": theUser['username'],
        "email": theUser['email'],
    })
    
    
# class Subject(BaseModel):
#     username = str
#     name = str
#     about = str
        
# @app.post("/api/subject")
# def createSubject(subject: Subject):
    
#     username = subject.username
#     name = subject.name
#     about = subject.about
    
#     print(subject.username)
#     return
    
#     subjectdb = deta.Base("Notecaster_Subject")
    
#     createSubject = {
#         "username": username,
#         "name": name,
#         "about": about
#     }
    
#     newSubject = subjectdb.insert(createSubject)
#     return newSubject
    
#     try:
#         newSubject = subjectdb.insert(createSubject)
#         return newSubject
#     except:
#         return({
#             "status": 500,
#             "message": "Some Error Occurred."
#         })
        
class Subject(BaseModel):
    username: str
    name: str
    about: str

@app.post("/api/subject")
def createproject(subject: Subject):
    
    name = subject.name
    about = subject.about
    username = subject.username
    
    subjectdb = deta.Base("Notecaster_Subject")
    
    createSubject = {
        "username": username,
        "name": name,
        "about": about
    }
    
    try:
        newSubject = subjectdb.insert(createSubject)
        return newSubject
    
    except:
        return({
            "status": 500,
            "message": "Some Error Occurred."
        })