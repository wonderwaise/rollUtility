from creation_abstract_class import AskWindowSample


class Inventory:
    def __init__(self, name, space: int = 99999):
        # Название хранилища
        self.name = name
        self.space: int = space
        self.inventory = []
        self.weight = 0

    def put(self, item):
        if self.name == 'MAIN':
            self.inventory.append(item)
            return
        if self.weight + item.weight <= self.space:
            self.inventory.append(item)

    def get(self):
        return self.inventory


class Quest:
    def __init__(self, description: str, parent, award: list, name=None, **kwargs):
        self.name = name
        self.parent = parent
        self.desc = description
        self.award = award


# abstract class
class Item:
    def __init__(self, name, weight: int, *changeable, **stats):
        self.name = name
        self.weight = weight
        self.changeable = changeable
        self.stats = stats

    def __str__(self):
        return self.name



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

























