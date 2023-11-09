import random
import pygame
from os.path import isfile, join

class Board:
    def __init__(self, id):
        #Game State
        self.id = id
        self.ready = False
        self.currentTurn = 0 # either zero or one 


        #Game Objects
        self.playerOne = Player("One")
        self.playerTwo = Player("Two")
        self.deck = Deck(2)
        self.field = [[],[],[],[]]
        self.discardPile = []

        self.deck.shuffle()

        for i in range(1,15):
            self.playerOne.goal.append(self.deck.deal())
            self.playerTwo.goal.append(self.deck.deal())


        if self.deck.compare(self.playerOne.goal[0], self.playerTwo.goal[0]):
            self.currentTurn = 0
        else:
            self.currentTurn = 1


    def connected(self):
        return self.ready
    
    def whoTurn(self):
        return self.currentTurn
    
    def reset(self):
        pass
    
    def play(self,data):
        self.field[0].append(self.deck.deal())

    def endTurn(self):
        if self.currentTurn == 0:
            while len(self.playerOne.hand) != 4:
                self.playerOne.hand.append(self.deck.deal())
            self.currentTurn = 1
        else:
            while len(self.playerTwo.hand) != 4:
                self.playerTwo.hand.append(self.deck.deal())
            self.currentTurn = 0
        

    def __str__(self):
        return str(self.playerOne)
    
    def draw(self, screen):
        screen.fill((0,100,0))

        ySpaceing = 105

        #STEP: Draw Player One
        x = 25
        y = 50

        self.playerOne.goal[0].draw(screen, x,y,90)

        x = 50

        for card in range(0,4):
            x += 20 + 71 
            if len(self.playerOne.hand) > card:
                self.playerOne.hand[card].draw(screen, x,y)
            else:
                pygame.draw.rect(screen, (0, 255, 0), (x,y,71,94), 2)

        x = 50
        y += ySpaceing

        for card in self.playerOne.discard:
            x += 20 + 71 
            if len(card) == 0:
                pygame.draw.rect(screen, (0, 255, 0), (x,y,71,94), 2)


        # Draw the field
        x = 50
        y += ySpaceing
        
        for card in self.field:
            x += 20 + 71 
            if len(card) == 0:
                pygame.draw.rect(screen, (0, 255, 0), (x,y,71,94), 2)
            else:
                card[len(card)-1].draw(screen,x,y)

        #STEP: Draw Player 2 
        x = 50
        y += ySpaceing

        for card in self.playerTwo.discard:
            x += 20 + 71 
            if len(card) == 0:
                pygame.draw.rect(screen, (0, 255, 0), (x,y,71,94), 2)


        x = 25
        y += ySpaceing
        
        self.playerTwo.goal[0].draw(screen, x,y,90)

        x = 50

        for card in range(0,4):
            x += 20 + 71 
            if len(self.playerTwo.hand) > card:
                self.playerTwo.hand[card].draw(screen, x,y)
            else:
                pygame.draw.rect(screen, (0, 255, 0), (x,y,71,94), 2)
        


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.discard = [[],[],[],[],]
        self.goal = []
    
    def __str__(self):
        playerInfo = "Player: {}\nCurrent Goal: {}\nCards left: {}\n".format(self.name, self.goal[0], len(self.goal))

        handInfo = "Hand: \n"
        for card in self.hand:
            handInfo += str(card) + "\n"

        return playerInfo + handInfo

class Deck:
    def __init__(self, decks =1):
        self.cards = []
        self.suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        self.ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"]

        for deck in range(1,decks):
            for suit in self.suits:
                for rank in self.ranks:
                    self.cards.append(Card(suit, rank))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()
    
    def compare(self, cardOne, cardTwo):
        if self.ranks.index(cardOne.rank) < self.ranks.index(cardTwo.rank):
            return True
        return False

class Card(pygame.sprite.Sprite):
    '''
    A card size is 71 X 94
    '''
    def __init__(self, suit, rank):
        super().__init__()
        self.suit = suit
        self.rank = rank

        self.image = pygame.image.load(join("assets", suit, suit+rank+".png"))
  
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def draw(self,screen, x, y, rotate =0):
        rotated_image = pygame.transform.rotate(self.image, rotate)
        screen.blit(rotated_image, (x,y))
