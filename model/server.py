import os
from pathlib import Path
import subprocess
import tempfile
import uuid
from flask import Flask, request, redirect, send_file
from werkzeug.utils import secure_filename
from midi2audio import FluidSynth
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

        # in windows using with was locking the temp files (Premission error)
        # fix : create manual temp files
        # Using tempfile.gettempdir() generates paths in the OS temp folder safely.
        temp_dir = tempfile.gettempdir()
        unique_id = uuid.uuid4().hex
        
        input_path = os.path.join(temp_dir, f"input_{unique_id}{extension}")
        output_path = os.path.join(temp_dir, f"output_{unique_id}.mid")
        output_audio = os.path.join(temp_dir, f"output_{unique_id}.wav")

        try:
            file.save(input_path)
        
            # this is the actual processing
            processed_input = process_input(input_path)
            mg = MelodyGenerator()
            seed = processed_input
            melody = mg.generate_melody(seed, 50, SEQUENCE_LENGTH, 0.3)
            mg.save_melody(melody, file_name=output_path)

            soundfont_path = os.path.join(os.path.dirname(__file__), "FluidR3_GM.sf2")

            cmd = [
                "fluidsynth",
                "-ni",                  # No interactive mode
                "-F", output_audio,     # Output WAV file definition FIRST
                "-r", "44100",          # Sample rate definition SECOND
                soundfont_path,         # Soundfont third
                output_path             # Input MIDI file last
            ]

            print(f"Running FluidSynth: {' '.join(cmd)}")

            subprocess.run(cmd , check=True , shell=True)

            # Send the file back to the browser
            return send_file(
                output_audio,
                as_attachment=True,
                download_name="generated.wav",
                mimetype="audio/wav"
            )
            
        except Exception as e:
            print(f"An error occurred during generation: {e}")
            return { "message": "Error generating file." }, 500
            
        finally: 
            for path in [input_path, output_path, output_audio]:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as cleanup_error:
                    print(f"Could not clean up temporary file {path}: {cleanup_error}")
    
    return { "message": "Method not allowed or bad request." }, 400

