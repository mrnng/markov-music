import os
import json
import music21 as m21
import numpy as np
import tensorflow.keras as keras

KERN_DATASET_PATH = "deutschl/"
SAVE_DIR = "dataset"
SINGLE_FILE_DATASET_PATH = "file-dataset.txt"
MAPPING_PATH = "mapping.json"
SEQUENCE_LENGTH = 64

ACCEPTABLE_DURATIONS = [
    0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4
]

def load_songs_in_kern(dataset_path):
    songs = []
    # 1. GO THROUGH ALL FILES AND LOAD THEM (music21)
    for path, subdirs, files in os.walk(dataset_path):
        for file in files:
            if file.split(".")[-1] == "krn":
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
    return songs

def has_acceptable_durations(song, acceptable_durations):
    for note in song.flatten().notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True

def transpose(song):
    # 1a. GET KEY FROM SONG IF GIVEN
    # In the kern format, the key signature may be stored
    # at this specific location.
    parts = song.getElementsByClass(m21.stream.Part)
    part_0_measures = parts[0].getElementsByClass(m21.stream.Measure)
    key = part_0_measures[0][4]

    # 1b. ESTIMATE KEY IF NOT GIVEN
    if not isinstance(key, m21.key.Key):
        key = song.analyze("key")

    # 2. GET INTERVAL FOR TRANSPOSITION
    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))

    # 3. TRANSPOSE SONG BY INTERVAL
    transposed_song = song.transpose(interval)

    return transposed_song

def encode_song(song, time_step=0.25):
    # INTEGER -> PITCH (MIDI)
    # "_" -> SUSTAIN (0.25 OR 1/16 note)
    # "r" -> REST
    encoded_song = []

    for event in song.flatten().notesAndRests:
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi
        elif isinstance(event, m21.note.Rest):
            symbol = "r"

        # CONVERT INTO TIME SERIES NOTATION
        steps = int(event.duration.quarterLength / time_step)
        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")
    
    encoded_song = " ".join([str(s) for s in encoded_song])

    return encoded_song

def preprocess(dataset_path):
    # 1. LOAD FOLK SONGS
    print("Loading songs...")
    songs = load_songs_in_kern(dataset_path)
    print(f"{len(songs)} songs loaded.")
    # 2. FILTER OUT SONGS
    for idx, song in enumerate(songs):
        if not has_acceptable_durations(song, ACCEPTABLE_DURATIONS):
            continue
        # 3. TRANSPOSE SONGS TO C/Am
        song = transpose(song)
        # 4. ENCODE SONGS WITH OUR FORMAT
        encoded_song = encode_song(song)
        # 5. SAVE SONGS TO TXT FILE
        save_path = os.path.join(SAVE_DIR, f"formatted-{KERN_DATASET_PATH.split('/')[-1]}-{idx}.txt")
        with open(save_path, "w") as f:
            f.write(encoded_song)

def load(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    return content

def create_single_file_dataset(dataset_path, single_file_dataset_path, sequence_length):
    # 1. LOAD ENCODED SONG AND ADD DELIMITERS
    # I don't understand this part:
    songs = ""
    new_song_delimiter = "/ " * sequence_length
    for path, _, files in os.walk(dataset_path):
        for file in files:
            file_path = os.path.join(path, file)
            song = load(file_path)
            songs += song + " " + new_song_delimiter
    # 2. SAVE THE STRING IN A FILE
    songs = songs[:-1]
    with open(single_file_dataset_path, "w") as f:
        f.write(songs)
    return songs

def create_mapping(songs, mapping_path):
    # 1. DEFINE VOCABULARY
    mapping = {}
    songs = songs.split()
    vocabulary = list(set(songs))

    for idx, symbol in enumerate(vocabulary):
        mapping[symbol] = idx

    # 2. SAVE AS JSON FILE
    with open(mapping_path, "w") as f:
        json.dump(mapping, f, indent=4)

def convert_songs_to_int(songs, mapping_path):
    int_songs = []
    # 1. LOAD THE MAPPING
    with open(mapping_path, "r") as f:
        mapping = json.load(f)
    # 2. MAP SONGS TO INT
    songs = songs.split()
    for symbol in songs:
        int_songs.append(mapping[symbol])

    return int_songs

def generate_training_sequences(sequence_length, single_file_dataset_path, mapping_path):
    # 1. LOAD SONGS AND MAP THEM TO INT
    songs = load(single_file_dataset_path)
    int_songs = convert_songs_to_int(songs, mapping_path)

    # 2. GENERATE THE TRAINING SEQUENCES
    inputs = []
    targets = []

    num_sequences = len(int_songs) - sequence_length
    for i in range(num_sequences):
        inputs.append(int_songs[i:i+sequence_length])
        targets.append(int_songs[i+sequence_length])

    inputs = np.array(inputs)
    targets = np.array(targets)

    return inputs, targets

if __name__ == "__main__":
    preprocess(KERN_DATASET_PATH)
    songs = create_single_file_dataset(SAVE_DIR, SINGLE_FILE_DATASET_PATH, SEQUENCE_LENGTH)
    create_mapping(songs, MAPPING_PATH)
    # inputs, targets = generate_training_sequences(SEQUENCE_LENGTH, SINGLE_FILE_DATASET_PATH, MAPPING_PATH)
    # print(inputs.shape, targets.shape)