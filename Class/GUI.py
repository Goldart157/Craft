###### Interface Macrodef fenetre_Commande():
import tkinter as tk
from tkinter import ttk
import logging
from datetime import timedelta


#Bouton qui change de label si activé ou non
class CustomCheckbutton:
    def __init__(self, master,row=0,column=0,padx=0,pady=0,text=""):
        self.master = master
        self.var = tk.BooleanVar()
        self.var.trace('w', self.update_label)  # Appeler update_label lorsqu'il y a un changement d'état
        self.label = text
        self.checkbutton = tk.Checkbutton(self.master, text=self.label+" Off", variable=self.var)
        self.checkbutton.grid(row=row, column=column,  padx=padx, sticky='w')

    def update_label(self, *args):
        if self.var.get():
            self.checkbutton["text"] = self.label+" On"
        else:
            self.checkbutton["text"] = self.label+" Off"

    def get_value(self):
        try:
            return self.var.get()
        except:
            pass

#fenetre de commande principale
class FenetreCommande:
    def __init__(self,crafting):
        self.fenetre = tk.Tk()
        self.fenetre.attributes('-topmost', True)
        craft_input = 0 
        self.crafting =crafting

        # Premiere colonne
        LabelConfig = tk.Label(self.fenetre, text="Configuration")
        LabelConfig.grid(row=0, column=0)

        self.foodButton = CustomCheckbutton(self.fenetre,row=1, pady=10,padx=10,text="Food")
        self.potButton = CustomCheckbutton(self.fenetre,row=2, pady=10,padx=10,text="Pot")
        self.shutdown_button = CustomCheckbutton(self.fenetre,row=3, pady=10,padx=10,text="Arrêt")
        self.repa_button = CustomCheckbutton(self.fenetre,row=4, pady=10,padx=10,text="Repa.")
        self.materialize_button = CustomCheckbutton(self.fenetre,row=5,padx=10, pady=10,text="Matéria")

        # Séparateur après la première colonne
        separator1 = ttk.Separator(self.fenetre, orient='vertical')
        separator1.grid(row=0, column=1, rowspan=6, padx=10, sticky='ns')

        # Deuxième colonne
        self.label_status = tk.Label(self.fenetre,text="Status : 0")
        self.label_status.grid(row=0, column=2, padx=10, pady=5, sticky='ns')

        self.label_text_status = tk.Label(self.fenetre,text="Attente Lancement")
        self.label_text_status.grid(row=1, column=2, padx=10, pady=5, sticky='ns')

        button_play = tk.Button(self.fenetre, text="Play", command= self.play,width=10)
        button_play.grid(row=2, column=2, padx=10, pady=5, sticky='ns')

        button_pause = tk.Button(self.fenetre, text="Pause", command= self.pause,width=10)  # , command=pause)
        button_pause.grid(row=3, column=2, padx=10, pady=5, sticky='ns')

        button_stop = tk.Button(self.fenetre, text="HQ", command= self.hq,width=10)  # , command=stop)
        button_stop.grid(row=4, column=2, padx=10, pady=5, sticky='ns')

        button_test = tk.Button(self.fenetre, text="test", command= self.test,width=10)  # , command=stop)
        button_test.grid(row=5, column=2, padx=10, pady=5, sticky='ns')

        # Séparateur après la deuxième colonne
        separator2 = ttk.Separator(self.fenetre, orient='vertical')
        separator2.grid(row=0, column=3, rowspan=6, padx=10, sticky='ns')

        # Troisième colonne
        label_craft = tk.Label(self.fenetre, text="Nombre de crafts à faire:")
        label_craft.grid(row=0, column=4, padx=10, pady=5, sticky='ns')

        self.label_craft_restant = tk.Label(self.fenetre, text="Restant : 0")
        self.label_craft_restant.grid(row=3, column=4, padx=10, pady=5, sticky='ns')

        self.entry_craft = tk.Entry(self.fenetre)
        self.entry_craft.grid(row=1, column=4, padx=10, pady=5, sticky='w')
        self.entry_craft.bind("<KeyRelease>", self._update_craft_after_key)
        
        # Séparateur après la craft 
        separator3 = ttk.Separator(self.fenetre, orient='horizontal')
        separator3.grid(row=2, column=4,  sticky='ew')

       

        self.label_Duree_restant = tk.Label(self.fenetre,text="Durée restante :")
        self.label_Duree_restant.grid(row=4, column=4, padx=10, pady=5, sticky='ns')

        self.label_Valeur_Duree_restant = tk.Label(self.fenetre,text="00:00:00")
        self.label_Valeur_Duree_restant.grid(row=5, column=4, padx=10, pady=5, sticky='ns')

    #Permet de rentrer la config saisie dans l'input box dans la variable
    def _update_craft_after_key(self, event): 
        temp = self.entry_craft.get()
        if self.isInt(temp)and self.entry_craft.focus_get():
            self.label_craft_restant.config(text="Restant : " + str(temp))
            self.craft_input = temp
            logging.debug("label updated")
    
    #Update du label craft restant
    def update_craft_restant(self, new_craft_restant=0):
        if self.isInt(new_craft_restant):
            self.label_craft_restant.config(text="Restant : " + str(new_craft_restant))

    #Updtate du status
    def update_status(self,status,text="No label for this status"):
        self.label_status.config(text="Status : "+str(status))
        self.label_text_status.config(text=text)

    def update_duree_restant(self,duree):
        if not isinstance(duree,timedelta):
            self.label_Valeur_Duree_restant.config(text="")
        else: 
            nbsecond = duree.seconds
            
            hours = nbsecond // 3600
            minutes = (nbsecond % 3600) // 60
            strtime = str(hours) +"h "+str(minutes)+" min"
            self.label_Valeur_Duree_restant.config(text=strtime)

    def isInt(self,value):
        try:
            int(value)
            return True 
        except ValueError:
            return False
    def run(self):
        # Lancer la boucle principale de la fenêtre
        self.fenetre.mainloop()
    
    #Updtate du status
    def update_status(self,status,text="No label for this status"):
        self.label_status.config(text="Status : "+str(status))
        self.label_text_status.config(text=text)

    def isInt(self,value):
        try:
            int(value)
            return True 
        except ValueError:
            return False

    #Fonction pour retourner les valeurs de la config
    def config_bouffe(self):
        return self.foodButton.get_value()

    def config_pot(self):
        return self.potButton.get_value()

    def config_arret(self):
        return self.shutdown_button.get_value()
    
    def nb_craft_saisi(self):
        if self.isInt(self.entry_craft.get()):
            return int(self.entry_craft.get())
        else :
            return 0
    
        
    #Fonction liées au bouton
    def play(self):
        if self.nb_craft_saisi()>0:
            self.crafting.craft_restant= self.nb_craft_saisi()
            self.crafting.change_status(1)
            self.entry_craft.delete(0,tk.END)
            self.fenetre.focus_set()    
        else:
            if self.crafting.get_craft_restant()>0:
                self.crafting.change_status(1)
            else:     
                self.label_craft_restant.config(text="N'est pas entier")
        
    def pause(self):
        self.crafting.change_status(10)
    def test(self):
        self.crafting.change_status(91)

    def hq(self):
        self.crafting.change_status(90)




