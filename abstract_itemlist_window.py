from tkinter import *
from abstract_window import AbstractWindow
from abstract_display_window import DisplayWindow
from structures import Item


class ItemsList(AbstractWindow):
    def __init__(self, parent, title, msize, items, switcher: bool):
        AbstractWindow.__init__(self, parent, title, msize)
        self.s = switcher
        self.items = items
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
        for item in self.items:
            self.list.insert(END, f'[{item.name}]')

    def delete_item(self, instance, item):
        instance.destroy()
        self.items.remove(item)
        self.list.destroy()
        self.scroller.destroy()
        self.create_list()

    def on_click(self):
        index = self.list.curselection()[0]
        item = self.items[index]
        ItemInfo(self, item, self.s)


class ItemInfo(DisplayWindow):
    def __init__(self, parent, item: Item, switcher: bool):
        DisplayWindow.__init__(self, parent, f'Info about: {item.name}', ('auto',),
                               item.name, f'Weight: {item.weight}', True, **item.stats)
        self.item = item
        if switcher:
            Button(self, text='Delete Item132',
                   command=lambda: parent.delete_item(self, self.item)).pack(side=RIGHT, pady=10, padx=10, anchor=N)
