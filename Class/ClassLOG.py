class logFFXIV:

    def __init__(self,fichier):
        self.fichier = fichier
        self.heure_message = datetime(1994,12,13,0,0,0)
        self.message = None
        self.heure_message_prev = datetime(1994,12,13,0,0,0)

    def derniere_ligne_filtree(self,filtre):
        with open(self.fichier, 'r', encoding='utf-8') as f:
            lignes = f.readlines()
            lignes = lignes[-100:]  # Obtenir les 100 dernières lignes du fichier
            for ligne in reversed(lignes):
                ligne = ligne.strip()
            
                if filtre in ligne:
                              
                    temp_heure_message = self._extraire_heure(ligne)

                    if  temp_heure_message > self.heure_message:
                        self.heure_message = temp_heure_message
                        self.message = ligne
                        logging.info("Trouvé ligne :"+ligne)
                        return self.message
                    else: 
                        logging.debug("heure message actuel < a h dernier message lu: None returned")
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
    
    def message_apparait (self, filtre):
        temp = self.derniere_ligne_filtree(filtre)
        if temp is not None:
            return True
        else: 
            return False


###### Fonction de gestion d'image, recherche et clique sur élement du jeu 

class element_FFXIV: #Element pour recherche d'image 
    def __init__(self,fichier):
        self.fichier = fichier
        self.region = self.obtenir_region_application()
        self.coord_x = 0
        self.coord_y = 0
        
    def obtenir_region_application(self,application="Final Fantasy XIV"):
        try:
            # Trouver la fenêtre de l'application par son titre ou son nom de classe
            app_window = pygetwindow.getWindowsWithTitle("Final Fantasy XIV")[0]

            # Obtenir les coordonnées et les dimensions de la fenêtre de l'application
            x, y, largeur, hauteur = app_window.left, app_window.top, app_window.width, app_window.height
            logging.debug("Fenetre FF trouvée")
            #logging.debug(x, y, largeur, hauteur)
            #self.region = x, y, largeur, hauteur
            return x,y,largeur,hauteur
        except IndexError:
            logging.error("La fenetre de l'application n'a pas été trouvée.")
            return None
        except Exception as e:
            logging.error("Une erreur s'est produite lors de l'obtention de la région de l'application:")
            logging.error(str(e))
            return None

    def localiser_image(self,mode_rapide = True, verif =False ):
        chemin_image=self.fichier
        if self.coord_x != 0 and self.coord_y  != 0:
            region_pre_recherche = self.coord_x -60,self.coord_y - 60,120,120
            position = pyautogui.locateOnScreen(image=chemin_image, region=region_pre_recherche)#recherche sur une petite partie
            if position is not None:
                self.coord_x = position.left + (position.width // 2)
                self.coord_y = position.top + (position.height // 2)
                logging.debug("Recherche rapide trouvé")
                return True
    
        if mode_rapide is True:
            divX = 4 #Nombre de division d'écran 
            divY = 5 
        
            for i in range(divX,2,-1): #Recherche horizontale
                for j in range(0,divY):#Recherche verticale
                
                    x, y, largeur, hauteur = self.region
                    x = x + ((i-1)*largeur/divX)
                    y = y + (j)*hauteur/divY
                    largeur = 1/divX*largeur
                    hauteur = 1/divY*hauteur

                    x=int(x)
                    y=int(y)
                    largeur =  int(largeur)
                    hauteur = int(hauteur)
                
                    subRegion =  x, y, largeur, hauteur   #Redélimitation de  
                    print (x, y, largeur, hauteur )
                    #logging.debug(x,y,largeur,hauteur)
                    # Prendre un screenshot
                    screenshot = pyautogui.screenshot(region=subRegion)

                    # Convertir l'image en format binaire
                    image_bytes = io.BytesIO()
                    screenshot.save(image_bytes, format='PNG')
                    image_bytes.seek(0)

                    # Ouvrir et afficher l'image
                    #image = Image.open(image_bytes)
                    #image.show()
                    position = pyautogui.locateOnScreen(image=chemin_image, region=subRegion)#recherche sur une petite partie
                
                    if position is not None:
                        self.coord_x = position.left + (position.width // 2)
                        self.coord_y = position.top + (position.height // 2)
                        logging.debug("Coordonnée trouvées")
                        #logging.debug(self.coord_x,self.coord_y)
                        return True
                        break
                
        if verif or not mode_rapide:
            position = pyautogui.locateOnScreen(image=chemin_image, region=region)#recherche sur une petite partie

            if position is not None:
                self.coord_x = position.left + (position.width // 2)
                self.coord_y = position.top + (position.height // 2)
                logging.debug("Coordonnée trouvées")
                logging.debug(self.coord_x,self.coord_y)
                return True  # Image trouvée avec les coordonnées
        logging.debug("Pas de résultat pour recherche d'image") 
        self.coord_x = 0 
        self.coord_y = 0 
        return False  # Image non trouvée, coordonnées non définies

    def clique_droit_image(self):
        x=self.coord_x
        y=self.coord_y        
        duree_pression = 250/1000
        pyautogui.mouseDown(x, y, button='left')
        sleep(duree_pression)
        pyautogui.mouseUp(x, y, button='left')
        logging.info("Cliqué sur "+str(x)+" "+str(y))
        self.deplacer_souris_vers_le_haut()
        return None
        
    def deplacer_souris_vers_le_haut(self):
        # Obtenir la position actuelle de la souris
        x, y = pyautogui.position()

        # Calculer la nouvelle position
        nouvelle_position = (x, y + 200)

        # Déplacer la souris vers la nouvelle position
        pyautogui.moveTo(nouvelle_position )

class craft:
    def __init__(self,craft):
        self.craft = craft
        self.craft_restant = craft
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

###### Interface Macrodef fenetre_Commande():
    
class ToggleButton:
    def __init__(self, text):
        self.text = text
        self.var = tk.BooleanVar()
        self.checkbutton = None

    def create_widget(self, parent, row =0,col=0,padx=0,pady=0,rowspan=1):
        self.checkbutton = tk.Checkbutton(parent, text=self.text + " désactivé", variable=self.var, command=self.toggle_button)
        self.checkbutton.grid(row=row, column=col,padx=padx,pady=pady,rowspan=rowspan)
        #self.label = tk.Label(parent,text="config "+self.text)
       # self.label.grid(row=row,column=col) 

    def etat(self):
        if self.var.get():
            return True
        else: 
            return False

    def toggle_button(self):
        if self.var.get():
            self.checkbutton.config(text=self.text + " activée")
        else:
            self.checkbutton.config(text=self.text + " désactivée")

class FenetreCommande:
    def __init__(self):
        self.fenetre = tk.Tk()
        self.fenetre.attributes('-topmost', True)
        craft_input = 0 

        # Premier colonne
        LabelConfig = tk.Label(self.fenetre, text="Configuration")
        LabelConfig.grid(row=0, column=0)

        foodButton = ToggleButton("Food")
        foodButton.create_widget(self.fenetre, row=1, pady=10)

        # Séparateur après la première colonne
        separator1 = ttk.Separator(self.fenetre, orient='vertical')
        separator1.grid(row=0, column=1, rowspan=3, padx=10, sticky='ns')

        # Deuxième colonne
        button_play = tk.Button(self.fenetre, text="Play", command=lambda: play())  # command=play)
        button_play.grid(row=0, column=2, padx=10, pady=5, sticky='ns')

        button_pause = tk.Button(self.fenetre, text="Pause", command=lambda: pause())  # , command=pause)
        button_pause.grid(row=1, column=2, padx=10, pady=5, sticky='ns')

        button_stop = tk.Button(self.fenetre, text="Stop")  # , command=stop)
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
        #self.entry_craft.bind("<FocusOut>", self._update_craft_after_key)
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
        return self.foodButton.etat()
    def nb_craft_saisi(self):
        if self.isInt(self.entry_craft.get()):
            return self.entry_craft.get()
        else :
            return 0