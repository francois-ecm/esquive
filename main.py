from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty,ListProperty
from kivy.core.window import Window
from random import randint
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock


class EsquiveGame(Widget):

    def __init__(self, **kwargs):
        super(EsquiveGame, self).__init__(**kwargs)

        # Initialisation du clavier
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
        self.pressed_keys = set()

        self.pressed_actions = {
            'up': lambda: self.player_move('up'),
            'down': lambda: self.player_move('down'),
            'left': lambda: self.player_move('left'),
            'right': lambda: self.player_move('right')
        }

        # Création du joueur
        self.player1 = Player()
        self.player1.lives = 3
        self.player1.score = 0
        self.player1.size = (15, 15)

        # Liste des Widgets des blocs qui tombent
        self.liste_Blocs = []

        # Gestion du nombre de blocs apparaissant
        self.difficulte = 3

        # Affichage initial
        with self.canvas:
            self.rect = Rectangle(pos=(self.center_x * 1.5, 0), size=(10, self.height))
            self.label1 = Label(font_size=20, center=(self.center_x * 1.75, self.center_y * 1.8),
                                text = 'Score :' )
            self.label2 = Label(font_size=20, center=(self.center_x * 1.75, self.center_y * 1.7),
                                text=str(self.player1.score))
            self.label3 = Label(font_size=20, center=(self.center_x * 1.75, self.center_y * 1),
                                text='Vies :')
            self.label4 = Label(font_size=20, center=(self.center_x * 1.75, self.center_y * 0.9),
                                text=str(self.player1.lives))
            self.player_rect = Rectangle(pos=(self.center_x * 0.75, self.center_y * 0.25), size=(15, 15))


    # Fonction principale exécutée tout les 1/60s. )
    def update(self, dt):

        # Réactualisation des différents Widgets
        self.rect.pos = (self.center_x * 1.5, 0)
        self.rect.size = (10, self.height)

        self.label1.center = (self.center_x * 1.75, self.center_y * 1.8)
        self.label2.center = (self.center_x * 1.75, self.center_y * 1.7)
        self.label3.center = (self.center_x * 1.75, self.center_y * 1)
        self.label4.center = (self.center_x * 1.75, self.center_y * 0.9)

        self.label1.text = 'Score :'
        self.label2.text = str(self.player1.score)
        self.label3.text = 'Vies :'
        self.label4.text = str(self.player1.lives)

        self.player_rect.pos = (self.player1.center_x - 7.5, self.player1.center_y - 7.5)

        for Bloc in self.liste_Blocs:
            Bloc.rect.pos = ((Bloc.center_x - 30, Bloc.center_y - 15))

        # Augmentation aléatoire de la difficulté
        if randint(1,100) < 5:
            self.difficulte += 1
        # Apparition aléatoire d'un nouveau bloc (en fonction de la difficulté)
        if randint(1,1000) < self.difficulte:
            self.pop_Bloc()

        self.move() # Bouge tous les blocs
        self.remove_Bloc() # Supprime les blocs arrivés trop bas
        self.contact() # Gère les contacts entre joueur et blocs

        if self.player1.lives == 0:
            self.defaite()

        for key in self.pressed_keys:
            try:
                self.pressed_actions[key]()
            except KeyError:
                return None

    def pop_Bloc(self): # Apparition d'un bloc

        self.Bloc = Bloc()

        self.Bloc.center_x = randint(30, int(self.center_x * 1.35))
        self.Bloc.center_y = self.center_y * 2

        self.add_widget(self.Bloc)
        self.liste_Blocs.append(self.Bloc)


    def remove_Bloc(self): # Suppression d'un bloc
        for Bloc in self.liste_Blocs:
            if Bloc.center_y < self.center_y * 0.1:
                self.remove_widget(Bloc)
                self.liste_Blocs.remove(Bloc)

    def defaite(self): # Si le nombre de vies arrive à 0 ... on reset tout !
        self.player1.score = 0
        self.player1.lives = 3
        self.difficulte = 1
        self.player1.center_x = self.center_x * 0.75
        self.player1.center_y = self.center_y * 0.25

        for Bloc in self.liste_Blocs:
            self.remove_widget(Bloc)
        self.liste_Blocs = []


    # Fonctions pour gérer les commandes clavier ...

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.pressed_keys.add(keycode[1])

    def _on_keyboard_up(self, keyboard, keycode):
        self.pressed_keys.remove(keycode[1])


    # Gestion du mouvement du joueur

    def player_move(self, touche):
        if touche == 'left':
            if self.player1.center_x >= self.center_x * 0.1:
                self.player1.center_x -= 4
        elif touche == 'right':
            if self.player1.center_x <= self.center_x * 1.4:
                self.player1.center_x += 4
        elif touche == 'up':
            if self.player1.center_y <= self.center_y * 1.9:
                self.player1.center_y += 4
        elif touche == 'down':
            if self.player1.center_y >= self.center_y * 0.1:
                self.player1.center_y -= 4
        return True


    def contact(self): # Gestion de contact entre le joueur et un bloc
        for Bloc in self.liste_Blocs:
            if self.player1.collide_widget(Bloc):

                if Bloc.categorie == 0: # La catégorie du bloc est 0 (rouge) si on doit l'éviter, 1 (vert) si c'est un bonus
                    self.player1.lives -= 1
                elif Bloc.categorie == 1:
                    self.player1.score += 1

                self.remove_widget(Bloc) # On supprime le bloc en contact avec le joueur
                self.liste_Blocs.remove(Bloc)



    def move(self):
        for Bloc in self.liste_Blocs:
            Bloc.move()



class Player(Widget):


    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)

        self.lives = NumericProperty(0)
        self.score = NumericProperty(0)
        self.center_x = 300
        self.center_y = 100

class Bloc(Widget):

    def __init__(self, **kwargs):
        super(Bloc, self).__init__(**kwargs)

        self.size = (60,30)
        self.center_x = -100
        self.center_y = -100

        x = randint(0, 100)

        if x <= 80:
            self.categorie = 0
        elif x > 80:
            self.categorie = 1


        with self.canvas:
            if self.categorie == 0:
                Color(1, 0, 0)
            else:
                Color(0,1,0)
            self.rect = Rectangle(pos=(self.center_x, self.center_y), size=self.size)



    def move(self):
        self.center_y = self.center_y - 2



class EsquiveApp(App):
    def build(self):
        game = EsquiveGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)

        return game


if __name__ == '__main__':
    EsquiveApp().run()
