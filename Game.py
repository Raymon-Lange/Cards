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
        pass

    def __str__(self):
        return str(self.playerOne)
    
    def draw(self, screen):
        screen.fill((0,100,0))

        # Set the border color
        border_color = (0, 0, 0)
        # Set the border width
        border_width = 5
        # Draw the rectangle
        pygame.draw.rect(screen, border_color, (50, 50, 50, 100), border_width)

        

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.discard = [[],[],[],[]]
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
        self.suits = ["hearts", "diamonds", "clubs", "spades"]
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

class Card:
  def __init__(self, suit, rank):
    self.suit = suit
    self.rank = rank

    self.image = pygame.image.load(join("assets", suit, suit+rank+"png"))

  def __str__(self):
    return f"{self.rank} of {self.suit}"
