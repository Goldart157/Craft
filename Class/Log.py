from datetime import datetime, time,timedelta
from time import sleep
import re
import logging
import os

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

class logFFXIV:

    def __init__(self,fichier):
        self.fichier = fichier
        self.heure_message = datetime(1994,12,13,0,0,0)
        self.message = None

    def derniere_ligne_filtree(self,filtre,sans_validation=False): #Renvoie la dernière du fichier spécifi contenant le filtre
        with open(self.fichier, 'r', encoding='utf-8') as f:
            lignes = f.readlines()
            if not sans_validation:
                lignes = lignes[-100:]  # Obtenir les 100 dernières lignes du fichier
            else:
                lignes = lignes[-300:]
            for ligne in reversed(lignes):
                ligne = ligne.strip()
            
                if filtre in ligne:
                    #Si il y a un résultat on compare son heure avec l'heure du message précédent pour le valider           
                    temp_heure_message = self._extraire_heure(ligne) 
                    if not sans_validation:
                        if  temp_heure_message > self.heure_message:
                            self.heure_message = temp_heure_message
                            self.message = ligne #On enregistre le message dans l'element
                            logging.debug("Trouvé ligne :"+ligne)
                            return self.message 
                        else: 
                            logging.debug("heure message actuel < a h dernier message lu: None returned")
                    else:
                        if datetime.now() - temp_heure_message > timedelta(minutes=2):
                            self.message = ligne #On enregistre le message dans l'element
                            logging.debug("Trouvé ligne :"+ligne)
                            return self.message 
        return None

    def _extraire_heure(self,message):
        #Decode le message de log et renvoie l'heure de celui-ci
        pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}).*\|"
        match = re.search(pattern, message)
        if match:
            heure_string = match.group(1)
            heure_obj = datetime.strptime(heure_string, "%Y-%m-%dT%H:%M:%S")
            logging.debug("heure extraite du message :"+str(heure_obj))
            return heure_obj
        else:
            logging.debug("Aucune heure trouvée dans le message")
            return None
    
    def message_apparait (self, filtre,sans_validation=False):
        temp = self.derniere_ligne_filtree(filtre,sans_validation=sans_validation)
        if temp is not None:
            return True
        else: 
            return False

    def message_apparait_depuis_x_seconde(self,filtre,x=10):
        if self.message_apparait(filtre):
            delta = timedelta (seconds=x)
            now =   datetime.now()
            temp = self.heure_message
            diff = now -temp
            if diff < delta :
                return True
            else: 
                return False

class craft:
    def __init__(self,craft):
        self.craft = craft
        self.craft_restant = int(craft)
        self.status = 0
    def moins_craft(self):
        self.craft_restant = self.craft_restant-1

    def get_craft_restant(self):
        return self.craft_restant
            

