from fastapi import FastAPI, File, UploadFile
from deta import Deta
from pydantic import BaseModel
import hashlib
import jwt
import io
import base64
import uuid
import json
from datetime import datetime, timedelta
from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from PIL import Image 
import PIL 

# pydantic to declare body of put or post
app = FastAPI()
a = "c02ff9ee_aRR2Gi3m4xe76"
deta = Deta(a+"F8txNbk77WqghL4nKKs")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        
class Subject(BaseModel):
    username: str
    name: str
    about: str

@app.post("/api/subjects")
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
        
@app.get("/api/subjects/{username}")
def getprojects(username: str):
    
    subjectdb = deta.Base("Notecaster_Subject")
    allSubjects = next(subjectdb.fetch({"username": username}))
    return allSubjects

@app.get("/api/subject/{key}")
def getproject(key: str):
    
    try:
        subjectdb = deta.Base("Notecaster_Subject")
        theSubject = subjectdb.get(key)
        return theSubject
    
    except:
        return({
            "status": 404,
            "message": "Project Does not Exist"
        })

@app.put("/api/subject/{key}")
def updateproject(key: str, subject: Subject):
    
    try:
        subjectdb = deta.Base("Notecaster_Subject")
        theSubject = subjectdb.get(key)
        theSubject['name'] = subject.name
        theSubject['about'] = subject.about
        theSubject = subjectdb.put(theSubject)
        return theSubject
    
    except:
        return({
            "status": 404,
            "message": "Project Does not Exist"
        })

@app.delete("/api/subject/{key}")
def getproject(key: str):
    
    try:
        subjectdb = deta.Base("Notecaster_Subject")
        subjectdb.delete(key)
        return ({
            "status": 203,
            "message": "Deleted Successfully."
        })
    
    except:
        return({
            "status": 404,
            "message": "Project Does not Exist"
        })
        

@app.put("/api/subjectimage/{key}")
def updateImage(key: str = "", file: UploadFile = File(...)):
    
    subjectDrive = deta.Drive("Notecaster_Subject")
    
    fileName = str(uuid.uuid4())
    fileExtension = file.filename.split(".")[1]
    fileName += "."+fileExtension
    
    subjectDrive.put(name=fileName, data=file.file, content_type="image/"+fileExtension)

    #update image location in db
    subjectdb = deta.Base("Notecaster_Subject")
    theSubject = subjectdb.get(key)
    theSubject['image'] = fileName
    theSubject = subjectdb.put(theSubject)
    theSubject['status'] = 200
    return theSubject

@app.put("/api/removesubjectimage/{key}")
def deleteImage(key: str = "", file: UploadFile = File(...)):
    
    subjectDrive = deta.Drive("Notecaster_Subject")
    subjectdb = deta.Base("Notecaster_Subject")
    theSubject = subjectdb.get(key)
    
    thatImage = theSubject['image']
    deleted_file = subjectDrive.delete(thatImage)
    
    del theSubject['image']
    
    theSubject = subjectdb.put(theSubject)
    return theSubject