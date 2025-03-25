# Telegram-AI
This repository provide a script to fetch members from any telegram group, send message and send media to groups or individuals using your user account.
# Flask Telegram Automation API

This script provides a Flask-based API for automating Telegram tasks using the Telethon library. The API allows users to authenticate, send messages, send media, and fetch group members.

## Features
- User Authentication: Send OTP and verify it to log in.
- Send Messages: Send text messages to a chat.
- Send Media: Send images, videos, and files with an optional caption.
- Fetch Group Members: Retrieve details of group members, including their username, bio, and names.

## Prerequisites
- Python 3.7+
- Telegram API credentials (API ID and API Hash)
- Flask
- Telethon

## Installation
   Install dependencies:
   pip install flask telethon asyncio
   

## Usage

### 1. Start the Flask Server
Run the Flask app:
python app.py (name of the python script)

### 2. API Endpoints

#### 1. Start Login Process
- Endpoint: '/start_login'
- Method: 'POST'
- Description: Sends an OTP to the provided phone number.

- Request JSON:
 
  {
    "api_id": 123456,
    "api_hash": "your_api_hash",
    "phone_number": "+1234567890"
  }
  
- Response:
  { "status": "OTP sent to +1234567890" }
  

#### 2. Verify OTP
- Endpoint: '/verify_otp'
- Method: 'POST'
- Description: Verifies the OTP received and logs in the user.

- Request JSON:
  {
    "phone_number": "+1234567890",
    "otp_code": "12345",
    "password": "optional_2fa_password"
  }
  
- Response:
  { "status": "Login successful" }
  

#### 3. Send Message
- Endpoint: '/send_message'
- Method: 'POST'
- Description: Sends a text message to a chat.

- Request JSON:
  {
    "phone_number": "+1234567890",
    "chat_id": 123456,
    "message_text": "Hello, this is a test message!"
  }
  
- Response:
  { "status": "Message sent to @username_or_id successfully!" }
 

#### 4. Send Media
- Endpoint: '/send_media'
- Method: 'POST'
- Description: Sends an image, video, or file to a chat.

- Request Form Data:
  - 'phone_number': '+1234567890'
  - 'chat_id': '-123456'
  - 'caption': '"Optional caption"'
  - 'media': File upload (image, video, or document)

- Response:
  { "status": "Media sent to @username_or_id successfully!" }


#### 5. Fetch Group Members
- Endpoint: '/fetch_members'
- Method: 'POST'
- Description: Fetches members of a Telegram group.

- Request JSON:
  {
    "phone_number": "+1234567890",
    "group_id": "@group_username_or_id",
    "limit": 100 (number of members you want to fetch from the group)
  }
  
- Response:
  {
    "members": [
{
"chat_id": 123456789,
"username": "user1",
"first_name": "John",
"last_name": "Doe",
"bio": "Hello!"
}
]
  }

## Notes
- Ensure that your Telegram account is logged in successfully before sending messages or media.
- The API uses an in-memory dictionary (`clients`) to store user sessions.


