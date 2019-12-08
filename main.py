import time, random, datetime, pygame
from threading import Thread
from graphics import Graphics

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
