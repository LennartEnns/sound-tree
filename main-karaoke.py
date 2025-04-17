from not_main.common import *
from not_main.mainfuncsKaraoke import run
from not_main.sender.treeSender import TreeLEDSender
from not_main.sender.webSender import WebSender

# Customize
run(4096, [TreeLEDSender()])
