from tkinter import *
from tkinter.messagebox import showerror, showwarning
from abstract_window import AbstractWindow
from abstract_display_window import DisplayWindow
from structures import Item, Inventory
from creation_abstract_class import AskWindowSample


class ItemsList(AbstractWindow):
    def __init__(self, parent, title, msize, items, switcher: bool, inv):
        AbstractWindow.__init__(self, parent, title, msize)
        self.s = switcher
        self.items = items
        self.inv = inv
        if switcher:
            Button(self, text='Создать вещь', command=self.add_item).pack(fill=X, anchor=NW, expand=1)
            Button(self, text='Создать хранилище', command=self.add_inventory).pack(fill=X, anchor=NE, expand=1)
        self.create_list()

    def add_item(self):
        NewItemWindow(self, self.inv)
        self.update_listbox()

    def add_inventory(self):
        NewInventoryWindow(self, self.inv)
        self.update_listbox()

    def update_listbox(self):
        self.list.destroy()
        self.scroller.destroy()
        self.create_list()

    def create_list(self):
        self.list = Listbox(self, relief=SOLID, selectmode=SINGLE)
        self.scroller = Scrollbar(self, command=self.list.yview)
        self.list.config(yscrollcommand=self.scroller.set, font=('Arial', 20, 'normal'))
        self.scroller.pack(side=RIGHT, fill=Y)
        self.list.pack(expand=1, fill=BOTH)
        self.fill_list()
        self.list.bind('<Double-1>', lambda event: self.on_click())

    def fill_list(self):
        for itemname in self.items:
            if not isinstance(self.items[itemname]['instance'], Inventory):
                self.list.insert(END, itemname)
            else:
                self.list.insert(END, itemname)

    def delete_item(self, instance, item):
        instance.destroy()
        self.items.pop(item.name)
        self.update_listbox()

    def on_click(self):
        index = self.list.curselection()[0]
        itemname = self.list.get(index)
        instance = self.items[itemname]['instance']
        if isinstance(instance, Inventory):
            showwarning('Внимание!', 'Данная вещь является инвентарем и не может быть открыта в данном режиме,'
                                     ' постарайтесь открыть ее добавив в свой инвентарь')
            return
        ItemInfo(self, self.items[itemname]['instance'], self.s)


class ItemInfo(DisplayWindow):
    def __init__(self, parent, item: Item, switcher: bool):
        DisplayWindow.__init__(self, parent, f'Информация о: {item.name}', ('auto',),
                               item.name, f'Вес: {item.weight}', True, **item.stats)
        if switcher:
            Button(self, text='Удалить вещь',
                   command=lambda: parent.delete_item(self, item)).pack(side=RIGHT, pady=10, padx=10, anchor=N)


class NewItemWindow(AskWindowSample):
    def __init__(self, parent, place):
        super().__init__(parent, 'Новая вещь', (400, 700), [])
        self.create_entry_parameter_field('Название', str)
        self.create_entry_parameter_field('Вес', int)
        self.wait_window()
        self.create_item_object(place)

    def check_box(self):
        for key in self.result:
            if not self.result[key]:
                return 0
        return 1

    def create_item_object(self, inventory: Inventory):
        if self.check_box():
            name = self.result.pop('Название').title()
            if name in inventory.inventory:
                showerror('Ошибка', f'Вещь с названием {name} уже существует!')
                return
            weight = self.result.pop('Вес')
            inventory.put(Item(name, weight, **self.result))


class NewInventoryWindow(AskWindowSample):
    def __init__(self, parent, place):
        super().__init__(parent, 'Новое хранилище', (400, 700), ['Название', 'Объем'])
        self.create_entry_parameter_field('Название', str)
        self.create_entry_parameter_field('Объем', int)
        self.wait_window()
        self.create_inventory_object(place)

    def check_box(self):
        for key in self.result:
            if not self.result[key]:
                return 0
        return 1

    def create_inventory_object(self, inv: Inventory):
        if self.check_box():
            name = self.result.pop('Название').title()
            if name in inv.inventory:
                showerror('Ошибка', f'Вещь с названием {name} уже существует')
                return
            space = self.result.pop('Объем')
            inv.put(Inventory(name, space))
