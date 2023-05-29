import os
import codecs
import time
import keyboard 
import pyautogui
import pygetwindow
import subprocess
import ctypes
import re
import sys
import logging
from PIL import Image
import io
import threading
from time import sleep

sys.path.append('C:/Users/Adrien/Documents/1_Documents/Script Python/craft/PythonApplication1/Class')

import tkinter as tk
from Class.GUI import *
from Class.Image import *
from Class.Log import *
from Class.Craft import *
import mouse
import keyboard

def button1_click():
    print("Bouton 1 cliqué!")

def button2_click():
    print("Bouton 2 cliqué!")
 
# Création de la fenêtre
fenetre = tk.Tk()

# Création des boutons
#button1 = tk.Button(fenetre, text="record", command=test.start_recording )
#button2 = tk.Button(fenetre, text="test", command=test.click_at_positions)

# Placement des boutons dans la fenêtre

from pynput.mouse import Listener
import pynput.mouse

logging.basicConfig( level=logging.DEBUG)

class test():
    def __init__(self):
        self.clicks = []
        self.initialisated = False
    
    #Evenement
    def on_click(self,x,y,button,pressed):
        with lock:
            if str(button) == "Button.left" and pressed:
                coord = {x,y}
                self.clicks.append(coord)
                logging.debug(str(x)+","+str(y)+" clicked")

    def record(self):
        with Listener(on_click=self.on_click) as listener:
            keyboard.wait("a")
            listener.stop()
            intialisated=True


    def restore(self):
        for coord in self.clicks:
            y,x = coord
            duree_pression = 250/1000
            pyautogui.mouseDown(x, y, button='left')
            sleep(duree_pression)
            pyautogui.mouseUp(x, y, button='left')
            sleep(1)
T=test()
T.record()
T.restore()


def clique(coordinates):
    for coord in coordinates:
        y,x = coord
        duree_pression = 250/1000
        pyautogui.mouseDown(x, y, button='left')
        sleep(duree_pression)
        pyautogui.mouseUp(x, y, button='left')
        sleep(1)
print(test)     
#clique(test)




