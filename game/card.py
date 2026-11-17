SPECIAL_POINTS = {"skip": 20, "reverse": 20, "draw2": 20, "wild": 50, "wild4": 50}

COLOR_NAMES = {
    "red": "красная",
    "yellow": "жёлтая",
    "green": "зелёная",
    "blue": "синяя",
    "black": "чёрная",
}

VALUE_NAMES = {
    "skip": "пропуск",
    "reverse": "разворот",
    "draw2": "+2",
    "wild" : "дикая",
    "wild4": "дикая +4"
}

class Card:
    def __init__(self, color, value):
        self.color = color # red, yellow, green, blue, black
        self.value = value # "0" - "9" skip, reverse, draw2, wild, wild4
    
    def points(self): # Проверка на спец карты или цифры
        if self.value in SPECIAL_POINTS:
            return SPECIAL_POINTS[self.value]
        return int(self.value)
    
    def is_wild(self):
        return self.color == "black"
    
    def can_play(self, top_card, current_color): #дикую карту можно класть всегда
        if self.is_wild():
            return True
        
        if self.color == current_color:
            return True
        
        if self.value == top_card.value:
            return True
        
        return False
    
    def to_dict(self):
        return {"color": self.color, "value": self.value}
    
    def __str__(self):
        color = COLOR_NAMES.get(self.color, self.color)
        value = VALUE_NAMES.get(self.value, self.value)
        return f"{color} {value}"

if __name__ == "__main__":
    top = Card("red", "7")
    print(top, "-", top.points(), "очков")
    print(Card("red", "3").can_play(top, "red")) # True: цвет
    print(Card("blue", "7").can_play(top, "red")) # True: число
    print(Card("blue", "3").can_play(top, "red")) # False: нет совподений 
    