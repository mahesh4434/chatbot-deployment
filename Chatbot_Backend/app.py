from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://maheshai.vercel.app", "http://localhost:3000"]}})

API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
API_TOKEN = "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"

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/process', methods=['POST'])
def process_text():
    data = request.get_json()
    text = data.get('text', '')

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    input_tokens = len(text.split())
    logging.debug(f"Input text length: {input_tokens} words")

    max_input_length = 1024
    max_output_length = 512

    if input_tokens > max_input_length:
        text = ' '.join(text.split()[:max_input_length])
        logging.warning(f"Input text too long, truncating to {max_input_length} tokens")

    payload = {
        "inputs": text,
        "parameters": {
            "max_length": max_input_length + max_output_length,
            "max_new_tokens": max_output_length,
            "do_sample": False,
            "top_k": 50,
            "top_p": 0.95,
            "temperature": 0.7,
            "repetition_penalty": 1.2
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        logging.debug(f"Response Status Code: {response.status_code}")
        logging.debug(f"Raw Response: {response.text[:500]}")

        if response.status_code == 200:
            result = response.json()
            logging.debug(f"Processed Response: {result}")

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

if __name__ == '__main__':
    app.run(debug=True)
