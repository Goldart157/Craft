import os
import codecs
import time
import keyboard 
import pyautogui
import pygetwindow

import re
import sys
import logging
from PIL import Image
import io
import threading
from time import sleep

#### Class Custom
from ClassLog import *
from ClassGUI import *
from ClassImage import *

##### Gestion et lecture des log
#Donnée 
imageFabriquer = "C:/Users/Adrien/Documents/1_Documents/Script Python/craft/PythonApplication1/Ressources/bouton fabriquer.PNG"
imageBuffCl = "C:/Users/Adrien/Documents/1_Documents/Script Python/craft/PythonApplication1/Ressources/BuffCl.PNG"
imageBouffe = "C:/Users/Adrien\Documents/1_Documents/Script Python/craft/PythonApplication1/Ressources/ImageBouffe.PNG"
log = "C:/Users/Adrien/Documents/FFLOG"
logging.basicConfig( level=logging.DEBUG)
titre_fenetre = "Final Fantasy XIV" 

def stop_program(e):
    if e.name == 'esc':
        print("Arrêt du programme")
        sys.exit() #Permet de stopper le programme a tout moment en appuyant sur echap

# Attachez la fonction `stop_program` à l'événement de pression de touche
keyboard.on_press(stop_program)

def chemin_document_plus_recent(dossier="C:/Users/Adrien/Documents/FFLOG"):
    fichiers = os.listdir(dossier)
    if not fichiers:
        logging.error("Aucun dossier n'as été trouvé le chemin n'est pas pas valide")
        return None
    
    chemin_plus_recent = None
    date_plus_recente = None
    
    for fichier in fichiers:
        chemin = os.path.join(dossier, fichier)
        if os.path.isfile(chemin):
            date_modification = os.path.getmtime(chemin)
            if date_plus_recente is None or date_modification > date_plus_recente:
                date_plus_recente = date_modification
                chemin_plus_recent = chemin
    logging.info("Le fichier FFLOG trouvé est :"+chemin_plus_recent)
    return chemin_plus_recent #Renvoie le fichier le plus récent d'un dossier



###### Fonction de gestion d'image, recherche et clique sur élement du jeu 






###### Fonction diverses
           
def bool_to_str(value):
    if value:
        return "True"
    else:
        return "False"

def obtenir_coordonnees_curseur():
    position = pyautogui.position()
    x = position.x
    y = position.y
    return x, y

def clique(x,y):      
        duree_pression = 250/1000
        pyautogui.mouseDown(x, y, button='left')
        sleep(duree_pression)
        pyautogui.mouseUp(x, y, button='left')
        logging.info("Cliqué sur "+str(x)+" "+str(y))
        
        return None

##### Fonction liées a FF
####Mode Craft
def mainCraft():
    while True:
         sleep(1)
         logging.info("Craft Lancé")
         global crafting
         global t
         global command
         global boutonFab
         global bouffe
         global LOGFile

         while crafting.status!=0 and crafting.status!=10: #on ne fait pas la boucle si le craft n'est pas lancé ou que le craft est pause
            
             if int(crafting.craft_restant) >= 1 :
                if t[crafting.status]:
                    if t[crafting.status].timer():
                        break

                if crafting.status ==1 : #Vérification de la nourriture
                    if command.config_bouffe():
                        if bouffe.localiser_image():
                            crafting.status=2
                        else:
                            clique(500,1000)
                            if  boutonFab.localiser_image() :
                                pyautogui.press('n')
                                sleep(1)
                            pyautogui.press('x')
                            sleep(3)
                            pyautogui.press('n')
                            sleep(3)
                            if not boutonFab.localiser_image() :
                                status=0
                                logging.error('refresh Food failed')
                    else:
                        status=2
        
                if crafting.status == 2:#Lancement du craft
                    if boutonFab.localiser_image() :
                        boutonFab.clique_droit_image()
                        crafting.status=3
                        logging.info("Bouton fab cliqué")
               
        
                if crafting.status == 3:#Lancement de la macro
                    logging.debug("attente confirmation lancement craft")
                    if LOGFile.message_apparait("Vous commencez à fabrique"):
                        crafting.status = 4
                        pyautogui.press('c')
                        logging.info("macro lancé")
        
                if crafting.status == 4 :#attente fin
                    logging.debug("attente fin de craft")
                    if LOGFile.message_apparait("Vous fabriquez"):
                        crafting.status=5
        
                if crafting.status==5: #Réinit et mise a jour données
                    for i in range(0,5):
                        if t[i]:
                            t[i].reset()
                    crafting.moins_craft()
                    command.update_craft_restant(int(crafting.craft_restant))
                    logging.info("craft finished")
                    crafting.status=1
            
####Initialisation des viriable
crafting = craft(0)
lastFFLOGFile =  chemin_document_plus_recent(log)
LOGFile = logFFXIV(lastFFLOGFile)
boutonFab = element_FFXIV(imageFabriquer)
bouffe =element_FFXIV(imageBouffe)
command = FenetreCommande()
t = [
    None,
    time_out(10),
    time_out(10),
    time_out(10),
    time_out(90),
    None
]

###Multi Threading

threadFenetre = threading.Thread(target=command.run)
threadCraft = threading.Thread(target=mainCraft)
threadCraft.start()
command.run()




