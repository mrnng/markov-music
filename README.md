# Monophonic Musical Phrase Predictor

This project is a monophonic musical phrase predictor using an LSTM model.

## Overview

The goal of this project is to build a mobile app that can analyze monophonic 
musical sequences and predict or generate the next notes using an LSTM.

The project is developed as part of a course assignment and focuses on:
- Modeling musical sequences
- Using an LSTM for prediction or generation
- Experimenting with different model parameters and representations

## Features

- Input: an audio file in a supported format, converted into note sequences
using Spotify's Basic Pitch.
- Output: predicted or generated musical phrases a playable MP3 file.
- Training using the [ESAC](https://www.esac-data.org/)
[European folk music](https://kern.humdrum.org/cgi-bin/browse?l=essen/europa)
dataset
- Mobile UI with support for audio input and playback

## UML Sequence Diagram

The following is the UML sequence diagram describing the prediction flow.
It shows the user flow from upload and input to prediction and playback.

![UML sequence diagram](./images/uml-sequence.png)

## Tech Stack

- Frontend: React Native
- Backend: Flask
- Training and Modeling: TensorFlow
- Version control: Git + GitHub

## Project Status

Work in progress.

## Team

- Ali Al-Mokdad
- Yehya Hammoud

## License

This project is licensed under the MIT License.
