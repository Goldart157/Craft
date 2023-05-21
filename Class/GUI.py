###### Interface Macrodef fenetre_Commande():
import tkinter as tk
from tkinter import ttk
import logging



#Bouton qui change de label si activé ou non
class CustomCheckbutton:
    def __init__(self, master,row=0,column=0,padx=0,pady=0,text=""):
        self.master = master
        self.var = tk.BooleanVar()
        self.var.trace('w', self.update_label)  # Appeler update_label lorsqu'il y a un changement d'état
        self.label = text
        self.checkbutton = tk.Checkbutton(self.master, text=self.label+" Off", variable=self.var)
        self.checkbutton.grid(row=row, column=column,  padx=padx, sticky='ns')

    def update_label(self, *args):
        if self.var.get():
            self.checkbutton["text"] = self.label+" On"
        else:
            self.checkbutton["text"] = self.label+" Off"

    def get_value(self):
        return self.var.get()

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

        self.foodButton = CustomCheckbutton(self.fenetre,row=1, pady=10,text="Food")
        self.shutdown_button = CustomCheckbutton(self.fenetre,row=2, pady=5,text="Arrêt apres craft")
        self.repa_button = CustomCheckbutton(self.fenetre,row=3, pady=5,text="Reparation")
        self.materialize_button = CustomCheckbutton(self.fenetre,row=4, pady=5,text="Matérialisation")

        # Séparateur après la première colonne
        separator1 = ttk.Separator(self.fenetre, orient='vertical')
        separator1.grid(row=0, column=1, rowspan=3, padx=10, sticky='ns')

        # Deuxième colonne
        button_play = tk.Button(self.fenetre, text="Play", command= self.play)
        button_play.grid(row=0, column=2, padx=10, pady=5, sticky='ns')

        button_pause = tk.Button(self.fenetre, text="Pause", command= self.pause)  # , command=pause)
        button_pause.grid(row=1, column=2, padx=10, pady=5, sticky='ns')

        button_stop = tk.Button(self.fenetre, text="Test", command= self.test)  # , command=stop)
        button_stop.grid(row=2, column=2, padx=10, pady=5, sticky='ns')

        # Séparateur après la deuxième colonne
        separator2 = ttk.Separator(self.fenetre, orient='vertical')
        separator2.grid(row=0, column=3, rowspan=3, padx=10, sticky='ns')

        # Troisième colonne
        label_craft = tk.Label(self.fenetre, text="Nombre de crafts à faire:")
        label_craft.grid(row=0, column=4, padx=10, pady=5, sticky='ns')

        self.label_craft_restant = tk.Label(self.fenetre, text="Restant : 0")
        self.label_craft_restant.grid(row=2, column=4, padx=10, pady=5, sticky='ns')

        self.entry_craft = tk.Entry(self.fenetre)
        self.entry_craft.grid(row=1, column=4, padx=10, pady=5, sticky='ns')
        self.entry_craft.bind("<KeyRelease>", self._update_craft_after_key)

    def _update_craft_after_key(self, event):
        temp = self.entry_craft.get()
        if self.isInt(temp)and self.entry_craft.focus_get():
            self.label_craft_restant.config(text="Restant : " + str(temp))
            self.craft_input = temp
            logging.debug("label updated")

    def update_craft_restant(self, new_craft_restant=0):
        if self.isInt(new_craft_restant):
            self.label_craft_restant.config(text="Restant : " + str(new_craft_restant))

    def run(self):
        # Lancer la boucle principale de la fenêtre
        self.fenetre.mainloop()

    def isInt(self,value):
        try:
            int(value)
            return True 
        except ValueError:
            return False

    def config_bouffe(self):
        return self.foodButton.get_value()
    
    def nb_craft_saisi(self):
        if self.isInt(self.entry_craft.get()):
            return int(self.entry_craft.get())
        else :
            return 0

    def play(self):
        if self.nb_craft_saisi()>0:
            self.crafting.craft_restant = self.nb_craft_saisi()
            self.crafting.change_statut(1)
            self.entry_craft.delete(0,tk.END)
        else:
             self.label_craft_restant.config(text="N'est pas entier")
        
    def pause(self):
        self.crafting.change_statut(10)

    def test(self):
        print(self.config_bouffe())




