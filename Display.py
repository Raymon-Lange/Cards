import pygame
from enum import Enum, auto
from Network import Network
from Game import *
import sys,os

# Create the window
window = pygame.display.set_mode((800, 600))

# Set the background color
window.fill((0, 100, 0))

# Load background
background = pygame.image.load("assets/background.png")

# Colors

WHITE = (255, 255, 255)
DARK_GREEN = (0, 100, 0)
BUTTON_COLOR = (17,60,24)
HOVER_COLOR = (7,24,10)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
DARK_GREY = (100, 100, 100)

# Button class
class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback
        self.assets_dir = os.path.join("assets", "font","PressStart2P-vaV7.ttf")
        self.font = pygame.font.Font(self.assets_dir, 16)
        self.bg_color = BUTTON_COLOR
        self.text_color =  WHITE
        self.border_color = BLACK
        self.hover_color = HOVER_COLOR
        self.border_width = 2
        self.border_radius = 10

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        current_color = self.hover_color if is_hovered else self.bg_color

        pygame.draw.rect(surface, current_color, self.rect, 0, self.border_radius)
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_width, self.border_radius)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()


class ToggleButton(Button):
    def __init__(self, text, x, y, w, h, callback, initial_state=True):
        super().__init__(text, x, y, w, h, callback)
        self.state = initial_state

    def draw(self, surface):
        label_text = f"{self.text}: {'ON' if self.state else 'OFF'}"
        pygame.draw.rect(surface, GREY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        label = self.font.render(label_text, True, BLACK)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.state = not self.state
            self.callback(self.state)


class Slider:
    def __init__(self, label, x, y, w, h, min_value, max_value, initial, on_change):
        self.label = label
        self.rect = pygame.Rect(x, y, w, h)
        self.slider_rect = pygame.Rect(x, y - 5, 10, h + 10)
        self.min = min_value
        self.max = max_value
        self.value = initial
        self.dragging = False
        self.on_change = on_change
        self.assets_dir = os.path.join("assets", "font","PressStart2P-vaV7.ttf")
        self.font = pygame.font.Font(self.assets_dir, 16)
        self.update_slider_pos()

    def update_slider_pos(self):
        percent = (self.value - self.min) / (self.max - self.min)
        self.slider_rect.centerx = self.rect.x + int(percent * self.rect.width)

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GREY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        pygame.draw.rect(surface, GREY, self.slider_rect)
        pygame.draw.rect(surface, BLACK, self.slider_rect, 1)
        text = self.font.render(f"{self.label}: {self.value}", True, BLACK)
        surface.blit(text, (self.rect.x, self.rect.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.slider_rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_x = max(self.rect.x, min(event.pos[0], self.rect.right))
            percent = (new_x - self.rect.x) / self.rect.width
            self.value = int(self.min + percent * (self.max - self.min))
            self.update_slider_pos()
            self.on_change(self.value)



class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    OPTIONS = auto()
    CONNECTING  = auto()

# Create the main class
class Display:

    def __init__(self):
        self.window = window
        self.game = Board(0)
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Spite and Malice")
        
        self.playerId = 1
        deck = Deck()

        self.cardImages = {}
        self.otherPlayerCard = pygame.image.load(join("assets", "backs", "BackRed.png"))

        for suit in deck.suits:
            for rank in deck.ranks:
                key = f"{rank} of {suit}"
                image = pygame.image.load(join("assets", suit, suit+rank+".png"))
                self.cardImages.update({key : image})


        self.assets_dir = os.path.join("assets", "font","PressStart2P-vaV7.ttf")
        self.font = pygame.font.Font(self.assets_dir, 16)

        box_rect = pygame.Rect((800 // 2) - 200, (600 // 2) - 100, 300, 100)
        button_rect = pygame.Rect(box_rect.centerx - 40, box_rect.bottom - 40, 80, 30)

        # Create buttons
        self.menuButtons = [
            Button("Multiplayer", 280, 250, 220, 60, self.on_multiplayer),
            Button("Single Player", 280, 330, 220, 60, self.on_singleplayer),
            Button("Options", 280, 410, 220, 60, self.on_options),
            
        ]

        self.playingButtons = [
            Button("OK", button_rect.x , button_rect.y , 80, 30, self.ok_button)
        ]

        self.optionsButtons = [
            Button("Back", 50, 500, 100, 40, self.on_back),
            ToggleButton("Sound", 50, 250, 150, 40, self.toggle_sound, initial_state=True),
            Slider("Volume", 50, 330, 300, 20, min_value=1, max_value=100, initial=50, on_change=self.set_volume),    
        ]

        # Load sounds 
        self.muted = False
        self.volume = 50/100
        self.cardDrop = pygame.mixer.Sound(join("assets", "sounds", "carddrop.wav"))
        self.cardDrop.set_volume(self.volume)

        self.cardshuffle = pygame.mixer.Sound(join("assets", "sounds", "cardsShuffling.wav"))
        self.cardshuffle.set_volume(self.volume)

        self.state = GameState.MENU

    def run(self):
        while True:
            if self.state == GameState.MENU:
                self.handle_menu()
            elif self.state == GameState.PLAYING:
                self.handle_multiplayer()
            elif self.state == GameState.OPTIONS:
                self.handle_options()
            elif self.state == GameState.CONNECTING:
                self.handleConnecting()
            else:   
                print("No State!!!")
                break  

    ########################################
    # Drawling Game Helper Methods
    ########################################

    def deal(self):
        self.game.play("deal::", 0)

    def play(self):
        self.game.play("deal::", 1)

    def drawCard(self, card , rotate=0):
        image = self.cardImages[str(card)]
        rotateImage = pygame.transform.rotate(image, rotate)
        self.window.blit(rotateImage, card.rect)

    def drawBoard(self):

        #STEP: Repaint the background
        self.window.fill((0,100,0))

        self.drawInfoBox()

        ySpaceing = 105

        #STEP: Draw Player One
        x = 25
        y = 50

        if len(self.game.playerOne.goal) !=0:
            self.drawCard(self.game.playerOne.goal[0], 90)

        x = 50

        for card in range(0,5):
            x += 12 + 71 
            if len(self.game.playerOne.hand) > card:
                if self.playerId == 0:
                    self.drawCard(self.game.playerOne.hand[card])
                else:
                    self.window.blit(self.otherPlayerCard, self.game.playerOne.hand[card])

        x = 80
        y += ySpaceing

        for card in self.game.playerOne.discard:
            x += 20 + 71 
            if len(card) == 0:
                pygame.draw.rect(self.window, (0, 255, 0), (x,y,71,94), 2)
            else:
                self.drawCard(card[len(card)-1])

        # Draw the field
        x = 50
        y += ySpaceing
        
        for card in self.game.field:
            x += 20 + 71 
            if len(card) == 0:
                pygame.draw.rect(self.window, (0, 255, 0), (x,y,71,94), 2)
            else:
                topcard = card[len(card)-1]
                tmp = Deck()
                if topcard.rank == "King":
                    king = Card(topcard.suit, tmp.ranks[len(card)-1])
                    king.rect = topcard.rect
                    self.drawCard(king)
                else:
                    self.drawCard(topcard)


        #STEP: Draw Player Two
        x = 80
        y += ySpaceing

        for card in self.game.playerTwo.discard:
            x += 20 + 71 
            if len(card) == 0:
                pygame.draw.rect(self.window, (0, 255, 0), (x,y,71,94), 2)
            else:
                self.drawCard(card[len(card)-1])


        x = 25
        y += ySpaceing

        if len(self.game.playerTwo.goal) != 0:
            self.drawCard(self.game.playerTwo.goal[0],90)

        x = 50

        for card in range(0,5):
            x += 20 + 71 
            if len(self.game.playerTwo.hand) > card:
                if self.playerId == 1:
                    self.drawCard(self.game.playerTwo.hand[card])
                else: 
                    self.window.blit(self.otherPlayerCard, self.game.playerTwo.hand[card])

    def drawInfoBox(self):
        rect = pygame.Rect(540, 10, 800-540, 200)
        white = (255, 255, 255)

        pygame.draw.rect(window, white, rect,5,25)

        text = "You are \nPlayer {}".format(self.playerId+1)
        text_surface = self.font.render(text, True, white)
        text_rect = text_surface.get_rect()
        text_rect.center = (550+((800-540)//2), 35)
        self.window.blit(text_surface, text_rect)

        if self.game == None:
            return

        text = "Current Turn \n Player {}".format(self.game.currentTurn+1)
        text_surface = self.font.render(text, True, white)
        text_rect = text_surface.get_rect()
        text_rect.center = (550+((800-540)//2), 75)
        self.window.blit(text_surface, text_rect)

        text = "Player 1\n{} cards left".format(len(self.game.playerOne.goal))
        text_surface = self.font.render(text, True, white)
        text_rect = text_surface.get_rect()
        text_rect.center = (550+((800-540)//2), 120)
        self.window.blit(text_surface, text_rect)

        text = "Player 2\n{} cards left".format(len(self.game.playerTwo.goal))
        text_surface = self.font.render(text, True, white)
        text_rect = text_surface.get_rect()
        text_rect.center = (550+((800-540)//2), 170)
        self.window.blit(text_surface, text_rect)

    def drawNoficationBox(self, text, callback=None):

        text_surface = self.font.render(text, True, BLACK)
        #if we have callback, make room for the ok Button
        if callback:
            box_rect = pygame.Rect((800 // 2) - 200, (600 // 2) - 100, 300, 100)
            text_rect = text_surface.get_rect(center=(box_rect.centerx, box_rect.centery- 20))
        else:  
            box_rect = pygame.Rect((800 // 2) - 200, (600 // 2) - 100, 300, 80)
            text_rect = text_surface.get_rect(center=(box_rect.centerx, box_rect.centery))

        # Draw notification box
        pygame.draw.rect(self.window, WHITE, box_rect, 0, 25)
        pygame.draw.rect(self.window, BLACK, box_rect, 5, 25)
    
        # Draw text
        self.window.blit(text_surface, text_rect)
        
        #Define and draw button
        if callback:
            button = self.playingButtons[0]
            button.draw(self.window)

    def ok_button(self):
        self.state = GameState.MENU

    ########################################
    # Option Screen Section 
    ########################################

    def handle_options(self):
        while self.state == GameState.OPTIONS:
            # Repaint the background
            self.drawOptionsScreen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

    def drawOptionsScreen(self):
        self.window.blit(background, (0, 0))

        for button in self.optionsButtons:
            button.draw(self.window)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for button in self.optionsButtons:
                button.handle_event(event)
        
        pygame.display.flip()    

    def on_back(self):
        self.state = GameState.MENU
        self.cardDrop.play()

    def toggle_sound(self, state):
        print("Sound On" if state else "Sound Off")
        self.muted = not self.muted
        if self.muted:
            self.volume = 0
        else:
            self.volume = 50/100
            self.cardDrop.play()

    def set_volume(self, value):
        print(f"Volume set to: {value}")
        self.volume = value / 100
        self.cardDrop.set_volume(self.volume)
        self.cardshuffle.set_volume(self.volume)

    def getPlayerName(self):

        input_active = True
        name = ""
        #font = pygame.font.Font(self.assets_dir, 32)
        input_box = pygame.Rect(300, 250, 200, 40)
        color = pygame.Color('white')

        while input_active:
            self.window.fill((0, 100, 0))  # Repaint background
            pygame.draw.rect(self.window, color, input_box, 2)

            text_surface = self.font.render(name, True, (255, 255, 255))
            self.window.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        
            prompt_surface = self.font.render("Enter your name:", True, (255, 255, 255))
            self.window.blit(prompt_surface, (input_box.x - 50, input_box.y - 50))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False  # Exit loop when Enter is pressed
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]  # Remove last character
                    else:
                        name += event.unicode  # Add character

        return name
    ########################################
    # Menu Screen Section 
    ########################################
    def drawLoadingScreen(self):
        self.window.blit(background, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for button in self.menuButtons:
            button.draw(self.window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for button in self.menuButtons:
                button.handle_event(event)
        pygame.display.flip()

    def on_multiplayer(self):
        self.state = GameState.CONNECTING
        self.cardDrop.play()
        print("Multiplayer clicked!")

    def on_singleplayer(self):
        self.cardDrop.play()
        print("Single Player clicked!")

    def on_options(self):
        self.cardDrop.play()
        self.state = GameState.OPTIONS
        print("Options clicked!")

    def handle_menu(self):
        while self.state == GameState.MENU:
            self.drawLoadingScreen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

    ########################################
    # Connecting  Section 
    ########################################


    def handleConnecting(self):
        self.network = Network()
        self.playerId = int(self.network.getId())

        while self.state == GameState.CONNECTING:

            self.game = self.network.send("get")
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                for button in self.playingButtons:
                    button.handle_event(event)
            
            self.drawBoard()

            if not self.game.ready:    
                self.drawNoficationBox("Waiting for a\nPlayer to Join")                
            else:
                print("Game is ready")
                self.cardshuffle.play()
                self.state = GameState.PLAYING

            # Update the window
            pygame.display.update()

    
    ########################################
    # Multiplayer Section 
    ########################################

    def handle_multiplayer(self):
        clock = pygame.time.Clock()

        self.activeCard = None
        self.orgX = 0
        self.orgY = 0

        while self.state == GameState.PLAYING:
            clock.tick(60)

            if self.game == None:
                self.game = self.network.send("get")

            if self.game.currentTurn != self.playerId and self.game.winner == None:
                self.game = self.network.send("get")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                for button in self.playingButtons:
                    button.handle_event(event)

                #if there is a winner no need to check for card movement
                if self.game.winner != None:
                    break

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_mouse_down(event.pos)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.handle_mouse_up()

                if event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.rel)

            self.drawBoard()

            if not self.game.ready:    
                self.drawNoficationBox("Waiting for a\nPlayer to Join")

            if self.game.winner != None:
                self.drawNoficationBox("Player {} Won!".format(self.game.winner), self.ok_button)

            # Update the window
            pygame.display.update()

    def handle_mouse_down(self, pos):
        if self.activeCard is not None:
            return

        player = self.game.playerOne if self.playerId == 0 else self.game.playerTwo

        self.try_select_card_from_list(player.hand, pos)
        self.try_select_card_from_discard(player.discard, pos)
        self.try_select_card(player.goal[0], pos)

    def try_select_card_from_list(self, cards, pos):
        for card in cards:
            if card.rect.collidepoint(pos):
                self.set_active_card(card)
                print("Clicked on", card)
                return

    def try_select_card_from_discard(self, discard_piles, pos):
        for pile in discard_piles:
            if pile and pile[0].rect.collidepoint(pos):
                card = pile[-1]
                self.set_active_card(card)
                print("Clicked on discard", card)
                return

    def try_select_card(self, card, pos):
        if card.rect.collidepoint(pos):
            self.set_active_card(card)
            print("Clicked on", card)

    def set_active_card(self, card):
        self.activeCard = card
        self.orgX = card.rect.x
        self.orgY = card.rect.y

    def handle_mouse_up(self):
        if self.activeCard and self.game.currentTurn == self.playerId:
            data = self.game.playCard(self.activeCard)

            if data:
                self.game = self.network.send(data)
            else:
                self.activeCard.move(self.orgX, self.orgY)

            self.activeCard = None
            self.cardDrop.play()

    def handle_mouse_motion(self, rel):
        if self.activeCard:
            self.activeCard.rect.move_ip(rel)

# Create the instance of the main class
main_class = Display()

# Run the main loop
main_class.run()
