from abc import ABC, abstractmethod

class LEDSender(ABC):
    @abstractmethod
    def __init__(self):
        pass
    @abstractmethod
    def close(self):
        pass
    
    @abstractmethod
    def enqueue_frame(self, frame):
        pass