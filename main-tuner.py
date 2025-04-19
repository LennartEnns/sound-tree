from soundTree.engine.tunerEngine import TunerEngine
from soundTree.common import *
from soundTree.sender.treeSender import TreeLEDSender
from soundTree.sender.webSender import WebSender

if __name__ == "__main__":
    # Customize
    engine = TunerEngine(100, 700, senders=[TreeLEDSender()])
    engine.run()
