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
imagePot = "./Ressources/buffPot.png"
imageBoutonToutReparer = "./Ressources/bouton tout reparer.PNG"
imageBoutonOui = "./Ressources/boutton oui.PNG"
log = "C:/Users/Adrien/Documents/FFLOG"
logging.basicConfig( level=logging.DEBUG)
titre_fenetre = "Final Fantasy XIV" 

def shutdown_computer():
    try:
        subprocess.run(["shutdown", "/s","/f", "/t", "0"], shell=True)
        print("Arrêt de l'ordinateur en cours...")
    except subprocess.CalledProcessError as e:
        print("Une erreur s'est produite lors de l'arrêt de l'ordinateur :", e)

def stop_program(e):
   
    if e.name == 'esc':
        print("Arrêt du programme")
        sys.exit() #Permet de stopper le programme a tout moment en appuyant sur echap

# Attachez la fonction `stop_program` à l'événement de pression de touche
keyboard.on_press(stop_program)

def chemin_document_plus_recent(dossier="C:/Users/Adrien/Documents/FFLOG"):
    fichiers = os.listdir(dossier)
    if not fichiers: #Si le dossier est mauvais
        logging.error("Le dossier log n'est pas valide ")
        return None
    
    chemin_plus_recent = None
    date_plus_recente = None
    
    for fichier in fichiers:
        chemin = os.path.join(dossier, fichier)

        if os.path.isfile(chemin):


            date_modification = os.path.getmtime(chemin)

            #Si le chemin est plus récent on le sauvegarde
            if date_plus_recente is None or date_modification > date_plus_recente:
                date_plus_recente = date_modification
                chemin_plus_recent = chemin

    logging.info("Le fichier FFLOG trouvé est :"+chemin_plus_recent)

    return chemin_plus_recent #Renvoie le fichier le plus récent d'un dossier

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

def verif_buff(command,buff,touche_buff):

    global boutonFab
    #Vérification de l'état de la case config bouffe
    
    if buff.localiser_image():#Est ce que le buff est présent ? 
        
        logging.info("buff Nourriture actif")
        return True
       
    else:

        #On met la fenetre FF14 au premier plan et focus
        hwnd = boutonFab.windows._hWnd
        ctypes.windll.user32.SetForegroundWindow(hwnd)

        if  boutonFab.localiser_image() :

            pyautogui.press('n') #Fermeture de l'ui crafteur
            sleep(5)
            logging.debug("interface crafteur fermée")
        

        pyautogui.press(touche_buff) #On met le buff
        logging.debug("nourriture appuyée")
        sleep(3)

        pyautogui.press('n') #Réouverture de l'interface crafteur
        logging.debug("interface crafteur ouverte")
        sleep(3)

        if boutonFab.localiser_image() : #Si l'interface de craft est présente on valide

            logging.error('refresh Food failed')
            return True

        else:

            #Sinon on tente de l'ouvrir et on reregarde
            pyautogui.press('n') 

            if boutonFab.localiser_image() and buff.localiser_image() :

                logging.error('refresh Food failed')
                return True

            else:

                return False
    
def reparation(touche_repa):
    logging.info("reparation a faire")
    global bouton_tout_reparer
    global bouton_oui
    global boutonFab
    if boutonFab.localiser_image():
        pyautogui.press('n')
    sleep(3)
    pyautogui.press(touche_repa)
    sleep(1)
    if  bouton_tout_reparer.localiser_image():
        logging.debug("bouton oui et tout réparé ok")
        bouton_tout_reparer.clique_droit_image()
        sleep(1)
        if bouton_oui.localiser_image():
            bouton_oui.clique_droit_image()
            sleep(5)
            pyautogui.press(touche_repa)
            sleep(1)
            pyautogui.press('n')
            sleep(1)
            logging.info("equipement réparé")
            return True
        
    logging.debug("bouton oui ou bouton tout reparer non trouvé")
    return False

#Permet de réaliser un affichage en temps réel des données de craft 
def update_status_GUI(): 
    global crafting
    global command
    global config_Craft
    while crafting.get_status() != 99:
        status = crafting.get_status()
        command.update_status(status,config_Craft[status]["text"])
        command.update_duree_restant(crafting.duree_craft_restante())
        sleep(0.5)

        

        
#Programme principal qui a en charge toute la gestion du craft
def grafcet_craft():
    
    #Déclaration Variable globale
    global crafting
    global t
    global command
    global boutonFab
    global bouffe
    global LOGFile
    global pot

    while crafting.get_status()!=99: #On fait la boucle tant que le statut n'est pas arret du programme (99)

        sleep(2)
        logging.info("Boucle Craft en attente")

        while crafting.get_status() > 0 and crafting.get_status() < 10: #on ne fait pas la boucle si le craft n'est pas lancé ou que le craft est pause

             sleep(1)
             logging.debug("boucle de craft ite")

             if int(crafting.craft_restant) >= 1 : #Boucle a faire tant qu'il y a des craft a faire
                
                #Vérification de la nourriture
                if crafting.get_status() ==2:
                    if command.config_bouffe():
                        if verif_buff(command,bouffe,'c'):
                            crafting.next_step()
                            logging.info("Config Nourriture vérifiée")
                        else:
                            crafting.status=0

                    else:
                        crafting.next_step()
                
                        #Vérification de la config pot
                if crafting.get_status() ==3:
                    if command.config_pot():
                        if verif_buff(command,pot,'x'):
                            crafting.next_step()
                            logging.info("Config Pot vérifiée")
                        else:
                            crafting.status=0
                            logging.error("Pas de confirmation POT up")
                    else:
                         crafting.next_step()


                #Lancement du craft
                if crafting.get_status() ==4:
                    if boutonFab.localiser_image() :
                        boutonFab.clique_droit_image()
                        crafting.next_step()
                        logging.info("Bouton fab cliqué")
               
                #Lancement de la macro
                if crafting.get_status() ==5 : 
                    logging.debug("attente confirmation lancement craft")
                    if LOGFile.message_apparait("Vous commencez à fabrique"):
                        crafting.next_step()
                        pyautogui.press('a')
                        logging.info("macro lancé")
                #attente fin
                if crafting.get_status() ==6:
                    logging.debug("attente fin de craft")
                    if LOGFile.message_apparait("Vous fabriquez"):
                        crafting.next_step()

                #Verification equipement non cassé
                if crafting.get_status() ==1:
                    if command.repa_button.get_value():
                        logging.debug("Verification Reparation")
                        if RechercheRepa.message_apparait("cassé",True):
                            if reparation('v'):
                                crafting.next_step()
                            else:
                                logging.error("reparation failed")
                                crafting.change_status(0)
                        else:
                            crafting.next_step()
                    else:
                            crafting.next_step()


                #Réinit et mise a jour données
                if crafting.get_status()==7: 

                    crafting.moins_craft()
                    command.update_craft_restant(int(crafting.craft_restant))
                    logging.info("craft finished")
                    if crafting.get_craft_restant()>0:
                        crafting.change_status(1)
                    else:
                        if command.config_arret():
                            shutdown_computer()
                        else:
                            crafting.change_status(0)
            
####Initialisation des variable
config_Craft ={
   0:{
       "time_out":None,
       "text":"Attente de craft"
     },
   1:{
       "time_out":None,
       "text":"Vérification Repa"
     },
   2:{
       "time_out":None,
       "text":"Vérification Bouffe"
     },
   3:{
       "time_out":None,
       "text":"Vérification Pot"
     },
   4:{
       "time_out":None,
       "text":"Lancement Synthèse"
     },
   5:{
       "time_out":None,
       "text":"Lancement Macro Craft"
     },
   6:{
       "time_out":None,
       "text":"Attente fin craft"
     },
   7:{
       "time_out":None,
       "text":"Reset et relancement"
     },
   10:{
       "time_out":None,
       "text":"Paused"
     },
   99:{
       "time_out":None,
       "text":"Paused"
     }  
  
}


lastFFLOGFile =  chemin_document_plus_recent(log)
LOGFile = logFFXIV(lastFFLOGFile)
RechercheRepa = logFFXIV(lastFFLOGFile)
boutonFab = element_FFXIV(imageFabriquer)
bouffe =element_FFXIV(imageBouffe)
pot = element_FFXIV(imagePot)
bouton_tout_reparer = element_FFXIV( imageBoutonToutReparer)
bouton_oui = element_FFXIV(imageBoutonOui)
crafting = craft(0,config_Craft)
command = FenetreCommande(crafting)


###Multi Threading

#threadFenetre = threading.Thread(target=command.run)
thread_craft = threading.Thread(target=grafcet_craft)
thread_update_data_GUI = threading.Thread(target=update_status_GUI)
thread_craft.start()
thread_update_data_GUI.start()

command.run()
crafting.change_status(99)
logging.debug("prout")