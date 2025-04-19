from soundTree.engine.plotEngine import PlotEngine
from soundTree.common import *

if __name__ == "__main__":
    # Customize
    engine = PlotEngine(4096, MIN_FREQ_HUMAN, MAX_FREQ_HUMAN, False)
    engine.run()
