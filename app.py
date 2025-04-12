from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from HubSpot

@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    user_input = data.get('input')
    result = f"Processed: {user_input}"  # Replace with your logic
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run()
