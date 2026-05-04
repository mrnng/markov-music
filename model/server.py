import os
from tempfile import NamedTemporaryFile
from flask import Flask, request, redirect, send_file
from werkzeug.utils import secure_filename
from model.melody_generator import MelodyGenerator
from model.input_processing import process_input
from model.data_processing import SEQUENCE_LENGTH

app = Flask(__name__)

ALLOWED_EXTENSIONS = ["mp3", "m4a"]
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/generate", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            print("No file uploaded.")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == '':
            print("No file uploaded.")
            return redirect(request.url)
        if not file or not allowed_file(file.filename):
            print("Error, wrong file type/content.")
            return redirect(request.url)
        
        # this is recommended by the Flask docs
        filename = secure_filename(file.filename)
        extension = "." + filename.rsplit(".", 1)[1].lower()
        
        # tempfiles prevent the processed files from being saved locally
        with NamedTemporaryFile(mode="w+b", suffix=extension) as input_path, \
            NamedTemporaryFile(mode="w+b", suffix=".mid") as output_path:

            file.save(input_path.name)
        
            # this is the actual processing
            processed_input = process_input(input_path.name)
            mg = MelodyGenerator()
            seed = processed_input["encoded_song"]
            melody = mg.generate_melody(seed, 500, SEQUENCE_LENGTH, 0.3)
            mg.save_melody(melody, file_name=output_path.name)

            # as_attachment=True forces the browser to download the file
            return send_file(
                output_path.name,
                as_attachment=True,
                download_name="generated.mid",
                mimetype="audio/midi"
            )
    
    return { "message": "Error generating file." }
