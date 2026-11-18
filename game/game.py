from game.card import Card
from game.deck import Deck
from game.player import Player

class Game:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.discard = [] # Верхняя карта
        self.current_color = None # цвет, которым нужно ходить 
        self.turn = 0 # чей ход по индексу 
        self.direction = 1 # 1 - по часовой; -1 - против часовой 
        self.finished = False
        self.winner = None
        
    def start_game(self):
        self.deck.shuffle()
        for player in self.players:
            for card in self.deck.deal(7):
                player.take_card(card)
        
        # Стартавая карта, дикая не может быть первой
        card = self.deck.take()
        while card.is_wild():
            self.deck.put_back([card])
            self.deck.shuffle()
            card = self.deck.take()
        
        self.discard.append(card)
        self.current_color = card.color
        
        # Стартавая карта тоже рабочия 
        if card.value == "skip":
            self.next_turn()
        elif card.value == "reverse":
            self.direction = -1
        elif card.value == "draw2":
            self.give_cards(self.current_player(), 2)
            self.next_turn()
        
    def current_player(self):
        return self.players[self.turn]
    
    def top_card(self):
        return self.discard[-1]
    
    def next_turn(self):
        self.turn = (self.turn + self.direction) % len(self.players)
        
    def give_cards(self, player, count):
        for i in range(count):
            card = self.take_from_deck()
            if card is None:
                break
            player.take_card(card)
    
    def take_from_deck(self):
        card = self.deck.take()
        if card is not None:
            return card
        
        #конец колоды - перекладываем сброс 
        if len(self.discard) > 1:
            top = self.discard.pop()
            rest = self.discard
            self.discard = [top]
            self.deck.put_back(rest)
            self.deck.shuffle()
            return self.deck.take()
        return None
    
    def play_card(self, player, index, chosen_color = None):# None значит ход принят
        if self.finished:
            return "Партия уже закончена"
        if player is not self.current_player():
            return "Сейчас не твой ход"
        if index < 0 or index >= len(player.hand):
            return "Нет карты с таким номером"
        
        card = player.hand[index]
        if not card.can_play(self.top_card(), self.current_color):
            return "Эта карта не подходит"
        
        if card.is_wild() and chosen_color is None:
            return "Надо выбрать цвет"
        
        player.remove_card(index)
        self.discard.append(card)
        
        if card.is_wild():
            self.current_color = chosen_color
        else:
            self.current_color = card.color
            
        # кинул последния карта = победа
        if len(player.hand) == 0:
            self.finished = True
            self.winner = player
            return None
        
        self.apply_effect(card)
        return None
    
    def apply_effect(self, card):
        if card.value == "skip":
        # Пропуск победителя, два шага
            self.next_turn()
            self.next_turn()
        
        elif card.value == "reverse":
            self.direction = -1 * self.direction
            self.next_turn()
            # при двух игроках разворот работает как пропуск
            if len(self.players) == 2:
                self.next_turn()
                
        elif card.value == "draw2":
            self.next_turn()
            self.give_cards(self.current_player(), 2)
            self.next_turn()
        
        elif card.value == "wild4":
            self.next_turn()
            self.give_cards(self.current_player(), 4)
            self.next_turn()
            
        else:
            self.next_turn()
    
    def draw_card(self, player):
        if self.finished:
            return "Партия уже закончена"
        if player is not self.current_player():
            return "Сейчас не твой ход"
        
        card = self.take_from_deck()
        if card is None:
            return "Колода пуста"
        
        player.take_card(card)
        return None
    
    def pass_turn(self, player):
        # игрок взял карту и решил не ходить 
        if player is not self.current_player():
            return "Сейчас не твой ход"
        self.next_turn()
        return None
    
    def say_uno(self, player):
        player.said_uno = True 
        
    def catch_uno(self, target):
        # не сказла UNO осталось одна карта
        if len(target.hand) == 1 and not target.said_uno:
            self.give_cards(target, 2)
            return True
        return False
    
    def state_dict(self):
        players = []
        for p in self.players:
            players.append(p.to_dict())
        
        winner = None
        if self.winner is not None:
            winner = self.winner.name
            
        return {
            "players": players,
            "top": self.top_card().to_dict(),
            "color": self.current_color,
            "turn": self.turn,
            "direction": self.direction,
            "finished": self.finished,
            "winner": winner,
            "deck": self.deck.left(),
        }
    
    def hand_list(self, player):
        # руку отдаём только её владельцу
        cards = []
        for card in player.hand:
            cards.append(card.to_dict())
        return cards
    

if __name__ == "__main__":
    p1 = Player(1, "Аня")
    p2 = Player(2, "Богдан")
    game = Game([p1, p2])
    game.start_game()

    print(f"Стартовая карта: {game.top_card()}, цвет: {game.current_color}")

    steps = 0
    while not game.finished and steps < 200:
        steps += 1
        player = game.current_player()

        # ищем первую подходящую карту
        index = -1
        for i in range(len(player.hand)):
            if player.hand[i].can_play(game.top_card(), game.current_color):
                index = i
                break

        if index == -1:
            error = game.draw_card(player)
            if error is not None:
                print("Ошибка:", error)
                break
            print(f"{player.name} берёт карту")
            game.pass_turn(player)
        else:
            card = player.hand[index]
            color = None
            if card.is_wild():
                color = "red"
            error = game.play_card(player, index, color)
            if error is not None:
                print("Ошибка:", error)
                break
            print(f"{player.name} кладёт {card}")

    if game.finished:
        print(f"Победил {game.winner.name} за {steps} ходов")
    else:
        print("За 200 ходов партия не закончилась")