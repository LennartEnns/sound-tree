from not_main.mainfuncs import run
from not_main.common import *
from not_main.sender.treeSender import TreeLEDSender
from not_main.sender.webSender import WebSender

if __name__ == "__main__":
    # Customize
    run(False, MIN_FREQ_HUMAN, MAX_FREQ_HUMAN, 2048, DIST_MODES.HUMAN, beatDetect=False, senders=[TreeLEDSender()])
