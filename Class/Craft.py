from  time import sleep
import logging

class ModeManager:
    def __init__(self):
        self._mode = 0
    
    @property
    def mode(self):
        return self._mode
    
    def __setattr__(self, name, value):
        if name == "mode":
            if isinstance(value, int) and value != self._mode:
                self._mode = value
                self.on_mode_change()  # Appeler la fonction on_mode_change()
            else:
                raise ValueError("Le mode doit être un entier.")
        else:
            super().__setattr__(name, value)
    
    def on_mode_change(self):
        # Fonction à exécuter lorsque la valeur du mode change
        print("Mode changé :", self._mode)

class craft:
    def __init__(self,craft):
        self.craft = craft
        self.craft_restant = int(craft)
        self.status = ModeManager()
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
