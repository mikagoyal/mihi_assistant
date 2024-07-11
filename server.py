import logging
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import prompt_definition
import embeddings
from flask_socketio import SocketIO, emit

# Initialise Flask app and CORS
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.logger.setLevel(logging.ERROR)

# Define the route for the index page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')  # Render the index.html template

# Define the route for processing messages
@app.route('/process-message', methods=['POST'])
def process_message_route():
    user_message = request.json['userMessage']  # Extract the user's message from the request
    
    if "transcript" in user_message.lower():
        # Get the generated transcript from the embeddings module
        generated_transcript = embeddings.audio.get_transcripts()

        # Return the generated transcript as the bot's response
        return jsonify({
            "botResponse": generated_transcript[0],
            "generatedTranscript": generated_transcript[0]
        }), 200
    
    # Check if the user is requesting image generation
    elif "generate an image of" in user_message.lower():
        # Generate the image using the prompt_definition module
        image_url = prompt_definition.generate_image(user_message)
        
        # Return the image URL as the bot's response
        return jsonify({
            "botResponse": f"Here is the image you requested: ",
            "imageUrl": image_url
        }), 200
    
    # Process the user's message using the prompt_definition module
    bot_response = prompt_definition.get_answer_from_chain(user_message)
    
    # Return the bot's response along with the extracted text as JSON
    return jsonify({
        "botResponse": bot_response
    }), 200

# Define the route for processing documents
@app.route('/process-document', methods=['POST'])
def process_document_route():
    # Check if files were uploaded
    if 'files' not in request.files:
        return jsonify({
            "botResponse": "No files uploaded. Please upload a PDF, DOCX, XLSX, or image file."
        }), 400

    files = request.files.getlist('files')  # Extract the uploaded files from the request
    file_paths = []
    file_extensions = []

    for file in files:
        file_path = os.path.join("uploads", file.filename)  # Define the path where the file will be saved
        file.save(file_path)  # Save the file
        file_paths.append(file_path)
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        file_extensions.append(file_extension)
        
    doc_files = [file_paths[i] for i in range(len(file_paths)) if file_extensions[i] in {'.pdf', '.docx', '.xlsx'}]
    image_files = [file_paths[i] for i in range(len(file_paths)) if file_extensions[i] in {'.png', '.jpg', '.jpeg'}]
    audio_files = [file_paths[i] for i in range(len(file_paths)) if file_extensions[i] in {'.mp3'}]

    if doc_files:
        embeddings.doc.process_documents(doc_files)  # Process the documents using the embeddings module
    if image_files:
        embeddings.image.add_images(image_files)  # Process the images using the embeddings module
    if audio_files:
        embeddings.audio.load_transcripts(audio_files)

    # Return a success message as JSON
    return jsonify({
        "botResponse": "Thank you for providing your files. They have been analyzed, and you can now ask any questions regarding them!"
    }), 200


# Define a route to handle WebSocket connections and stream responses
@socketio.on('start_stream')
def handle_start_stream(data):
    user_message = data.get('userMessage')
    
    if "transcript" in user_message.lower():
        transcripts = embeddings.audio.get_transcripts()
        for transcript in transcripts:
            for token in transcript.split():
                stream.on_llm_new_token(token)
            emit('stream_response', {'data': '\n'})

    if "http" in user_message.lower():
        embeddings.video.load_videos(user_message)
    
    str = ""
    if "generate an image of" in user_message.lower():
        str = embeddings.generate_img.generate_image(user_message)                    
    else:
        str = prompt_definition.get_answer_from_chain(user_message)

    stream = prompt_definition.Streaming()
    for token in str.split():
        stream.on_llm_new_token(token=token)
    emit('stream_response', {'data': '\n'})

# Run the Flask app
if __name__ == "__main__":
    # Ensure the upload directory exists
    os.makedirs("uploads", exist_ok=True)
    socketio.run(app, debug=True, port=8000, host='0.0.0.0')
