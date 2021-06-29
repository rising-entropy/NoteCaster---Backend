from fastapi import FastAPI
from deta import Deta
from pydantic import BaseModel

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
    
    
    
    return({
        "fName": user.fName,
        "lName": user.lName,
        "username": user.username,
        "email": user.email,
    })
