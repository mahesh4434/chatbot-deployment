from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

# Set up logging for better debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "https://chatbot-deployment-e3gg.vercel.app"}})

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
API_TOKEN = "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"  # Insert your valid Hugging Face API token here

# Increase max content length for large responses
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit for large responses

@app.route('/process', methods=['POST'])
def process_text():
    data = request.get_json()
    text = data.get('text', '')

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": text,
        "parameters": {
            "max_new_tokens": 200,  # Reduce token generation length
            "temperature": 0.7,
            "top_k": 50,
            "top_p": 0.95,
            "do_sample": False,
        }
    }

    try:
        # Send the request to Hugging Face API with increased timeout
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and "generated_text" in result[0]:
                return jsonify({"generated_text": result[0]["generated_text"][:1000]})
            else:
                return jsonify({"error": "Unexpected response structure", "raw_response": result})
        else:
            return jsonify({
                "error": f"Failed to process the request: {response.status_code}",
                "status_code": response.status_code,
                "raw_response": response.text
            })
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out", "status_code": 408})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}", "status_code": 500})

# Vercel handler
def handler(req, res):
    return app(req, res)

if __name__ == '__main__':
    app.run(debug=True)
