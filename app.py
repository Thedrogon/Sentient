# -----------------------------------------------------------------------------
# app.py - The Core Flask Application
# -----------------------------------------------------------------------------
# This script creates a simple web server that listens for requests from your
# frontend, analyzes the text using a pre-trained model from Hugging Face,
# and sends back the sentiment.

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import logging

# Set up logging to monitor the application
logging.basicConfig(level=logging.INFO)

# Initialize the Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) to allow your frontend
# (even if running on a different address) to communicate with this backend.
CORS(app)

# --- Model Loading ---
# We load the sentiment analysis model from Hugging Face's transformers library.
# The `pipeline` function is a high-level helper that handles all the complex
# steps for you (like tokenization and model inference).
# The model is downloaded and cached the first time this line is run.
try:
    logging.info("Loading sentiment analysis model...")
    # Using a specific, well-regarded model for sentiment analysis.
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    # If the model fails to load, we'll store the exception to return an error message.
    sentiment_pipeline = e


# --- API Endpoint for Prediction ---
# We define a route '/predict' that accepts POST requests.
# This is the endpoint your frontend JavaScript will call.
@app.route('/predict', methods=['POST'])
def predict():
    """
    Receives text data from a POST request, analyzes its sentiment,
    and returns the result in JSON format.
    """
    # Check if the model loaded correctly. If not, return a server error.
    if isinstance(sentiment_pipeline, Exception):
        return jsonify({
            "error": "Model is not available. Please check server logs."
        }), 500

    # Get the JSON data from the request.
    # We use .get_json() which automatically parses the incoming JSON.
    data = request.get_json()

    # Basic validation: Check if the 'text' key exists in the received data.
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid input. 'text' field is required."}), 400

    text_to_analyze = data['text']

    # More validation: Check if the text is empty.
    if not text_to_analyze.strip():
        return jsonify({"error": "Text field cannot be empty."}), 400

    try:
        logging.info(f"Analyzing text: '{text_to_analyze[:50]}...'")
        # The pipeline function takes the text and returns a list of dictionaries.
        # Example: [{'label': 'POSITIVE', 'score': 0.9998}]
        result = sentiment_pipeline(text_to_analyze)

        # We extract the first result from the list.
        prediction = result[0]
        sentiment = prediction['label']
        score = prediction['score']

        logging.info(f"Prediction: {sentiment} with score {score:.4f}")

        # Return the sentiment and score in a JSON response.
        return jsonify({
            "sentiment": sentiment,
            "score": score
        })

    except Exception as e:
        logging.error(f"An error occurred during prediction: {e}")
        # Return a generic error message if something goes wrong during analysis.
        return jsonify({"error": "Failed to analyze sentiment."}), 500

# --- Health Check Endpoint ---
# A simple route to check if the server is running.
@app.route('/', methods=['GET'])
def health_check():
    return "Sentiment Analyzer backend is running!"


# This block ensures the server only runs when the script is executed directly.
if __name__ == '__main__':
    # Runs the app on localhost, port 5000.
    # `debug=True` allows for automatic reloading when you save changes.
    # In a production environment, you would use a proper WSGI server like Gunicorn.
    app.run(host='0.0.0.0', port=5000, debug=True)
