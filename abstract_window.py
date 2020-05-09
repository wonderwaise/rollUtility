from tkinter import *


class AbstractWindow(Toplevel):
    def __init__(self, parent, title: str, mgeo: tuple):
        Toplevel.__init__(self, parent)
        self.title(title)
        self.grab_set()
        if mgeo != ('auto',):
            self.maxsize(*mgeo)
