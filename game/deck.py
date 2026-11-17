import random 
from game.card import Card

COLORS = ["red", "yellow", "green", "blue"]
ACTION = ["skip", "reverse", "draw2"]

class Deck:
    def __init__(self):
        self.cards = []
        self.build()
    
    def build(self): #растановка какрт по цветам на каждый по 25 и 8 чёрных
        self.cards = []
        for color in COLORS:
            self.cards.append(Card(color, "0"))
            for number in range(1 , 10):
                self.cards.append(Card(color, str(number)))
                self.cards.append(Card(color, str(number)))
        
            for action in ACTION:
                self.cards.append(Card(color, action))
                self.cards.append(Card(color, action))
        
        for wild in ["wild", "wild4"]:
            for i in range(4):
                self.cards.append(Card("black", wild))
    
    def shuffle(self): # Перемешивание
        random.shuffle(self.cards)
    
    def deal(self, count):
        hand = []
        for i in range(count):
            card = self.take()
            if card is not None:
                hand.append(card)
        return hand
    
    def take(self): #брать карту сверху колоды 
        if len(self.cards) == 0: 
            return None
        return self.cards.pop()
    
    def put_back(self, cards):
        for card in cards:
            self.cards.append(card)
            
    def left(self):
        return len(self.cards)
    
if __name__ == "__main__":
    deck = Deck()
    print(f"Собрали колоду: {deck.left()} карт")
    deck.shuffle()
    hand = deck.deal(7)
    print(f"Раздали семь, осталось: {deck.left()}")
    for card in hand:
        print ("  ", card)
    print(f"Сверху колоды лежит: {deck.take()}")
    print(f"После добора осталось: {deck.left()}") 
        
        