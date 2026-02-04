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