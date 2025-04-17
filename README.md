# Sound Tree
Your Audio Visualizer For Next Christmas.

## Features
### Audio Spectrum Visualization
There are 3 main modes for adjusting the visualization to different kinds of audio:
- MUSIC: Distributes frequencies logarithmically (lower frequencies take up more space) and changes LED colors when a beat is detected.
- HUMAN: Similar distribution to MUSIC, but the frequency range is fit to the human voice.
- LINEAR: Linear distribution of frequencies.

Enable [**Normalization Level Tracking**](#customization) to track the maximum loudness over time and use it for normalization.
This enables a more dynamic visual experience.

### Karaoke Game
In this game, 2 to 7 players compete to imitate each other's melodies. The tree rates them after every imitation and at the end of a round.

#### Gameplay
Start the *main-karaoke* script.
After the LEDs have stopped blinking, you specifiy the number of players:

Clap once for every player and wait for the tree to finish blinking in the color of the added player. Wait a few seconds when you're done.

For every round, each player will be the original singer once.
The LEDs show a short animation in the color of a player to indicate that the player should start singing.

After singing, wait a few seconds for the game to continue.
Imitators will be rated with a score which is shown as a height on the LED strip.

At the end of a round, the average score of each player is shown, starting with the last place.

#### Karaoke Customization
Set the MAX_ERROR_SEMITONES constant in *mainfuncsKaraoke.py* to specify how high the average semitones deviation of a melody should be in order to caused a score of 0.

### Customization
You can pass different parameters to the *run* functions invoked in the *main* scripts. Normally, these include:
- Normalization Level Tracking (Yes/No)
- Min and Max Frequency to visualize
- Number of frequency points to compute (more = smoother)
- Distribution Mode (see [here](#audio-spectrum-visualization))

## Basic Setup
For these setups to work, you need to have the required things listed under [Requirements](#requirements).

Also, you should adjust the *USB_SERIAL_PORT* constant in **commons.py** to match your actual port that the MCU is connected to.

### Real Tree with LED Strip
Attach the LED strip to the tree (*optional*), connect the LED strip to the Arduino Uno and the Arduino Uno to your device.

### Virtual Tree
Just launch the web frontend + one of the main Python scripts and you're good to go!

## Requirements
### Hardware For The Real Tree Setup
A Tree (*optional*), an LED strip with individually controllable segments, an Arduino Uno MCU for running the LED controller.

### Python Environment
Easy setup:

macos: brew install portaudio

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

#### Python Modules
numpy, scipy, pyaudio, clapDetector

#### Additional Modules For Real Tree Setup:
pyserial

#### Additional Modules For Virtual Tree Setup:
websockets

#### Additional Modules For Python Plotting:
matplotlib

### Audio Routing
You'll need this if you want to capture system audio, or route an audio stream to multiple outputs.

**Example**: Route System Audio to the MCU **and** to a speaker.

#### For macOS
- BlackHole (2ch) --> Select as input **and** as output to route system audio to the MCU.
- Audio MIDI setup --> For routing an input to **multiple** outputs (see example above).

#### For Other OS
Use other software solutions if necessary.
