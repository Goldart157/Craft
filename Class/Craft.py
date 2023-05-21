from  time import sleep
import logging
import threading
import datetime
lock = threading.Lock()


class status():
    def __init__(self,config):
        self.value = 0
        self.Etiquette = "Attente lancement Craft"
        self.timer = None
        self.config = config
        self.thread = None

    def statut_change(self,statut):
#        try:
            new_value = int(statut)
            if new_value != self.value:
                if new_value in self.config: #On vérifie si un timer a été précisé pour le statut actuel
                    logging.debug("timer trouvé et initialisé")
                    self.timer = threading.Timer(self.config[new_value]["time_out"],self.timeout_handler)
                    self.timer.start()
                    logging.debug(self.config[new_value]["time_out"])
                else:
                    self.timer = None
                    logging.debug("pas de timer pour le statut spécifié")
                with lock:
                    self.value=new_value
#        except:
 #           logging.error("une erreur non gérée est arrivée")
    def timeout_handler(self):
        with lock:
            self.value = 0

    def return_status(self):
        return self.value

    def timer_is_ok(self):
        if self.timer is None:
            logging.debug('phase non timée')
            return False
        else :
            with lock():
                return self.timer.value        
            

            
class craft:
    def __init__(self,craft,config):
        self.craft = craft
        self.craft_restant = int(craft)
        self.status = status(config)
    def moins_craft(self):
        self.craft_restant = self.craft_restant-1

    def get_craft_restant(self):
        return self.craft_restant
            
class time_out:
    def __init__(self,Timer=10):
       self.test = False
       self.value = Timer
       self.ini_value = datetime.datetime.now() 
  

    def timer(self):
       heure_appel = datetime.datetime.now() 
       delta = datetime.timedelta(seconds=self.value)
       with lock: 
           if heure_appel - self.ini_value > delta :
               return True
           else:
               print(heure_appel - self.ini_value)
               return False
      