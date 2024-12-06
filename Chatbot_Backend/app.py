from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

# Set up logging for better debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Enable CORS for all routes, allowing requests from localhost:3000
CORS(app, origins="http://localhost:3000")

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"  # Change model name if needed
API_TOKEN = "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"  # Insert your Hugging Face API token here

# Increase max content length for large responses
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit for large responses

@app.route('/process', methods=['POST'])
def process_text():
    # Get the text from the request body
    data = request.get_json()
    text = data.get('text', '')

    # Prepare headers and payload for Hugging Face API
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    # Tokenize the input and estimate the length
    input_tokens = len(text.split())  # Estimate by word count, but tokenization might differ
    logging.debug(f"Input text length: {input_tokens} words")

    # Setting parameters for the Hugging Face model
    max_input_length = 1024  # Set input token length to avoid large inputs
    max_output_length = 512  # Limit the number of tokens the model can generate

    # If the input length is too long, truncate it
    if input_tokens > max_input_length:
        text = ' '.join(text.split()[:max_input_length])
        logging.warning(f"Input text too long, truncating to {max_input_length} tokens")

    payload = {
        "inputs": text,
        "parameters": {
            "max_length": max_input_length + max_output_length,  # Total length = input + output
            "max_new_tokens": max_output_length,  # Limit the number of tokens generated
            "do_sample": False,  # Disable sampling for deterministic output
            "top_k": 50,  # Control diversity of responses
            "top_p": 0.95,  # Control the cumulative probability for top tokens
            "temperature": 0.7,  # Lower temp for more controlled and coherent output
            "repetition_penalty": 1.2  # Prevent repetition in responses
        }
    }

    try:
        # Send the request to Hugging Face API
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

        # Log the raw response for debugging
        logging.debug(f"Response Status Code: {response.status_code}")
        logging.debug(f"Raw Response: {response.text[:500]}...")  # Log first 500 characters of the response

        if response.status_code == 200:
            result = response.json()

            # Log the result for further debugging
            logging.debug(f"Processed Response: {result}")

            # Ensure that the response contains the generated text
            if isinstance(result, list) and "generated_text" in result[0]:
                # Limit the response size to 1000 characters to avoid exceeding Vercel limits
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
