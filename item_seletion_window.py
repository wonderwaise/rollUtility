from tkinter import *
from abstract_window import AbstractWindow


class ItemSelectionWindow(AbstractWindow):
    def __init__(self, parent, title, inventory):
        AbstractWindow.__init__(self, parent, title, ('auto',))
        self.all_items = {x.name: x for x in inventory.inventory}
        self.unselected_items = [x.name for x in inventory.inventory]
        self.selected_items = []
        self.create_lists()

    def create_lists(self):
        self.unselected = Listbox(self, height=20, selectmode=SINGLE, relief=SOLID)
        self.unselected.grid(row=0, column=0)
        self.unselected.bind('<Double-1>', lambda event: self.add_to(self.selected))

        self.selected = Listbox(self, height=20, selectmode=SINGLE, relief=SOLID)
        self.selected.grid(row=0, column=1)
        self.selected.bind('<Double-1>', lambda event: self.add_to(self.unselected))

        self.fill_master_list()
        self.fill_selected_list()

    def destroy_lists(self):
        self.unselected.destroy()
        self.selected.destroy()
        self.create_lists()

    def fill_master_list(self):
        for item in self.unselected_items:
            self.unselected.insert(END, item)

    def fill_selected_list(self):
        for item in self.selected_items:
            self.selected.insert(END, item)

    def add_to(self, to):
        try:
            if to is self.unselected:
                item = self.selected.get(self.selected.curselection()[0])
                self.selected_items.remove(item)
                self.unselected_items.append(item)
            else:
                item = self.unselected.get(self.unselected.curselection()[0])
                self.unselected_items.remove(item)
                self.selected_items.append(item)
            self.destroy_lists()
        except IndexError:
            pass
