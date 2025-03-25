from flask import Flask, request, jsonify
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import asyncio
import os

app = Flask(__name__)
clients = {}  # Store Telegram clients based on phone numbers

# Use a shared asyncio event loop
loop = asyncio.get_event_loop()

async def send_code_async(api_id, api_hash, phone_number):
    client = TelegramClient(f"session_{phone_number}", api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
    clients[phone_number] = client  # Store the client after sending the OTP
    return f"OTP sent to {phone_number}"

async def verify_otp_async(phone_number, otp_code, password=None):
    client = clients.get(phone_number)
    if not client:
        raise Exception("Client not found. Start the login process first")

    try:
        await client.sign_in(phone_number, otp_code)
        if await client.is_user_authorized():
            return "Login successful"

    except SessionPasswordNeededError:
        if password:
            await client.sign_in(password=password)
            if await client.is_user_authorized():
                return "Login successful with 2FA"
        else:
            raise Exception("Password required for 2FA-enabled account")

    except Exception as e:
        raise Exception(f"Login failed: {e}")

async def send_message_async(phone_number, chat_id, message_text):
    client = clients.get(phone_number)
    if not client:
        raise Exception("Client not found. Authenticate first")
    
    await client.disconnect()
    await client.connect()
    
    await client.send_message(chat_id, message_text)
    return f"Message sent to {chat_id} successfully!"

async def send_media_async(phone_number, chat_id, file_path, caption=None):
    client = clients.get(phone_number)
    if not client:
        raise Exception("Client not found. Authenticate first")
    
    await client.disconnect()
    await client.connect()
    
    # Convert string IDs to integers and handle peer resolution
    try:
        chat_id = int(chat_id)  # Convert numeric strings to integers
        entity = await client.get_input_entity(chat_id)  # Better resolution method
    except ValueError:
        entity = await client.get_input_entity(chat_id)  # For usernames
        
    await client.send_file(entity, file_path, caption=caption)
    os.remove(file_path)  # Delete the file after sending
    return f"Media sent to {chat_id} successfully!"

async def fetch_members_async(phone_number, group_id, limit=None):
    client = clients.get(phone_number)
    if not client:
        raise Exception("Client not found. Authenticate first")

    await client.disconnect()
    await client.connect()
    
    entity = await client.get_entity(group_id)
    members = await client.get_participants(entity, limit=limit)
    
    members_data = []
    for member in members:
        bio = await client.get_entity(member.id)  # Fetch user bio
        members_data.append({
            "chat_id": member.id,
            "username": member.username,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "bio": bio.about if hasattr(bio, 'about') else None
        })
    
    return members_data

@app.route('/start_login', methods=['POST'])
def start_login():
    data = request.json
    api_id = int(data.get('api_id'))
    api_hash = data.get('api_hash')
    phone_number = data.get('phone_number')

    if not (api_id and api_hash and phone_number):
        return jsonify({"error": "All fields (api_id, api_hash, phone_number) are required"}), 400

    try:
        message = loop.run_until_complete(send_code_async(api_id, api_hash, phone_number))
        return jsonify({"status": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.json
    phone_number = data.get('phone_number')
    otp_code = data.get('otp_code')
    password = data.get('password')  # Optional for 2FA

    if not (phone_number and otp_code):
        return jsonify({"error": "Both phone_number and otp_code are required"}), 400

    try:
        message = loop.run_until_complete(verify_otp_async(phone_number, otp_code, password))
        return jsonify({"status": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    phone_number = data.get('phone_number')
    chat_id = data.get('chat_id')
    message_text = data.get('message_text')

    if not (phone_number and chat_id and message_text):
        return jsonify({"error": "All fields (phone_number, chat_id, message_text) are required"}), 400

    try:
        message = loop.run_until_complete(send_message_async(phone_number, chat_id, message_text))
        return jsonify({"status": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_media', methods=['POST'])
def send_media():
    phone_number = request.form.get('phone_number')
    chat_id = request.form.get('chat_id')
    caption = request.form.get('caption')
    media = request.files.get('media')

    if not (phone_number and chat_id and media):
        return jsonify({"error": "phone_number, chat_id, and media file are required"}), 400

    file_path = f"temp_{media.filename}"
    media.save(file_path)

    try:
        message = loop.run_until_complete(send_media_async(phone_number, chat_id, file_path, caption))
        return jsonify({"status": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fetch_members', methods=['POST'])
def fetch_members():
    data = request.json
    phone_number = data.get('phone_number')
    group_id = data.get('group_id')
    limit = data.get('limit')

    if not (phone_number and group_id):
        return jsonify({"error": "Both phone_number and group_id are required"}), 400

    try:
        members = loop.run_until_complete(fetch_members_async(phone_number, group_id, limit=limit))
        return jsonify({"members": members}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
