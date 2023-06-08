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

sys.path.append('C:/Users/Adrien/source/repos/Goldart157/Craft/Class')

#### Class Custom
from Class.GUI import *
from Class.Image import *
from Class.Log import *
from Class.Craft import *


logging.basicConfig( level=logging.ERROR)
##### Gestion et lecture des log
#Donnée 


def shutdown_computer():
    try:
        sleep(10)
        subprocess.run(["shutdown", "/s","/f", "/t", "0"], shell=True)
        print("Arrêt de l'ordinateur en cours...")
    except subprocess.CalledProcessError as e:
        print("Une erreur s'est produite lors de l'arrêt de l'ordinateur :", e)

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

#Vérifie si un buff est présent dans le cas contraire lance la séquence pour le faire
def verif_buff(GUI,buff,touche_buff):

    global boutonFab
    global crafting
    #Vérification de l'état de la case config bouffe
    
    if buff.localiser_image():#Est ce que le buff est présent ? 
        
        logging.info("Vérification nourriture: buff  actif")
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

         #Réouverture de l'interface crafteur
        open_Craft()
        logging.debug("interface crafteur ouverte")
        sleep(3)

        if boutonFab.localiser_image() : #Si l'interface de craft est présente on valide

            logging.info('Verif : buff mit placé ')
            return True

        else:

            #Sinon on tente de l'ouvrir et on reregarde
            open_Craft()

            if boutonFab.localiser_image() and buff.localiser_image() :

                logging.info("Vérification nourriture: buff  actif")
                return True

            else:

                logging.error('refresh Food failed')
                return False

#Répare le stuff in game    
def reparation(touche_repa):

    logging.info("reparation a faire")

    global bouton_tout_reparer
    global bouton_oui
    global boutonFab
    global crafting

    sleep(0.5) #Attente que la fenetre repop
    if boutonFab.localiser_image():
        pyautogui.press('n')

    sleep(3)#attente que le crafteur se leve
    pyautogui.press(touche_repa)

    sleep(0.5)#Apparition fenetre

    if  bouton_tout_reparer.localiser_image():

        logging.debug("bouton oui et tout réparé ok")
        bouton_tout_reparer.clique_droit_image()
        sleep(0.5)#Apparition fenetre

        if bouton_oui.localiser_image():

            bouton_oui.clique_droit_image()
            sleep(5)
            pyautogui.press(touche_repa)
            sleep(0.5)#Apparition fenetre
            open_Craft()
            sleep(0.5)#Apparition fenetre
            logging.info("equipement réparé")
            return True
        
    logging.debug("bouton oui ou bouton tout reparer non trouvé")
    return False

#Réouverture fenetre Craft
def open_Craft():
    global crafting
    global boutonFab
    logging.info('ouverture fenetre de craft')

    if not boutonFab.localiser_image():#Si on ne trouve pas le gui on le lance
         keyboard.press('n')
         
    if crafting.HQ.initialized:  
        sleep(0.5)#Apparition fenetre
        crafting.HQ.restore()
        sleep(0.5)#Apparition fenetre

#THREAD : Permet de réaliser un affichage en temps réel des données de craft 
def update_status_GUI(): 
    global crafting
    global GUI
    global config_Craft

    while crafting.get_status() != 99:
        status = crafting.get_status()
        try:
            GUI.update_status(status,config_Craft[status]["text"])
        except:
            GUI.update_status(status,"No Label")
        GUI.update_duree_restant(crafting.duree_craft_restante())
        #GUI.label_Duree_restant.config(text=str(crafting.need_repair))
        sleep(0.5)

#THREAD : Gestion des evenement
def event_checker():

    global lastFFLOGFile
    global crafting

    LOGRepa = logFFXIV(lastFFLOGFile)
    LOGEchoue = logFFXIV(lastFFLOGFile)
    
    while crafting.get_status() != 99:
        sleep(0.2)#Cadencement
        if LOGEchoue.message_apparait_depuis_x_seconde("échoué"):
            crafting.change_status(95)

        if LOGRepa.message_apparait_depuis_x_seconde("cassé") and crafting.get_status() >0 :
            crafting.need_repair = True

        
#Programme principal qui a en charge toute la gestion du craft
def grafcet_craft():
    
    #Déclaration Variable globale
    global crafting
    global t
    global GUI
    global boutonFab
    global bouffe
    global LOGFile
    global pot

    while crafting.get_status()!=99: #On fait la boucle tant que le statut n'est pas arret du programme (99)

        sleep(1)
        logging.info("Boucle Craft en attente")

        while crafting.get_status() > 0 and crafting.get_status() < 10: #on ne fait pas la boucle si le craft n'est pas lancé ou que le craft est pause

             sleep(1)
             logging.debug("boucle de craft ite")

             #Grafcet du programme
             if int(crafting.craft_restant) > 0 : 

                #Verification equipement non cassé
                if crafting.get_status() ==1:
                    if GUI.repa_button.get_value():#####Le déclencheur de réparation doit être refait
                        logging.info("Verification Reparation")


                        if crafting.need_repair:#Condition géré sur la fonction d'évènement

                            if reparation('v'):
                                crafting.need_repair = False
                                crafting.next_step()

                            else:
                                logging.error("reparation failed")
                                crafting.change_status(97)
                        else:
                            crafting.next_step()
                    else:
                            crafting.next_step()

                #Vérification de la nourriture
                if crafting.get_status() ==2:
                    if GUI.config_bouffe():
                        if verif_buff(GUI,bouffe,'c'):
                            crafting.next_step()
                            logging.info("Config Nourriture vérifiée")
                        else:
                            crafting.status=0

                    else:
                        crafting.next_step()
                
                #Vérification de la config pot
                if crafting.get_status() ==3:
                    if GUI.config_pot():
                        if verif_buff(GUI,pot,'x'):
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
                   
                    if LOGFile.message_apparait("Vous commencez à fabrique"):
                        crafting.next_step()
                        pyautogui.press('a')
                        logging.info("macro lancé")

                #attente fin
                if crafting.get_status() ==6:
                    logging.debug("attente fin de craft")
                    if LOGFile.message_apparait("Vous fabriquez"):
                        logging.info("Fin de craft ok")
                        crafting.next_step()

                #Réinit et mise a jour données
                if crafting.get_status()==7: 

                    crafting.moins_craft()
                    GUI.update_craft_restant(int(crafting.craft_restant))
                    logging.info("craft finished")
                    if crafting.get_craft_restant()>0:
                        crafting.change_status(1)
                        logging.info("next craft")
                    else:
                        logging.info("fini")
                        crafting.change_status(96)
        
        #Appel de la fonction enregistrer HQ
        if crafting.get_status()==90:
            crafting.HQ.record()
            crafting.change_status(0)
        #test
        if crafting.get_status()==91:
            open_Craft()
            crafting.change_status(0)

        #Choix fin d'execution
        if crafting.get_status() ==96:
            if GUI.config_arret():
                crafting.change_status(99)
            else:
                crafting.change_status(0)


        #Gestion d'erreur
        if crafting.get_status()==97:
            logging.error("erreur levée")
            #crafting.change_status(0)
            sleep(300)
            crafting.change_status(96)

        #Gestion du time out
        if crafting.get_status()==98:  
   
            logging.error("time out sur l'étape : "+str(crafting.get_status()))
            i=0
            while i<300 and crafting.get_status()==98:
                i=i+1
                sleep(1)
            crafting.change_status(96)            #crafting.change_status(99)

        #Fin de programme
        if crafting.get_status()==99:
            if GUI.config_arret():
                shutdown_computer()

            
####Initialisation des variable
config_Craft ={
   0:{
       "time_out":None,
       "text":"Attente de craft"
     },
   1:{
       "time_out":40,
       "text":"Vérification Repa"
     },
   2:{
       "time_out":40,
       "text":"Vérification Bouffe"
     },
   3:{
       "time_out":40,
       "text":"Vérification Pot"
     },
   4:{
       "time_out":20,
       "text":"Lancement Synthèse"
     },
   5:{
       "time_out":20,
       "text":"Lancement Macro Craft"
     },
   6:{
       "time_out":200,
       "text":"Attente fin craft"
     },
   7:{
       "time_out":10,
       "text":"Reset et relancement"
     },
   10:{
       "time_out":None,
       "text":"Paused"
     },
   90:{
       "time_out":None,
       "text":"Config HQ - cliquez puis s"
    },
   95:{
       "time_out":None,
       "text":"craft échoué détecté"
   },
   97:{
       "time_out":None,
       "text":"Erreur"
    },
   98:{
       "time_out":None,
       "text":"time Out"
     },
   99:{
       "time_out":None,
       "text":"Fin de programme"
     }  
  
}

#Lien vers les fichiers
imageFabriquer = "./Ressources/bouton fabriquer.PNG"
imageBuffCl = "./Ressources/BuffCl.PNG"
imageBouffe = "./Ressources/ImageBouffe.PNG"
imagePot = "./Ressources/buffPot.png"
imageBoutonToutReparer = "./Ressources/bouton tout reparer.PNG"
imageBoutonOui = "./Ressources/boutton oui.PNG"
log = "C:/Users/Adrien/Documents/FFLOG"
titre_fenetre = "Final Fantasy XIV" 

#Initialisation
lastFFLOGFile =  chemin_document_plus_recent(log)
LOGFile = logFFXIV(lastFFLOGFile)
boutonFab = element_FFXIV(imageFabriquer)
bouffe =element_FFXIV(imageBouffe)
pot = element_FFXIV(imagePot)
bouton_tout_reparer = element_FFXIV( imageBoutonToutReparer)
bouton_oui = element_FFXIV(imageBoutonOui)
crafting = craft(0,config_Craft)
GUI = FenetreCommande(crafting)


###Multi Threading

#thread Grafcet craft
thread_craft = threading.Thread(target=grafcet_craft)
thread_craft.start()

#Thread GUI
thread_update_data_GUI = threading.Thread(target=update_status_GUI)
thread_update_data_GUI.start()


#Thread evenement
thread_event = threading.Thread(target=event_checker)
thread_event.start()

GUI.run()
crafting.change_status(99)
logging.debug("prout")