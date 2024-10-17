from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import re
import bcrypt
import datetime
import requests  # For making API calls to weather or other services

# Initialize Flask app
app = Flask(__name__)  # Fixed _name_ to __name__

# Enable CORS
CORS(app)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['Blind_Walking_Stick']
users_collection = db['users']

# Password validation pattern: At least 8 characters, 1 special character
PASSWORD_REGEX = r'^(?=.*[!@#$%^&(),.?":{}|<>])(?=.*[a-zA-Z]).{8,}$'

# Weather API Key
WEATHER_API_KEY = "644499f581c7474c88322946243108"  # Set your Weather API key here

# 1. User Registration API
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    name = data.get('name')
    mobile = data.get('mobile')
    email = data.get('email')
    stickId = data.get('stickId')
    emergency_contacts = data.get('emergencyContacts', [])
    password = data.get('password')

    # Validate inputs
    if not name or not mobile or not email or not stickId or len(emergency_contacts) != 3:
        return jsonify({"error": "All fields are required and must include 3 emergency contacts"}), 400
    
    if not re.match(PASSWORD_REGEX, password):
        return jsonify({"error": "Password must be at least 8 characters and contain 1 special character"}), 400

    # Check if user already exists
    if users_collection.find_one({"mobile": mobile}):
        return jsonify({"error": "User with this mobile number already exists"}), 409

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Save user data
    user = {
        "name": name,
        "mobile": mobile,
        "email": email,
        "stickId": stickId,
        "emergency_contacts": emergency_contacts,
        "password": hashed_password
    }
    users_collection.insert_one(user)
    return jsonify({"message": "User registered successfully"}), 201

# 2. User Login API
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    mobile = data.get('mobile')
    stickId = data.get('stickId')
    password = data.get('password')

    # Validate inputs
    if not mobile or not stickId or not password:
        return jsonify({"error": "Mobile number, stick ID, and password are required"}), 400

    # Find user by mobile number and stick ID
    user = users_collection.find_one({"mobile": mobile, "stickId": stickId})

    if not user:
        return jsonify({"error": "Invalid mobile number or stick ID"}), 404

    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({"error": "Invalid password"}), 401

    # Return user details along with success message
    return jsonify({
        "message": "Login successful",
        "name": user["name"],
        "stickId": user["stickId"]
    }), 200

# 3. Get User Details API
@app.route('/get_user_details', methods=['GET'])
def get_user_details():
    mobile = request.args.get('mobile')  # Get the mobile number from query parameters

    # Find user by mobile number
    user = users_collection.find_one({"mobile": mobile}, {"_id": 0, "password": 0})  # Exclude the password

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Return the user's name, stickId, and email
    return jsonify({
        "name": user["name"],
        "stickId": user["stickId"],
    }), 200

# 4. Get User Email by Mobile API
@app.route('/get_user_email', methods=['GET'])
def get_user_email():
    mobile = request.args.get('mobile')  # Get the mobile number from query parameters

    # Find user by mobile number
    user = users_collection.find_one({"mobile": mobile}, {"_id": 0, "email": 1})  # Only retrieve the email field

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Return the user's email
    return jsonify({
        "email": user["email"]
    }), 200

# 5. Voice Command API
@app.route('/voice_command', methods=['GET'])
def voice_command():
    mobile = request.args.get('mobile')  # Get the mobile number from query parameters
    command = request.args.get('command')  # Get the command from query parameters

    # Validate inputs
    if not mobile or not command:
        return jsonify({"error": "Mobile number and command are required"}), 400

    response = ""

    # Process voice command
    if command.lower() == "date":
        response = datetime.datetime.now().strftime("%Y-%m-%d")
    elif command.lower() == "time":
        response = datetime.datetime.now().strftime("%H:%M:%S")
    elif command.lower() == "wikipedia":
        response = "You can search Wikipedia at https://www.wikipedia.org/"
    elif command.lower() == "youtube":
        response = "You can visit YouTube at https://www.youtube.com/"
    elif command.lower() == "location":
        # Use a geolocation API to get the user's location
        location_response = requests.get('http://ip-api.com/json/')
        location_data = location_response.json()
        
        if location_data['status'] == 'success':
            response = f"Your location is {location_data['city']}, {location_data['regionName']}, {location_data['country']}"
        else:
            response = "Unable to retrieve location."

    elif command.lower() == "weather":
        # Get the weather for the user's location
        location_response = requests.get('')
        location_data = location_response.json()
        
        if location_data['status'] == 'success':
            city = location_data['city']
            weather_response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric')
            weather_data = weather_response.json()
            
            if weather_data['cod'] == 200:
                temp = weather_data['main']['temp']
                description = weather_data['weather'][0]['description']
                response = f"The current temperature in {city} is {temp}°C with {description}."
            else:
                response = "Unable to retrieve weather information."
        else:
            response = "Unable to retrieve location."

    else:
        response = "Unknown command."

    # Return response to the user
    return jsonify({"mobile": mobile, "response": response}), 200

# Start Flask server
if __name__ == '__main__':  # Fixed _name_ to __name__
    app.run(debug=True, host='0.0.0.0', port=5000)
