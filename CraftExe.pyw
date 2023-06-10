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



####### Class Custom #######
from Class.GUI import *
from Class.Image import *
from Class.Log import *
from Class.Craft import *


logging.basicConfig( level=logging.INFO)
##### Gestion et lecture des log
#Donnée 

sys.path.append('C:/Users/Adrien/source/repos/Goldart157/Craft/Class')
logging.basicConfig( level=logging.ERROR)

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

def shutdown_computer():
    try:
        sleep(10)
        subprocess.run(["shutdown", "/s","/f", "/t", "0"], shell=True)
        print("Arrêt de l'ordinateur en cours...")
    except subprocess.CalledProcessError as e:
        print("Une erreur s'est produite lors de l'arrêt de l'ordinateur :", e)

####### Fonction liées a FF #######

## Vérifie si un buff est présent dans le cas contraire lance la séquence pour le faire
def verif_buff(GUI,buff,touche_buff):

    global boutonFab
    global crafting
    #Vérification de l'état de la case config bouffe
    
    if buff.localiser_image():#Est ce que le buff est présent ? 
        
        logging.info("Verif buff: buff  actif")
        return True
       
    else:

        #On met la fenetre FF14 au premier plan et focus
        hwnd = boutonFab.windows._hWnd
        ctypes.windll.user32.SetForegroundWindow(hwnd)

        if not close_craft():
            return False
        

        pyautogui.press(touche_buff) #On met le buff
        logging.debug("nourriture appuyée")
        sleep(3)

         #Réouverture de l'interface crafteur
        open_craft()
        logging.debug("interface crafteur ouverte")
        sleep(3)

        if boutonFab.localiser_image() : #Si l'interface de craft est présente on valide
            crafting.need_waiting = True
            logging.info('Verif : buff mit placé ')
            return True

        else:

            #Sinon on tente de l'ouvrir et on reregarde
            open_craft()

            if boutonFab.localiser_image() and buff.localiser_image() :
                crafting.need_waiting = True
                logging.info("Vérification nourriture: buff  actif")
                return True

            else:

                logging.error('Verif : refresh buff failed')
                return False

## Répare le stuff in game    
def reparation(touche_repa):

    logging.info("reparation a faire")

    global bouton_tout_reparer
    global bouton_oui_rep
    global boutonFab
    global crafting

    if not close_craft():
        return False

    pyautogui.press(touche_repa)

    sleep(0.5)#Apparition fenetre

    if  bouton_tout_reparer.localiser_image():

        logging.debug("bouton oui et tout réparé ok")
        bouton_tout_reparer.clique_droit_image()
        sleep(0.5)#Apparition fenetre

        if bouton_oui_rep.localiser_image():

            bouton_oui_rep.clique_droit_image()
            sleep(5)
            pyautogui.press(touche_repa)
            sleep(0.5)#Apparition fenetre
            open_craft()
            sleep(0.5)#Apparition fenetre
            logging.info("equipement réparé")
            crafting.need_waiting = True
            return True
        
    logging.debug("Réparation: bouton oui ou bouton \" tout reparer \" non trouvé")
    return False

## Réouverture fenetre Craft
def open_craft():
    global crafting
    global boutonFab
    logging.info('open_craft: ouverture fenetre de craft')

    if not boutonFab.localiser_image():#Si on ne trouve pas le gui on le lance
        keyboard.press('n')
         
    if crafting.HQ.initialized:  
        sleep(0.5)#Apparition fenetre
        crafting.HQ.restore()
        sleep(0.5)#Apparition fenetre

## Fermeture fenetre craft
def close_craft():
    global boutonFab
    sleep(1) #Attente repop fenetre craft

    if boutonFab.localiser_image():
        pyautogui.press('n')
        #Attente que le crafteur se leve
        sleep(3)
        if not boutonFab.localiser_image():
           logging.debug("Close Craft:interface fermée")
           return True
        else:
           logging.debug("Close Craft:interface non fermée")
           return False
    else:
        return True

## Gere la matérialisation des élément symbiosé
def symbiose(touche_symb='<'):

    global symb100
    global bouton_oui_symb


    close_craft()

    #Ouverture de la fenetre de symbiose
    pyautogui.press(touche_symb)
    logging.debug("Symbiose:Ouverture fenetre symbiose")

    while symb100.localiser_image():
        #On verifie si il y a des element a matérialiser
        if symb100.localiser_image():

            symb100.clique_droit_image()
            sleep(1)

            #Confirmation symbiose
            if bouton_oui_symb.localiser_image():
                bouton_oui_symb.clique_droit_image()
            else:
                return False

        sleep(3)

    return  open_craft()

####### Gestion UI et évenement #######

## THREAD : Permet de réaliser un affichage en temps réel des données de craft 
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

## THREAD : Gestion des evenement
def event_checker():

    global lastFFLOGFile
    global crafting

    LOGRepa = logFFXIV(lastFFLOGFile)
    LOGEchoue = logFFXIV(lastFFLOGFile)
    LOGSymp = logFFXIV(lastFFLOGFile)

    while crafting.get_status() != 99:
        sleep(0.2)#Cadencement
        if LOGEchoue.message_apparait_depuis_x_seconde("échoué"):
            crafting.change_status(95)
        
        current_status = crafting.get_status()
        validation_verif =  (current_status < 10 and current_status > 0) or current_status == 91

        if LOGRepa.message_apparait_depuis_x_seconde("cassé") and validation_verif : 
            crafting.need_repair = True  

        if LOGSymp.message_apparait_depuis_x_seconde("symbiose") and  validation_verif :
            crafting.need_material = True
            crafting.change_status(10)

####### Programme principal qui a en charge toute la gestion du craft #######
def grafcet_craft():
    
    ## Déclaration Variable globale
    global crafting
    global t
    global GUI
    global boutonFab
    global bouffe
    global LOGFile
    global pot
    

    while crafting.get_status()!=99: # On fait la boucle tant que le statut n'est pas arret du programme (99)
        crafting.need_waiting = True # On attend que le crafteur se prépare 
        sleep(1)
        logging.info("Boucle Craft en attente")
        
        #### Grafcet du programme EN MODE CRAFT #####
        while crafting.get_status() > 0 and crafting.get_status() < 10: # on ne fait pas la boucle si le craft n'est pas lancé ou que le craft est pause

             sleep(1)
             logging.debug("CraftExe: Crafting en cours")

             if int(crafting.craft_restant) > 0 : 

                ## Verification equipement non cassé
                if crafting.get_status() == 1:
                    if GUI.repa_button.get_value():#####Le déclencheur de réparation doit être refait
                        logging.info("Craft Exe : Vérification Réparation")
                        if crafting.need_repair:#Condition géré sur la fonction d'évènement

                            if reparation('v'):
                                crafting.need_repair = False
                                crafting.next_step()

                            else:
                                logging.error("CraftExe: reparation failed")
                                crafting.change_status(97)
                        else:
                            crafting.next_step()
                    else:
                            crafting.next_step()

                ## Verification besoin materialisation
                if crafting.get_status() == 2:
                    if GUI.materialize_button.get_value():#####Le déclencheur à refaire
                        logging.info("Craft Exe : Vérification Matérialisation")
                        if crafting.need_material:#Condition géré sur la fonction d'évènement

                            if symbiose('v'):
                                crafting.need_material = False
                                crafting.next_step()

                            else:
                                logging.error("CraftExe: materialisation failed")
                                crafting.change_status(97)
                        else:
                            crafting.next_step()
                    else:
                            crafting.next_step()

                ## Vérification de la nourriture
                if crafting.get_status() == 3:
                    if GUI.config_bouffe():
                        logging.info("CraftExe: Vérfication nouriture")
                        if verif_buff(GUI,bouffe,'c'):
                            crafting.next_step()
                           
                        else:
                            crafting.change_status(97)
                            
                    else:
                        crafting.next_step()
                
                ## Vérification de la config pot
                if crafting.get_status() == 4:
                    if GUI.config_pot():
                        logging.info("CraftExe : Vérification Pot")
                        if verif_buff(GUI,pot,'x'):
                            crafting.next_step()
                            
                        else:
                            crafting.change_status(97)
                            
                    else:
                         crafting.next_step()

                ## Lancement du craft
                if crafting.get_status() == 5:
                    if boutonFab.localiser_image() :
                        boutonFab.clique_droit_image()
                        logging.info("Bouton fab cliqué")
                        crafting.next_step()
                     
                ## Lancement de la macro
                if crafting.get_status() == 6: 
                   
                    if LOGFile.message_apparait("Vous commencez à fabrique"):

                        if crafting.need_waiting:
                            crafting.need_waiting = False
                            sleep(2)
                        pyautogui.press('a')
                        logging.info("macro lancé")
                        crafting.next_step()

                ## attente fin
                if crafting.get_status() == 7:
                    logging.debug("attente fin de craft")
                    if LOGFile.message_apparait("Vous fabriquez"):
                        logging.info("CraftExe : Fin de craft ok")
                        crafting.next_step()

                ## Réinit et mise a jour données
                if crafting.get_status() == 8: 

                    crafting.moins_craft()
                    GUI.update_craft_restant(int(crafting.craft_restant))
                    logging.info("CraftExe : craft finished")
                    if crafting.get_craft_restant()>0:
                        logging.info("CraftExe : next craft")
                        crafting.change_status(1)
                    else:
                        logging.info("CraftExe : fini")
                        crafting.change_status(96)
        
        
        #### Gestion d'element hors craft
                        
        ## Appel de la fonction enregistrer HQ
        if crafting.get_status()==90:
            crafting.HQ.record()
            crafting.change_status(0)

        ## zone de test
        if crafting.get_status()==91:
            print(str(symb100.localiser_image()))
            symbiose()
            #reparation('v')
            #open_craft()
            crafting.change_status(0)

        ## Choix fin d'execution
        if crafting.get_status() ==96:
            if GUI.config_arret():
                crafting.change_status(99)
            else:
                crafting.change_status(0)


        ## Gestion d'erreur
        if crafting.get_status()==97:
            logging.error("erreur levée")
            #crafting.change_status(0)
            sleep(300)
            crafting.change_status(96)

        ## Gestion du time out
        if crafting.get_status()==98:  
   
            logging.error("time out sur l'étape : "+str(crafting.get_status()))
            i=0
            while i<300 and crafting.get_status()==98:
                i=i+1
                sleep(1)
            crafting.change_status(96)            #crafting.change_status(99)

        ## Fin de programme
        if crafting.get_status()==99:
            if GUI.config_arret():
                shutdown_computer() 
                
####### Initialisation des variable #######
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
       "time_out":60,
       "text":"Vérification Symbiose"
     },
   3:{
       "time_out":40,
       "text":"Vérification Bouffe"
     },
   4:{
       "time_out":40,
       "text":"Vérification Pot"
     },
   5:{
       "time_out":20,
       "text":"Lancement Synthèse"
     },
   6:{
       "time_out":20,
       "text":"Lancement Macro Craft"
     },
   7:{
       "time_out":200,
       "text":"Attente fin craft"
     },
   8:{
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

####### Lien vers les fichiers #######
imageFabriquer = "./Ressources/bouton fabriquer.PNG"
imageBuffCl = "./Ressources/BuffCl.PNG"
imageBouffe = "./Ressources/ImageBouffe.PNG"
imagePot = "./Ressources/buffPot.png"
imageBoutonToutReparer = "./Ressources/bouton tout reparer.PNG"
imageBoutonOuiRep = "./Ressources/boutton oui.PNG"
imageSymb = "./Ressources/Symbiose100.PNG"
imageBoutonOuiRep = "./Ressources/boutton oui.PNG"
imageBoutonOuiSymb= "./Ressources/ouisymb.PNG"
log = "C:/Users/Adrien/Documents/FFLOG"
titre_fenetre = "Final Fantasy XIV" 

####### Initialisation #######
lastFFLOGFile =  chemin_document_plus_recent(log)
LOGFile = logFFXIV(lastFFLOGFile)
boutonFab = element_FFXIV(imageFabriquer)
bouffe =element_FFXIV(imageBouffe)
pot = element_FFXIV(imagePot)
bouton_tout_reparer = element_FFXIV( imageBoutonToutReparer)
bouton_oui_rep = element_FFXIV(imageBoutonOuiRep)
bouton_oui_symb = element_FFXIV(imageBoutonOuiSymb)
crafting = craft(0,config_Craft)
GUI = FenetreCommande(crafting)
symb100=element_FFXIV(imageSymb)

####### Multi Threading #######

## thread Grafcet craft
thread_craft = threading.Thread(target=grafcet_craft)
thread_craft.start()

## Thread GUI
thread_update_data_GUI = threading.Thread(target=update_status_GUI)
thread_update_data_GUI.start()

## Thread evenement
thread_event = threading.Thread(target=event_checker)
thread_event.start()

GUI.run()
crafting.change_status(99)
logging.debug("prout")