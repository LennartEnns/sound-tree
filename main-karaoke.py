from soundTree.common import *
from soundTree.engine.karaokeEngine import KaraokeEngine
from soundTree.sender.treeSender import TreeLEDSender
from soundTree.sender.webSender import WebSender

if __name__ == "__main__":
    # Customize
    engine = KaraokeEngine(4096, MIN_FREQ_HUMAN, MAX_FREQ_HUMAN, senders=[WebSender()])
    engine.run()
