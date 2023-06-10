from  time import sleep
import logging
import threading
import datetime
lock = threading.Lock()
import pygetwindow
import keyboard
import mouse
from pynput.mouse import Listener
import pyautogui

#Class qui gere le statut
class status():
    def __init__(self,config):
        self._value = 0
        self.Etiquette = "Attente lancement Craft"
        self._timer = None
        self.config = config
        self._thread = None
        self.heure_init = None
        self.duree_cycle = None
        self.chrono_unvalid = False
        
    def status_change(self,statut):
        new_value = int(statut)
        self.chrono()

        if new_value != self._value:

            logging.info("New Status :"+str(new_value))
            
            if self._timer is not None:
                self._timer.cancel()

            if new_value in self.config: #On vérifie si un timer a été précisé pour le statut actuel

                #Si un time out est spécifié pour l'étape demandée
                if self.config[new_value]["time_out"] is not None:
                    logging.debug("timer trouvé et initialisé")
                    self._timer = threading.Timer(self.config[new_value]["time_out"],self.timeout_handler)
                    self._timer.start()
                    logging.debug(self.config[new_value]["time_out"])
                
                else:
                    self._timer = None
                    logging.debug("pas de timer pour le statut spécifié")
                
            #Modification de la valeur après traitement timer
            with lock:
                self._value=new_value
    
    def timeout_handler(self): #Réinitialise le status si time_out 
        logging.error("status:Time Out")
        with lock:
            self._value = 98

    def return_status(self):
        return self._value

    def chrono(self):
        stat= self.return_status()

        if stat==1: 
            self.heure_init = datetime.datetime.now()
            self.chrono_unvalid = False #Au passage a 1 la mesure de temps est revalidée 

        if stat==7 and not self.chrono_unvalid :
            self.duree_cycle = datetime.datetime.now() - self.heure_init
        
        if not (stat > 0 and stat < 10):#Si le statut n'est pas compris dans la plage de mesure on dévalide la mesure.
            self.chrono_unvalid=True

#Permet le record de la config HQ du craft
class HQ:
    def __init__(self):
        self.clicks = []
        self.initialized = False

    def on_click(self, x, y, button, pressed):
        if str(button) == "Button.left" and pressed:
            new_click = [{'x':x},{'y':y}]
            self.clicks.append(new_click)
            
            logging.debug(f"({x}, {y}) clicked")

    def record(self):
        logging.info("Record Click Started")
        self.clicks = []
        with Listener(on_click=self.on_click) as listener:
            keyboard.wait('s')
            listener.stop()
            self.initialized = True
            listener=None

    def restore(self):
       
        for click in self.clicks:
            print(self.clicks)
            x = click[0]['x']
            y = click[1]['y']
            duration = 0.25  # Durée de pression de 250 ms
            logging.debug("click on x:"+str(x)+",y: "+str(y))
            pyautogui.mouseDown(x, y, button='left')
            sleep(duration)
            pyautogui.mouseUp(x, y, button='left')
            sleep(0.25)

#Class qui contient toutes les données relative au craft            
class craft:
    def __init__(self,craft,config):
        self.craft = craft
        self.craft_restant = int(craft)
        self._status = status(config)
        self.need_repair = False
        self.HQ = HQ()
        self.need_waiting = True
        self.need_material = False

    def moins_craft(self): #Retire un craft
        self.craft_restant = self.craft_restant-1

    def get_craft_restant(self): 
        return self.craft_restant

    def change_status(self,new_status):
        
            temp=int(new_status)
            if temp !=  self.get_status():
                self._status.status_change(new_status)
            else:
                logging.debug("Changement de status demandé mais refusé car ancien = nouveau")

    def get_status(self):

        return self._status.return_status()

    def next_step(self): #Augment le status de 1 

        temp=self._status.return_status()
        self.change_status(temp+1)       
    
    def duree_craft_restante(self):

        duree_craft = self._status.duree_cycle

        if duree_craft is not None:

            duree_craft = duree_craft * self.craft_restant
            logging.debug(str(duree_craft))
            return duree_craft

        return None


