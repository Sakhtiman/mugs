from pydantic import BaseModel, EmailStr,constr

class UserRegistration(BaseModel):
    name: constr(min_length=4, max_length=20)
    email: EmailStr
    full_name: constr(min_length=3, max_length=50)
    password: constr(min_length=8, max_length=50)

    class Config:
        schema_extra = {
            "example": {
                "name": "mugsnamana",
                "email": "example@gmail.com",
                "password": "samplepass123",
                "full_name": "namanjain"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=50)
    
    class Config:
        schema_extra = {
            "example": {
                "email": "example@gmail.com",
                "password": "samplepass123"
            }
        }

class ResetRequest(BaseModel):
    email: str

class ResetPassword(BaseModel):
    token: str
    new_password: str


