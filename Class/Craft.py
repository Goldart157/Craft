from  time import sleep
import logging
import threading
import datetime
lock = threading.Lock()
import pygetwindow

class status():
    def __init__(self,config):
        self._value = 0
        self.Etiquette = "Attente lancement Craft"
        self._timer = None
        self.config = config
        self._thread = None

    def status_change(self,statut):
        new_value = int(statut)
        if new_value != self._value:
            if new_value in self.config: #On vérifie si un timer a été précisé pour le statut actuel
                logging.debug("timer trouvé et initialisé")
                self.timer = threading.Timer(self.config[new_value]["time_out"],self.timeout_handler)
                self.timer.start()
                logging.debug(self.config[new_value]["time_out"])
            else:
                self.timer = None
                logging.debug("pas de timer pour le statut spécifié")
            with lock:
                self._value=new_value
    
    def timeout_handler(self):
        with lock:
            self._value = 0

    def return_status(self):
        return self._value

           
            

            
class craft:
    def __init__(self,craft,config):
        self.craft = craft
        self.craft_restant = int(craft)
        self._status = status(config)

    def moins_craft(self):
        self.craft_restant = self.craft_restant-1

    def get_craft_restant(self):
        return self.craft_restant

    def change_status(self,new_status):
        try:
            temp=int(new_status)
            self._status.status_change(new_status)
        except:
            logging.debug("statut n'as pas été changé")

    def get_status(self):
        return self._status.return_status()

    def next_step(self):
        temp=self._status.return_status()
        self.change_status(temp+1)            

      