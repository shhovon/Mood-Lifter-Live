# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

TOMORROW_IO_API_KEY = 'LRdpOcscGcCaRIfDMPmtPaftfHDmFu7k'
IPSTACK_API_KEY = '74f82293891a9328e3a78d729f446d4c'

def get_location(ip):
    url = f'http://api.ipstack.com/{ip}?access_key={IPSTACK_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('city'), data.get('latitude'), data.get('longitude')
    return None, None, None

def get_weather(lat, lon):
    url = f'https://api.tomorrow.io/v4/weather/forecast?location={lat},{lon}&apikey={TOMORROW_IO_API_KEY}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        first_minute_data = data['timelines']['minutely'][0]['values']
        return {
            'city': f'Lat: {lat}, Lon: {lon}',  # You can replace this with actual city name if available
            'weather': {
                'temp': first_minute_data['temperature'],  # Access the temperature value
                'description': get_weather_description(first_minute_data['weatherCode'])  # Map weatherCode to description
            },
            'weather_message': 'Stay hydrated!'  # Custom message
        }
    return None

def get_weather_description(code):
    weather_codes = {
        1000: 'Clear',
        1100: 'Mostly Clear',
        1101: 'Partly Cloudy',
        1102: 'Mostly Cloudy',
        # Add more codes as necessary...
    }
    return weather_codes.get(code, 'Unknown weather condition')


def get_weather_message(weather):
    messages = {
        'clear': [
            "Clear skies ahead! Time to shine like the sun!",
            "It's a beautiful day outside. Why not take a moment to enjoy it?",
            "Sunny days are here again! Let's make the most of it!"
        ],
        'clouds': [
            "Cloudy with a chance of awesome! Your mood can brighten any day.",
            "Even on cloudy days, your potential is limitless!",
            "Clouds are nature's way of painting the sky. What will you create today?"
        ],
        'rain': [
            "Rainy days are perfect for cozy productivity. What's on your to-do list?",
            "The plants are getting a refreshing drink. How about treating yourself too?",
            "Rain is liquid sunshine. Let it wash away your worries!"
        ],
        'hot': [
            "It's a scorcher out there! Stay cool and hydrated, you hot stuff!",
            "Feels like the sun is giving us a big, warm hug today. Embrace it!",
            "Hot day alert! Time to chill out and take it easy."
        ],
        'cold': [
            "Brrr! It's nippy out there. Perfect weather for warm thoughts and hot cocoa!",
            "Cold days are nature's way of saying 'stay in and cuddle up'!",
            "Chilly weather outside, but your heart can keep you warm inside!"
        ]
    }
    
    if weather['temp'] > 30:
        return random.choice(messages['hot'])
    elif weather['temp'] < 10:
        return random.choice(messages['cold'])
    elif 'clear' in weather['description'].lower():
        return random.choice(messages['clear'])
    elif 'cloud' in weather['description'].lower():
        return random.choice(messages['clouds'])
    elif 'rain' in weather['description'].lower():
        return random.choice(messages['rain'])
    else:
        return "Whatever the weather, you've got this!"

def get_mood_message(mood):
    messages = {
        'happy': [
            "Your happiness is contagious! Spread the joy!",
            "Glad to see you're feeling great! Keep that positive energy flowing!",
            "Happiness looks good on you! Enjoy every moment of it!"
        ],
        'sad': [
            "It's okay to feel down sometimes. Remember, this too shall pass.",
            "Sending you a virtual hug. You're stronger than you know!",
            "Even on tough days, you're still amazing. Be gentle with yourself."
        ],
        'neutral': [
            "Feeling neutral? That's a clean slate to create any mood you want!",
            "A neutral mood is like a blank canvas. What masterpiece will you create today?",
            "Sometimes, being in the middle is the perfect place to start something great!"
        ],
        'excited': [
            "Excitement is in the air! What wonderful things await you today?",
            "Your enthusiasm is electric! Go out there and light up the world!",
            "Excited energy is the fuel for amazing achievements. What will you accomplish?"
        ],
        'tired': [
            "Feeling tired? Remember, rest is not a luxury, it's a necessity. Take care of yourself!",
            "Even when you're tired, you're still capable of amazing things. But don't forget to recharge!",
            "A tired body often hides a determined spirit. Listen to what yours needs right now."
        ]
    }
    return random.choice(messages.get(mood, ["You're doing great!"]))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user_info', methods=['GET'])
def user_info():
    ip = request.remote_addr
    city, lat, lon = get_location(ip)
    if not all([city, lat, lon]):
        return jsonify({'error': 'Unable to determine location'}), 400
    
    weather = get_weather(lat, lon)
    if not weather:
        return jsonify({'error': 'Unable to fetch weather data'}), 400
    
    weather_message = get_weather_message(weather)
    
    return jsonify({
        'city': city,
        'weather': weather,
        'weather_message': weather_message
    })

@app.route('/mood_message', methods=['POST'])
def mood_message():
    data = request.json
    mood = data['mood']
    
    message = get_mood_message(mood)
    return jsonify({'message': message})


@app.route('/get-ip-info', methods=['GET'])
def get_ip_info():
    try:
        ipapi_url = 'https://ipapi.co/json/'
        ip_response = requests.get(ipapi_url)
        ip_response.raise_for_status()  # Raise an error for bad responses
        return jsonify(ip_response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500  # Return an error response


if __name__ == '__main__':
    app.run(debug=True)