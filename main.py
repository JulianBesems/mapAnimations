import time, random, datetime, pygame
from threading import Thread
from mapGraphics import Graphics
from classifyPlaces2 import LocationGrid, Cell

class Main:
    def __init__(self):
        self.time = datetime.datetime.now()

    def run(self):
        graphics = Graphics()
        graphics.display()
        while True:
            pass

main = Main()
main.run()
