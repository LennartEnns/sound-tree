from not_main.ledController import LEDController

ledController = LEDController()
ledController.show_values_increasing([(0.2, (255, 0, 0)), (0.5, (0, 255, 0)), (0.9, (0, 0, 255))])
