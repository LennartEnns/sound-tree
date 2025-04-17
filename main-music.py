from not_main.mainfuncs import run
from not_main.common import *
from not_main.sender.treeSender import TreeLEDSender
from not_main.sender.webSender import WebSender

if __name__ == "__main__":
    # Customize
    run(False, MIN_FREQ_MUSIC, MAX_FREQ_MUSIC, 4096, DIST_MODES.MUSIC, beatDetect=True, senders=[WebSender()])
