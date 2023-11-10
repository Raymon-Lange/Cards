import random
import pygame
from os.path import isfile, join

class Board:
    def __init__(self, id):
        #Game State
        self.id = id
        self.ready = False
        self.currentTurn = 0 # either zero or one 

        self.displayedCard = []

        self.activeCard = None


        #Game Objects
        self.playerOne = Player("One")
        self.playerTwo = Player("Two")
        self.deck = Deck(2)
        self.field = [[],[],[],[]]
        self.discardPile = []

        self.deck.shuffle()

        print(len(self.deck.cards))

        for i in range(1,15):
            self.play("start::", 0)
            self.play("start::", 1)

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
    
    def checkValidMove(self, card):
        pass

    def play(self,data, playerId):

        action, value, location = data.split(':')

        if action == "deal":
            self.dealPlayer(playerId)
        if action == "start":
            self.startGame(playerId)
        if action == "discard":
            self.discard(value, location, playerId)
            self.currentTurn = (self.currentTurn + 1) % 2
            self.dealPlayer(self.currentTurn)
        if action == "move":
            self.move(value, location, playerId)


    def startGame(self, playerId):
        if playerId == 0:
            self.playerOne.goal.append(self.deck.deal())
            index = len(self.playerOne.goal) - 1
            self.playerOne.goal[index].rect.x = 25
            self.playerOne.goal[index].rect.y = 50
        if playerId == 1:
            self.playerTwo.goal.append(self.deck.deal())
            index = len(self.playerTwo.goal) - 1
            self.playerTwo.goal[index].rect.x = 25
            self.playerTwo.goal[index].rect.y = 470

    def dealPlayer(self, playerId):
        if playerId == 0:
            while len(self.playerOne.hand) != 5:
                self.playerOne.hand.append(self.deck.deal())

            for num, card in enumerate(self.playerOne.hand):
                index = num
                x = 140 + (81 * index)
                y = 50
                card.rect.x = x
                card.rect.y = y
        if playerId == 1:
            while len(self.playerTwo.hand) != 5:
                self.playerTwo.hand.append(self.deck.deal())

            for num, card in enumerate(self.playerTwo.hand):
                index = num
                x = 140 + (81 * index)
                y = 470
                card.rect.x = x
                card.rect.y = y

    def discard(self, value, location , playerId):
        print(value)
        if playerId == 0:
            x = 80
            y = 155
            for card in self.playerOne.hand:
                if str(card) == value:
                    x += 91 * (int(location)+1)
                    card.move(x,y)
                    self.playerOne.discard[int(location)].append(card)
                    self.playerOne.hand.remove(card)
        if playerId == 1:
            x = 80
            y = 365
            for card in self.playerTwo.hand:
                if str(card) == value:
                    x += 91 * (int(location)+1)
                    card.move(x,y)
                    self.playerTwo.discard[int(location)].append(card)
                    self.playerTwo.hand.remove(card)

    def move(self, value, location, playerId):
        if playerId == 0:
            x = 50
            y = 260
            for card in self.playerOne.hand:
                if str(card) == value:
                    x += 91 * (int(location)+1)
                    card.move(x,y)
                    self.field[int(location)].append(card)
                    self.playerOne.hand.remove(card)
                    
            x = 50        
            if str(self.playerOne.goal[0]) == value:
                card = self.playerOne.goal[0]
                x += 91 * (int(location)+1)
                card.move(x,y)
                self.field[int(location)].append(card)
                self.playerOne.goal.remove(card)

            x = 50
            for discardPile in self.playerOne.discard:
                if len(discardPile) > 0:
                        card = discardPile[len(discardPile)-1]
                        if str(card) == value:
                            x += 91 * (int(location)+1)
                            card.move(x,y)
                            self.field[int(location)].append(card)
                            discardPile.remove(card)
                        

        
        if playerId == 1:
            x = 50
            y = 260
            for card in self.playerTwo.hand:
                if str(card) == value:
                    x += 91 * (int(location)+1)
                    card.move(x,y)
                    self.field[int(location)].append(card)
                    self.playerTwo.hand.remove(card)

            x = 50
            if str(self.playerTwo.goal[0]) == value:
                card = self.playerTwo.goal[0]
                x += 91 * (int(location)+1)
                card.move(x,y)
                self.field[int(location)].append(card)
                self.playerTwo.goal.remove(card)

            x = 50
            for discardPile in self.playerTwo.discard:
                if len(discardPile) > 0:
                        card = discardPile[len(discardPile)-1]
                        if str(card) == value:
                            x += 91 * (int(location)+1)
                            card.move(x,y)
                            self.field[int(location)].append(card)
                            discardPile.remove(card)


    def playCard(self, card):

        #STEP: than check the field
        fieldY = 260
        x = 50

        for num, field in enumerate(self.field):
            x += 20+71
            if len(field) == 0:
                if pygame.Rect(x,fieldY,71,94).colliderect(card.rect):
                    if card.rank == "King" or card.rank == "Ace":
                        return "move:"+ str(card)+":"+str(num)
            else:
                if field[0].rect.colliderect(card.rect):
                    cardCount = len(field)-1
                    if self.deck.ranks.index(card.rank) - cardCount == 1 or card.rank == "King":
                        return "move:"+ str(card)+":"+str(num)        

        #STEP: Check for first player
        if self.currentTurn == 0:
            #STEP: First check to see if we discarded a card
            discardY = 155
            x = 80
            for num, discardPile in enumerate(self.playerOne.discard):
                x += 20 + 71 
                if len(discardPile) == 0:
                    if pygame.Rect(x,discardY, 71,94).colliderect(card.rect):
                        return "discard:"+ str(card)+":"+str(num)
                else:
                    if discardPile[0].rect.colliderect(card.rect):
                        return "discard:"+ str(card)+":"+str(num)
                    
                        
        if self.currentTurn == 1:
             #STEP: First check to see if we discarded a card
            discardY = 365
            x = 80
            for num, discardPile in enumerate(self.playerTwo.discard):
                x += 20 + 71 
                if len(discardPile) == 0:
                    if pygame.Rect(x,discardY, 71,94).colliderect(card.rect):
                        return "discard:"+ str(card)+":"+str(num)
                else:
                    if discardPile[0].rect.colliderect(card.rect):
                        return "discard:"+ str(card)+":"+str(num)
                    

        return None
    

    def __str__(self):
        return str(self.playerOne) + "\n " + str(self.playerTwo)
    
    def draw(self, screen):

        #STEP: Repaint the background
        screen.fill((0,100,0))

        ySpaceing = 105

        #STEP: Draw Player One
        x = 25
        y = 50

        self.playerOne.goal[0].draw(screen,90)

        x = 50

        for card in range(0,5):
            x += 12 + 71 
            if len(self.playerOne.hand) > card:
                self.playerOne.hand[card].draw(screen)
            #else:
            #    pygame.draw.rect(screen, (0, 255, 0), (x,y,71,94), 2)

        x = 80
        y += ySpaceing

        for card in self.playerOne.discard:
            x += 20 + 71 
            if len(card) == 0:
                pygame.draw.rect(screen, (0, 255, 0), (x,y,71,94), 2)
            else:
                card[len(card)-1].draw(screen)

        # Draw the field
        x = 50
        y += ySpaceing
        
        for card in self.field:
            x += 20 + 71 
            if len(card) == 0:
                pygame.draw.rect(screen, (0, 255, 0), (x,y,71,94), 2)
            else:
                card[len(card)-1].draw(screen)


        #STEP: Draw Player Two
        x = 80
        y += ySpaceing

        for card in self.playerTwo.discard:
            x += 20 + 71 
            if len(card) == 0:
                pygame.draw.rect(screen, (0, 255, 0), (x,y,71,94), 2)
            else:
                card[len(card)-1].draw(screen)


        x = 25
        y += ySpaceing

        self.playerTwo.goal[0].draw(screen,90)

        x = 50

        for card in range(0,5):
            x += 20 + 71 
            if len(self.playerTwo.hand) > card:
                self.playerTwo.hand[card].draw(screen)

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
        self.ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

        for deck in range(0,decks):
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
        self.rect = self.image.get_rect()
  
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def move(self, x, y):
        self.rect.x = x
        self.rect.y = y
    
    def draw(self,screen, rotate =0):
        rotated_image = pygame.transform.rotate(self.image, rotate)
        screen.blit(rotated_image, self.rect)
