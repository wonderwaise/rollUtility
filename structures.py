# abstract class
class Item:
    def __init__(self, name, weight: int, *changeable, **stats):
        self.name = name
        self.weight = weight
        self.changeable = changeable
        self.stats = stats


class Inventory:
    def __init__(self, name, space: int = 999999):
        # Название хранилища
        self.name = name
        self.space: int = space
        self.inventory = {}
        self.weight = 0

    def put(self, item: Item, quantify=1):
        if self.name == 'MAIN':
            self.inventory[item.name] = {
                'instance': item,
                'quantify': 0
            }
            return
        if self.weight + item.weight * quantify <= self.space:
            try:
                self.inventory[item.name] = {
                    'instance': item,
                    'quantify': self.inventory[item.name]['quantify'] + quantify
                }
            except KeyError:
                self.inventory[item.name] = {
                    'instance': item,
                    'quantify': 1
                }

    def get_abs_space(self):
        item_weights = 0
        for item in self.inventory:
            item_weights += self.inventory[item]['instance'].weight * self.inventory[item]['quantify']
        return self.space - item_weights

    def get(self):
        return self.inventory


class Quest:
    def __init__(self, description: str, parent, award: list, name=None, **kwargs):
        self.name = name
        self.parent = parent
        self.desc = description
        self.award = award


class Achievement:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class Profile:
    def __init__(self, name, inventory: Inventory, abcventory: Inventory, **stats):
        self.name = name
        self.stats = stats
        self.inventory = inventory
        self.abcventory = abcventory
        self.quests = []
        self.achievements = []

    def edit_stats(self, stats=None, **anotherstats):
        if stats:
            for key in stats:
                self.stats[key] = stats[key]
        else:
            for key in anotherstats:
                self.stats[key] = anotherstats[key]

    # REWORK ++++++++ FOR LOOP IN

    def add_achieve(self, achievement: Achievement):
        self.quests.append(achievement)


class NotPlayerCharacter:
    def __init__(self, name, race, home, occupation):
        self.name = name
        self.race = race
        self.home = home
        self.occupation = occupation
        self.avatar = None

    def get_stats(self):
        return {'Name': self.name, 'Race': self.race, 'Home': self.home, 'Occupation': self.occupation}

    @staticmethod
    def update_avatar():
        print('NOT IMPLEMENTED')
