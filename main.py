from fastapi import FastAPI, HTTPException,status,Request
from firebase_admin import credentials, auth, firestore
from fastapi.responses import JSONResponse
import time
from fastapi.requests import Request
from models import UserRegistration, UserLogin,ResetRequest,ResetPassword
import firebase_admin
import logging
from sendgrid.helpers.mail import Mail
from fastapi import Query
import pyrebase
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import uvicorn
from functools import wraps



# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
calls = []
# Define the rate limiting settings (adjust as needed)
def rate_limited(max_calls: int, time_frame: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            now = time.time()
            calls_in_time_frame = [call for call in calls if call > now - time_frame]
            if len(calls_in_time_frame) >= max_calls:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded.")
            calls.append(now)
            return await func(request, *args, **kwargs)

        return wrapper
    return decorator
# Apply rate limiting to all routes
@app.middleware("http")
async def add_rate_limit_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(5)  # Adjust as needed
    response.headers["X-RateLimit-Remaining"] = str(5 - len(calls))
    return response

# Your existing FastAPI routes and functions
custom_swagger_ui_path = "/api-docs"

@app.get(custom_swagger_ui_path)
@rate_limited(max_calls=5, time_frame=60)
async def check_rate_limit_5(request:Request):
    return {"message": "you can check till 5 requests"}

if not firebase_admin._apps:
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)


firebaseConfig = {
  "apiKey": "AIzaSyBwQVIAmREyNBxguQblXZ6FpRggBv9yg3g",
  "authDomain": "mugs-16981.firebaseapp.com",
  "projectId": "mugs-16981",
  "storageBucket": "mugs-16981.appspot.com",
  "messagingSenderId": "242663768288",
  "appId": "1:242663768288:web:ade880a4aa659d81ed5085",
  "measurementId": "G-NJ116FTPZB",
  "databaseURL":""
}
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "2105470@kiit.ac.in"
SMTP_PASSWORD = "ssve xtfk mfee gllz"
SMTP_STARTTLS = True  # Use STARTTLS for security

firebase=pyrebase.initialize_app(firebaseConfig)
@app.post("/register")
@rate_limited(max_calls=5, time_frame=60)
async def register_user(request:Request,user_data: UserRegistration):
    name = user_data.name
    email = user_data.email
    password = user_data.password
    full_name = user_data.full_name

    try:
        # Create the user using Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password
           
        )
        db = firestore.client()
        user_ref = db.collection("users").document(user.uid)

        user_ref.set({
            "name": name,
            "email": email,
            "full_name": full_name,
            "password":password,
            "created_at": firestore.SERVER_TIMESTAMP
        })

        return JSONResponse(content={"message": f"User created successfully - UID: {user.uid}"}, status_code=201)
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="User already exists")

# global_token = None
user_tokens = {}

@app.post("/login")
@rate_limited(max_calls=5, time_frame=60)
async def login_user(user_data: UserLogin):
    email = user_data.email
    password = user_data.password

    try:
        # Authenticate the user using Firebase Authentication
        user = firebase.auth().sign_in_with_email_and_password(email=email, password=password)

        # Get the user's ID token
        token = user['idToken']

        # Store the token in the user_tokens dictionary with the email as the key
        user_tokens[email] = token

        return {"token": token}

    except auth.UserNotFoundError:
        raise HTTPException(status_code=401, detail="User not found")

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to log in user")

# Dependency to get the global token

@app.get("/uid")
async def get_current_user_uid(id_token: str = Query(...)):
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token.get("uid")
        logging.info(f"ID token verified successfully. User UID: {uid}")
        return {"uid": uid}
    except auth.InvalidIdTokenError as e:
        logging.error(f"Error verifying ID token: {e}")
        return {"error": "Invalid ID token"}

@app.get("/profile")
@rate_limited(max_calls=5, time_frame=60)
async def get_user_profile(request: Request, uid: str = Query(...)):
    # Debugging: Print the received UID
    print(f"Received UID: {uid}")

    # Debugging: Construct the Firestore document path
    document_path = f"users/{uid}"
    print(f"Firestore Document Path: {document_path}")

    # Fetch and return the user's profile information from Firestore using the provided UID
    db = firestore.client()
    user_ref = db.document(document_path)
    user_data = user_ref.get().to_dict()
    
    if user_data:
        # Exclude the "password" field from the user's profile data
        user_data.pop("password", None)

        return user_data
    else:
        # Debugging: Print a message when the profile is not found
        print(f"User profile not found for UID: {uid}")
        raise HTTPException(status_code=404, detail="User profile not found")


@app.put("/profile/update")
@rate_limited(max_calls=5, time_frame=60)
async def update_user_profile(request: Request, user_data: dict, current_user: str = get_current_user_uid):
    # Fields that are allowed to be updated
    allowed_fields = ["name", "full_name", "email"]

    # Create a dictionary containing only the allowed fields
    update_data = {field: user_data.get(field) for field in allowed_fields if field in user_data}

    # Check if any valid fields to update are provided
    if not update_data:
        return {"message": "No valid fields to update."}

    # Update the user's profile information in Firestore
    db = firestore.client()
    user_ref = db.collection("users").document(current_user)

    # Update only the allowed fields
    user_ref.update(update_data)

    return {"message": "User profile updated successfully"}

@app.delete("/profile/delete")
@rate_limited(max_calls=5, time_frame=60)
async def delete_user_account(request: Request,current_user: str = get_current_user_uid):
    try:
        # Delete the user's account from Firebase Authentication
        auth.delete_user(current_user)
        # Also, delete the user's profile data from Firestore if needed
        db = firestore.client()
        user_ref = db.collection("users").document(current_user)
        user_ref.delete()
        return {"message": "User account deleted successfully"}
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/password-reset/request")
async def request_password_reset(
    request: Request, user_data: ResetRequest, token: str = Query(None)
):
    email = user_data.email

    try:
        # Use the 'token' associated with the provided email address
        if email in user_tokens:
            token = user_tokens[email]

        # Continue with your password reset logic using the correct token

        # Send a password reset email with the JWT token included
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME  # Replace with your email address
        msg['To'] = email
        msg['Subject'] = "Password Reset Request"
        body = f"Click the following link to reset your password: https://example.com/reset-password?token={token}"
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server of your email provider and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Use STARTTLS for security, adjust if needed
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, [email], msg.as_string())  # Use the recipient's email address

        return {"message": "Password reset email sent successfully"}

    except auth.UserNotFoundError:
        raise HTTPException(status_code=401, detail="User not found")

    except smtplib.SMTPException as e:
        return HTTPException(status_code=500, detail=f"SMTP Error: {str(e)}")

    except Exception as e:
        return HTTPException(status_code=500, detail="Failed to send the reset email")


@app.post("/password-reset/reset")
async def reset_password(data: ResetPassword):
    try:
        # Verify the token
        reset_token = data.token  # Extract the reset_token from the request
        
        # Implement additional checks, such as token expiration and associated user
        
        # Check if the token is valid and the user exists
        decoded_token = auth.verify_id_token(reset_token)
        user_id = decoded_token.get("uid")
        
        # Check if the user exists
        user = auth.get_user(user_id)
        
        if user:
            # Update the user's password using Firebase Authentication
            auth.update_user(user_id, password=data.new_password)
            
            # Return a success message when the password is reset
            return {"message": "Password reset successful."}
        else:
            raise HTTPException(status_code=404, detail="User not found.")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found.")
    except Exception as e:
        # Handle other errors, such as Firebase Authentication errors
        return HTTPException(status_code=500, detail="Failed to reset the password")



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
