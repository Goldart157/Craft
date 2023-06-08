

import logging
import pyautogui
import pygetwindow
import logging
from PIL import Image
import io

from time import sleep
import ctypes

class element_FFXIV: #Element pour recherche d'image 
    def __init__(self,fichier):
        self.fichier = fichier
        self.windows = None
        self.region = self.obtenir_region_application()
        self.coord_x = 0
        self.coord_y = 0
        if self.windows is not None:
            self.hwnd = self.windows._hWnd
        
    def obtenir_region_application(self,application="Final Fantasy XIV"):
        try:
            # Trouver la fenêtre de l'application par son titre ou son nom de classe
            app_window = pygetwindow.getWindowsWithTitle("Final Fantasy XIV")[0]
            self.windows = app_window
            # Obtenir les coordonnées et les dimensions de la fenêtre de l'application
            x, y, largeur, hauteur = app_window.left, app_window.top, app_window.width, app_window.height
            logging.debug("Fenetre FF trouvée")
            #logging.debug(x, y, largeur, hauteur)
            #self.region = x, y, largeur, hauteur
            return x,y,largeur,hauteur
        except IndexError:
            logging.error("Element FF14: La fenetre de l'application n'a pas été trouvée.")
            return None
        except Exception as e:
            logging.error("Une erreur s'est produite lors de l'obtention de la région de l'application:")
            logging.error(str(e))
            return None

    def localiser_image(self,mode_rapide = False, verif =False ):
        ctypes.windll.user32.SetForegroundWindow(self.hwnd)
        chemin_image=self.fichier
        if self.coord_x != 0 and self.coord_y  != 0:
            region_pre_recherche = self.coord_x -100,self.coord_y - 60,200,120
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
            position = pyautogui.locateOnScreen(image=chemin_image)#, region=self.region)#recherche sur une petite partie
            logging.debug("recherche lancée")
            if position is not None:
                self.coord_x = position.left + (position.width // 2)
                self.coord_y = position.top + (position.height // 2)
                logging.debug("Coordonnée trouvées")
                return True  # Image trouvée avec les coordonnées
        logging.debug("Pas de résultat pour recherche d'image") 
        self.coord_x = 0 
        self.coord_y = 0 
        return False  # Image non trouvée, coordonnées non définies

    def clique_droit_image(self):
        x=self.coord_x
        y=self.coord_y   
        if x == 0 and y ==0 :
            self.localiser_image()
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


