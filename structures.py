from copy import deepcopy
# abstract class


class Item:
    def __init__(self, name, weight: int, *changeable, **stats):
        self.name = name
        self.weight = weight
        self.changeable = changeable
        self.stats = stats
        self.notes = ''


class Inventory:
    def __init__(self, name, space: int = 999999999):
        # Название хранилища
        self.name = name
        self.space: int = space
        self.inventory = {}
        self.weight = 0

    def weight_access_check(self, item_instance, change) -> bool:
        item_weight = item_instance.weight
        if self.get_abs_space() >= change * item_weight:
            return True
        else:
            return False

    def put(self, item, quantify=1):
        if self.name == 'MAIN':
            self.inventory[item.name] = {
                'instance': deepcopy(item),
                'quantify': 0
            }
            return
        if self.weight + item.weight * quantify <= self.space:
            try:
                self.inventory[item.name] = {
                    'instance': deepcopy(item),
                    'quantify': self.inventory[item.name]['quantify'] + quantify
                }
                self.recalculate_weight()
            except KeyError:
                self.inventory[item.name] = {
                    'instance': deepcopy(item),
                    'quantify': 1
                }
                self.recalculate_weight()

    def _find_inventories(self):
        for inv in self.inventory.values():
            if isinstance(inv["instance"], Inventory):
                inv["instance"].recalculate_weight()

    def recalculate_weight(self):
        self._find_inventories()
        new_weight: int = 0
        for key, value in self.inventory.items():
            for _ in range(self.inventory[key]['quantify']):
                new_weight += value["instance"].weight
        self.weight = new_weight

    def get_abs_space(self):
        item_weights = 0
        for item in self.inventory:
            item_weights += self.inventory[item]['instance'].weight * self.inventory[item]['quantify']
        return self.space - item_weights

    def get(self):
        return self.inventory


class Quest:
    def __init__(self, description: str, parent, award: list, name=None):
        self.name = name
        self.parent = parent
        self.desc = description
        self.award = award
        self.status = 1


class Achievement:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class Profile:
    def __init__(self, name, inventory: Inventory, **stats):
        self.name = name
        self.stats = stats
        self.inventory = inventory
        self.quests = []
        self.achievements = []

    def edit_stats(self, stats=None, **anotherstats):
        if stats:
            for key in stats:
                self.stats[key] = stats[key]
        else:
            for key in anotherstats:
                self.stats[key] = anotherstats[key]

    def add_achieve(self, achievement: Achievement):
        self.achievements.append(achievement)


class NotPlayerCharacter:
    def __init__(self, name, race, home, occupation):
        self.name = name
        self.race = race
        self.home = home
        self.occupation = occupation
        self.avatar = None

    def get_stats(self):
        return {'Имя': self.name, 'Раса': self.race, 'Где обитает': self.home, 'Чем занимается': self.occupation}
