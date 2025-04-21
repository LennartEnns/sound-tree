from soundTree.engine.ledVisualizerEngine import LEDVisualizerEngine
from soundTree.common import *
from soundTree.sender.treeSender import TreeLEDSender
from soundTree.sender.webSender import WebSender

if __name__ == "__main__":
    # Customize
    engine = LEDVisualizerEngine(2048, MIN_FREQ_MUSIC, MAX_FREQ_MUSIC, enhance_peaks=True, distMode=DIST_MODES.MUSIC, beatDetect=True, trackMaximumLevel=False, senders=[TreeLEDSender()])
    engine.run()
