# FastAPI User Management System

This is a simple user management system implemented with FastAPI, Firebase, and Pyrebase.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Testing](#testing)
- [API Endpoints](#api-endpoints)


## Features

- User registration
- User login
- User profile management
- Password reset functionality

## Requirements

- Python 3.6+
- FastAPI
- Firebase Admin SDK
- Pyrebase
- SendGrid (for sending password reset emails)
- Firebase Authentication

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/your-repo.git


Here are the libraries you need to install:

1. FastAPI
2. Firebase Admin SDK (firebase-admin)
3. Pyrebase
4. SendGrid (if you want to use SendGrid for sending password reset emails)

You can install these libraries by running the following command:

```bash
pip install -r requirements.txt

Usage
You can use the API endpoints to register users, login, manage user profiles, and reset passwords.

API Documentation
Access the Swagger documentation at http://localhost:8000/docs for details on available endpoints.

Testing
We have provided test cases in the test_main.py file. To run the tests:
for proper testing can follow postman link
Make sure your FastAPI server is running.

Execute the tests using the following command:
pytest test_main.py
<img width="947" alt="Screenshot 2023-11-08 164832" src="https://github.com/Sakhtiman/mugs/assets/134630688/dd8dae0f-abab-4d22-8f82-086436aa94f5">
API Endpoints
POST /register: Register a new user.
<img width="906" alt="Screenshot 2023-11-08 164949" src="https://github.com/Sakhtiman/mugs/assets/134630688/20ba8adb-2767-43a1-bb6d-f8a354008d07">

POST /login: Log in a user and get an authentication token.
<img width="932" alt="Screenshot 2023-11-08 165041" src="https://github.com/Sakhtiman/mugs/assets/134630688/94f37811-2f22-4992-9830-ade1eba2b9e0">

GET /uid: Get the user's UID using an authentication token.
GET /profile: Get the user's profile.
<img width="935" alt="Screenshot 2023-11-08 165133" src="https://github.com/Sakhtiman/mugs/assets/134630688/3cbe7f78-3a08-4cdd-bd04-15c175011b36">


PUT /profile/update: Update the user's profile (name, full_name, email).
DELETE /profile/delete: Delete the user's account.
POST /password-reset/request: Request a password reset.
<img width="914" alt="Screenshot 2023-11-08 165223" src="https://github.com/Sakhtiman/mugs/assets/134630688/6eb77bfe-e9d8-4d30-9584-60fad33d65c5">

POST /password-reset/reset: Reset the user's password.

##postman documentation links validation:
https://www.postman.com/orbital-module-specialist-67685748/workspace/mugs/collection/31009994-bb5a3bbc-24a2-43da-b250-33e3093292cd?action=share&creator=31009994
