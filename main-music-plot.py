from soundTree.engine.plotEngine import PlotEngine
from soundTree.common import *

if __name__ == "__main__":
    # Customize
    engine = PlotEngine(4096, MIN_FREQ_MUSIC, MAX_FREQ_MUSIC, trackMaximumLevel=False)
    engine.run()
