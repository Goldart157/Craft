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

sys.path.append('C:/Users/Adrien/Documents/1_Documents/Script Python/craft/PythonApplication1/Class')

#### Class Custom
from Class.GUI import *
from Class.Image import *
from Class.Log import *
from Class.Craft import *



##### Gestion et lecture des log
#Donnée 
imageFabriquer = "./Ressources/bouton fabriquer.PNG"
imageBuffCl = "./Ressources/BuffCl.PNG"
imageBouffe = "./Ressources/ImageBouffe.PNG"
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
def verif_Bouffe(command,bouffe,boutonFab):
    
    if command.config_bouffe(): #Vérification de l'état de la case config bouffe
        if bouffe.localiser_image():#Est ce que le buff est présent ? 
            crafting.status=2 #Passage étape 2
            logging.info("buff Nourriture actif")
        else:
            clique(500,1000)
            if  boutonFab.localiser_image() :
                pyautogui.press('n') #Fermeture de l'ui crafteur
                sleep(1)
                logging.debug("interface crafteur fermée")
            pyautogui.press('x') #Touche de bouffe
            logging.debug("nourriture appuyée")
            sleep(3)
            pyautogui.press('n') #Réouverture
            logging.debug("interface crafteur ouverte")
            sleep(3)
            if not boutonFab.localiser_image() :
                logging.error('refresh Food failed')
                return True
            else:
                return False
    else:
        return True 




####Mode Craft
def mainCraft():
    while True:
         sleep(2)
         logging.info("Boucle Craft en attente")
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
                        crafting.status = 0
                        break
                #Vérification de la nourriture
                if crafting.status ==1 : 
                    if verif_Bouffe(command,bouffe,boutonFab):
                        crafting.status=2
                        logging.info("Config Nourriture vérifiée")
                    else:
                        crafting.status=0
                        logging.error("Pas de confirmation nourriture up")

                #Lancement du craft
                if crafting.status == 2:
                    if boutonFab.localiser_image() :
                        boutonFab.clique_droit_image()
                        crafting.status=3
                        logging.info("Bouton fab cliqué")
               
                #Lancement de la macro
                if crafting.status == 3:
                    logging.debug("attente confirmation lancement craft")
                    if LOGFile.message_apparait("Vous commencez à fabrique"):
                        crafting.status = 4
                        pyautogui.press('c')
                        logging.info("macro lancé")
                #attente fin
                if crafting.status == 4 :
                    logging.debug("attente fin de craft")
                    if LOGFile.message_apparait("Vous fabriquez"):
                        crafting.status=5

                #Réinit et mise a jour données
                if crafting.status==5: 
                    for i in range(0,5):
                        if t[i]: #Reset de tous les time out par etape 
                            t[i].reset()
                    crafting.moins_craft()
                    command.update_craft_restant(int(crafting.craft_restant))
                    logging.info("craft finished")
                    crafting.status=1
            
####Initialisation des variable
config_Craft ={
    1:{ 
        "time_out":10
    }
}
crafting = craft(0,config_Craft)
lastFFLOGFile =  chemin_document_plus_recent(log)
LOGFile = logFFXIV(lastFFLOGFile)
boutonFab = element_FFXIV(imageFabriquer)
bouffe =element_FFXIV(imageBouffe)
command = FenetreCommande(crafting)


t = [
    None,
    time_out(10),
    time_out(10),
    time_out(10),
    time_out(90),
    None
]

###Multi Threading

#threadFenetre = threading.Thread(target=command.run)
threadCraft = threading.Thread(target=mainCraft)
#threadCraft.start()
#command.run()t=time_out(10)*
crafting.status.statut_change(1)
while True:
    print(crafting.status.return_status())    
    sleep(1)
