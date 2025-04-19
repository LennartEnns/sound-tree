from soundTree.engine.ledVisualizerEngine import LEDVisualizerEngine
from soundTree.common import *
from soundTree.sender.treeSender import TreeLEDSender
from soundTree.sender.webSender import WebSender

if __name__ == "__main__":
    # Customize
    engine = LEDVisualizerEngine(2048, MIN_FREQ_HUMAN, MAX_FREQ_HUMAN, DIST_MODES.HUMAN, beatDetect=False, trackMaximumLevel=False, senders=[TreeLEDSender()])
    engine.run()
