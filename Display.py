import pygame
from Network import Network
from Game import *
import sys,os

# Create the window
window = pygame.display.set_mode((800, 600))

# Set the background color
window.fill((0, 100, 0))

# Create the main class
class Display:

    def __init__(self):
        self.window = window
        #self.game = Board(0)
        pygame.init()
        
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
                self.drawCard(card[len(card)-1])


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

        text = "Current Turn \n Player {}".format(self.game.currentTurn+1)
        text_surface = self.font.render(text, True, white)
        text_rect = text_surface.get_rect()
        text_rect.center = (550+((800-540)//2), 75)
        self.window.blit(text_surface, text_rect)

        text = "Waiting for\n Player {}".format(not self.game.ready)
        text_surface = self.font.render(text, True, white)
        text_rect = text_surface.get_rect()
        text_rect.center = (550+((800-540)//2), 120)
        self.window.blit(text_surface, text_rect)


    def run(self):
        clock = pygame.time.Clock()

        network = Network()
        self.playerId = int(network.getId())

        print("You are player", self.playerId)
        
        self.activeCard = None
        self.orgX = 0
        self.orgY = 0

        try:
            self.game = network.send("get")
            print(sys.getsizeof(self.game))
        except:
            run = False
            print("Couldn't get game")
            exit()


        while True:

            clock.tick(60)

            if self.game.currentTurn != self.playerId:
                self.game = network.send("get")
            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    if self.playerId == 0:
                        if self.activeCard == None:
                            for num, card in enumerate(self.game.playerOne.hand):
                                if card.rect.collidepoint(event.pos):
                                    print("Clicked on", card)
                                    self.activeCard = card
                                    self.orgX = card.rect.x
                                    self.orgY = card.rect.y

                            for discardPile in self.game.playerOne.discard:
                                if len(discardPile) > 0:
                                    if discardPile[0].rect.collidepoint(event.pos):
                                        card = discardPile[len(discardPile)-1]
                                        print("Clicked on", card)
                                        self.activeCard = card
                                        self.orgX = card.rect.x
                                        self.orgY = card.rect.y
                            
                            if self.game.playerOne.goal[0].rect.collidepoint(event.pos):
                                    card = self.game.playerOne.goal[0]
                                    print("Clicked on", card)
                                    self.activeCard = card
                                    self.orgX = card.rect.x
                                    self.orgY = card.rect.y

                    if self.playerId == 1:
                        if self.activeCard == None:
                            for num, card in enumerate(self.game.playerTwo.hand):
                                if card.rect.collidepoint(event.pos):
                                    print("Clicked on", card)
                                    self.activeCard = card
                                    self.orgX = card.rect.x
                                    self.orgY = card.rect.y

                            for discardPile in self.game.playerTwo.discard:
                                if len(discardPile) > 0:
                                    if discardPile[0].rect.collidepoint(event.pos):
                                        card = discardPile[len(discardPile)-1]
                                        print("Clicked on discared", card)
                                        self.activeCard = card
                                        self.orgX = card.rect.x
                                        self.orgY = card.rect.y
                                
                            if self.game.playerTwo.goal[0].rect.collidepoint(event.pos):
                                    card = self.game.playerTwo.goal[0]
                                    print("Clicked on", card)
                                    self.activeCard = card
                                    self.orgX = card.rect.x
                                    self.orgY = card.rect.y                               


            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                        if self.activeCard != None:
                                    
                            data = self.game.playCard(self.activeCard)

                            if data:
                                #self.game.play(data, self.game.currentTurn) saved for local mode
                                self.game = network.send(data)
                            else:
                                self.activeCard.move(self.orgX, self.orgY)
                            
                            self.activeCard = None


            if event.type == pygame.MOUSEMOTION:
                if self.activeCard != None:
                    #if event.rel[0] > 1 or event.rel[0] < -1 and event.rel[1] > 1 or event.rel[1] < -1:
                        self.activeCard.rect.move_ip(event.rel)

            self.drawBoard()

            # Update the window
            pygame.display.update()

# Create the instance of the main class
main_class = Display()


#main_class.deal()
#main_class.deal()
#main_class.play()

# Run the main loop
main_class.run()
