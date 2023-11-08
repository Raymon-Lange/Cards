import random

class Game:
    def __init__(self):
        self.playerOne = Player("One")
        self.playerTwo = Player("Two")
        self.deck = Deck(2)
        self.field = [[]]
        self.discardPile = []

        self.deck.shuffle()

        for i in range(1,15):
            self.playerOne.goal.append(self.deck.deal())
            self.playerTwo.goal.append(self.deck.deal())

            while len(self.playerOne.hand) <= 5:
                self.playerOne.hand.append(self.deck.deal())


    def __str__(self):
        return str(self.playerOne)

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.discard = [[]]
        self.goal = []
    
    def __str__(self):
        playerInfo = "Player: {}\nCurrent Goal: {}\nCards left: {}\n".format(self.name, self.goal[0], len(self.goal))

        handInfo = "Hand: \n"
        for card in self.hand:
            handInfo += str(card) + "\n"

        return playerInfo + handInfo

class Deck:
    suits = ["hearts", "diamonds", "clubs", "spades"]
    ranks = ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"]

    def __init__(self, decks =1):
        self.cards = []

        for deck in range(1,decks):
            for suit in self.suits:
                for rank in self.ranks:
                    self.cards.append(Card(suit, rank))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

class Card:
  def __init__(self, suit, rank):
    self.suit = suit
    self.rank = rank

  def __str__(self):
    return f"{self.rank} of {self.suit}"


g = Game()
print(g)