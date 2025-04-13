from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from HubSpot

@app.route('/')
def home():
    return 'API is running!'


if __name__ == '__main__':
    app.run()
