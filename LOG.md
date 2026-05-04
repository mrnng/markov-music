# A log for decisions we make and ideas we have

## Descripion

We decided to create this log to keep track of any problems we face,
important decisions we make with justification, and any ideas we have.

## The Log

[04/02/2026 - 10:45] -AA  
Created the log.

[04/02/2026 - 10:53] -AA  
There are some library conflicts between Basic Pitch and TensorFlow.  
To resolve this, I used a pyenv with Python 3.11.14, and installed Basic Pitch
with TensorFlow: `pip install basic-pitch[tf]`  
The versions used are: Basic Pitch 0.4.0, TensorFlow 2.15.0.post1.

Also, to be able to play WAV files on Linux Mint, I needed to convert to 16-bit
samples: `ffmpeg -i input.wav -acodec pcm_s16le -ar 44100 -ac 2 output.wav`

[07/02/2026 - 20:13] -AA  
To run a test, run this from the backend folder:
`python -m tests.test_file`

If we try running things from the tests or the processing folder, Python will
see it as the top-level directory and will not understand any references to
other folders, even if defined as packages.

[07/02/2026 - 20:24] -AA  
MIDI instruments have "program numbers" assigned by the General MIDI standard.
This is what instrument.program returns in a PrettyMIDI object.

[09/02/2026 - 17:30]YH
react native demo barebones used expo command to run npx expo start
used expo-av for audio

[15/02/2026 - 12:37] -AA
Sometimes, Basic Pitch picks up on octaves that aren't there in the recording,
so I had to filter them out.

[15/02/2026 - 19:46] -AA
Backend works. To test it, run
`curl -X POST http://localhost:5000/generate -F "file=@piano-recording.m4a" -o "generated.mid"`
on Linux. It should create and save a generated.mid file which works as expected.
To run the server, use `flask --app main run` from the /backend folder.

While the as_attachment=True forces the browser to download the file, it might
not be automatic on React Native.

[21/02/2026 - 10:54] -AA
EXTREMELY IMPORTANT: do NOT update setuptools, as some packages use a deprecated
feature. Use version 69.5.1 at most.
When installing packages with pip, Python will create a build isolation environment
and then mess up the setuptools again, so run the following command instead:
`python -m pip install --no-build-isolation packagename`

[22/02/2026 - 10:17] -AA
I found a dataset in the form of TFRecords. They are sequences of notes,
with an encoding where the numbers 128 and 129 are possibly used for rest
and sustain. I need to convert this and the audio input into a common format
to be decided.

[22/02/2026 - 10:56] -AA
The notes in the dataset are on a 16th note grid, and we have 64 "events"
per entry, so that's a 4-bar melody dataset.

The format we're using is between MIDI and this dataset, so it contains the tempo
but then quantizes notes and rests into 16th steps.

[04/05/2026 - 10:11] -AA
The Markov chain model is insufficient to recognize and produce musicality.
For this reason, we have begun the migration to an RNN-LSTM architecture.