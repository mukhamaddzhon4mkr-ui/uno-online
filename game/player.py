from game.card import Card 

class Player:
    def __init__(self, user_id, name):
        self.user_id = user_id # id из таблиы users
        self.name = name
        self.hand = [] # карты на руках 
        self.said_uno = False # сказл UNO 
        
    def take_card(self, card): #
        if card is None: # Ответ колода пустая, если она пуста
            return False
        self.hand.append(card) # Взял каруту - флаг UNO сбрасываеться
        self.said_uno = False 
        return True
    
    def remove_card(self, index):
        # номер пришёл от клиента — проверяем, что такая карта есть
        if index < 0 or index >= len(self.hand):
            return None
        return self.hand.pop(index)
            
    def has_playable(self, top_card, current_color):
        for card in self.hand:
            if card.can_play(top_card, current_color):
                return True
        return False
    
    def hand_points(self):
        total = 0
        for card in self.hand:
            total += card.points()
        return total
    
    def to_dict(self):
        # Скрывамаем какие какрты у других игроков, кроме кол-во
        return {
            "user_id": self.user_id,
            "name": self.name,
            "count": len(self.hand),
            "said_uno": self.said_uno
        }
    
    def __str__(self):
        return f"{self.name}: {len(self.hand)} карт"

if __name__ == "__main__":
    from game.deck import Deck
    
    deck = Deck()
    deck.shuffle()
    
    player = Player(1, "Аня")
    for card in deck.deal(3):
        player.take_card(card)
        
    print(player)
    print(f"Очков на руке: {player.hand_points()}")
    
    top = deck.take()
    print(f"Верхняя карта: {top}")
    print(f"Есть чем ходить по красному: {player.has_playable(top, 'red')}")
    
    dropped = player.remove_card(0)
    print(f"Сбросили: {dropped}")
    print(player)