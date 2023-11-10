import pygame
from Network import Network
from Game import *

# Create the window
window = pygame.display.set_mode((800, 600))

# Set the background color
window.fill((0, 100, 0))

# Create the main class
class Display:

    def __init__(self):
        self.window = window
        self.game = Board(0)

    def drawBoard(self):
        self.game.draw(window)


    def deal(self):
        self.game.play("deal::", 0)

    def play(self):
        self.game.play("deal::", 1)

    def run(self):
        clock = pygame.time.Clock()
        
        self.activeCard = None
        self.orgX = 0
        self.orgY = 0

        while True:

            clock.tick(60)
            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    if self.game.currentTurn == 0:
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

                    if self.game.currentTurn == 1:
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
                                self.game.play(data, self.game.currentTurn)
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


main_class.deal()
main_class.deal()
main_class.play()

# Run the main loop
main_class.run()
