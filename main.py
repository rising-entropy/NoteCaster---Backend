from fastapi import FastAPI
from deta import Deta
from pydantic import BaseModel
import hashlib

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
    
    return({
        "status": 201,
        "message": "User created successfully.",
        "key": newuser.key,
        "fName": user.fName,
        "lName": user.lName,
        "username": user.username,
        "email": user.email,
    })
