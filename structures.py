from creation_abstract_class import AskWindowSample


class Inventory:
    def __init__(self, name, space: int = 99999):
        # Название хранилища
        self.name = name
        self.space: int = space
        self.inventory = []
        self.weight = 0

    def put(self, item):
        if self.weight + item.weight <= self.space:
            self.inventory.append(item)


class Quest:
    def __init__(self, description: str, parent, award: list, name=None, **kwargs):
        self.name = name
        self.parent = parent
        self.desc = description
        self.award = award


# abstract class
class Item:
    def __init__(self, name, place: Inventory, weight: int):
        self.name = name
        self.place = place
        self.weight = weight


class AbstractItem(Item):
    def __init__(self, name, place, weight, description, *changeable, **stats):
        super().__init__(name, place, weight)
        self.change = changeable
        self.desc = description
        self.stats = stats


class NonAbstractItem(Item):
    def __init__(self, name, place, weight, description, *changeable, **stats):
        super().__init__(name, place, weight)
        self.desc = description
        self.change = changeable
        self.stats = stats


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

    def add_quest(self, parent):
        add_quest_window = AskWindowSample(parent, 'New Quest', '400x700', [], 4)
        for parameter in ['Name', 'Description', 'Given by', 'Award']:
            add_quest_window.create_parameter_field(parameter, str)
        add_quest_window.wait_window()
        try:
            result = add_quest_window.box
            self.quests.append(Quest(result['Description'], result['Given by'], result['Award'], result['Name']))
        except KeyError:
            pass

    def add_achieve(self, achievement: Achievement):
        self.quests.append(achievement)

    def close_quest(self, quest: Quest):
        for item in quest.award:
            if isinstance(item, NonAbstractItem):
                self.inventory.put(item)
            else:
                self.abcventory.put(item)
        self.quests.remove(quest)
























