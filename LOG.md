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