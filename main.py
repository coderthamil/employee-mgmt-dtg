from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,EmailStr
from typing import Dict,Any

app = FastAPI()

#user model
class User(BaseModel):
    id:int
    name:str
    age:int
    phone_number:int
    email:EmailStr
    location:str


users:Dict[int,Dict[str,Any]]={}
'''Users={
            1:{
                    name:ram
                    age:23
                    phone_number:9876543210
                    email:ram@email.com
                    location:chennai
               }
            }'''
@app.post("/add_user")
            #object:Dictionarynamr
def add_user(user: User):
      #iterbale in Dictionary
    if user.id in users:
        raise HTTPException(status_code=400, detail="ID already exists")
        #object for values in Dictionaryname.values
    for u in users.values():
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")
        if u["phone_number"] == user.phone_number:
            raise HTTPException(status_code=400, detail="Phone number already exists")
    users[user.id] = user.dict()
    return {"message": "User added successfully", "user": user}

@app.get("/users")
def get_users():
    return users
