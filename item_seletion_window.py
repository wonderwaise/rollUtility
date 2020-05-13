from tkinter import *
from abstract_window import AbstractWindow


class ItemSelectionWindow(AbstractWindow):
    def __init__(self, parent, title, inventory):
        AbstractWindow.__init__(self, parent, title, ('auto',))
        self.all_items = inventory.inventory
        self.unselected_items = [x for x in inventory.inventory]
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
        for itemname in self.unselected_items:
            self.unselected.insert(END, itemname)

    def fill_selected_list(self):
        for itemname in self.selected_items:
            self.selected.insert(END, itemname)

    def add_to(self, to):
        try:
            if to is self.unselected:
                itemname = self.selected.get(self.selected.curselection()[0])
                self.selected_items.remove(itemname)
                self.unselected_items.append(itemname)
            else:
                itemname = self.unselected.get(self.unselected.curselection()[0])
                self.unselected_items.remove(itemname)
                self.selected_items.append(itemname)
            self.destroy_lists()
        except IndexError:
            pass
