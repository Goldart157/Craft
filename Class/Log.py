from datetime import datetime, time,timedelta
from time import sleep
import re
import logging

class logFFXIV:

    def __init__(self,fichier):
        self.fichier = fichier
        self.heure_message = datetime(1994,12,13,0,0,0)
        self.message = None
        self.heure_message_prev = datetime(1994,12,13,0,0,0)

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
                            logging.info("Trouvé ligne :"+ligne)
                            return self.message 
                        else: 
                            logging.debug("heure message actuel < a h dernier message lu: None returned")
                    else:
                        if datetime.now() - temp_heure_message > timedelta(minutes=2):
                            self.message = ligne #On enregistre le message dans l'element
                            logging.info("Trouvé ligne :"+ligne)
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



class craft:
    def __init__(self,craft):
        self.craft = craft
        self.craft_restant = int(craft)
        self.status = 0
    def moins_craft(self):
        self.craft_restant = self.craft_restant-1

    def get_craft_restant(self):
        return self.craft_restant
            
class time_out:
    def __init__(self,Timer=0,activate=True):
       self.test = False
       self.value = Timer
       self.activate =activate
       self.ini_value = Timer
    def timer(self):
       if not self.activate:
          return False  
       sleep(1)
       self.value=self.value-1
       if self.value <=0:
           logging.debug("timeout")
           self.test =  True
           return True
       else:
           return False

    def reset(self):
        self.test = False
        self.value = self.ini_value

