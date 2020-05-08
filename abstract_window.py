from tkinter import *


class AbstractWindow(Toplevel):
    def __init__(self, parent, title: str, geo: str):
        Toplevel.__init__(self, parent)
        self.title(title)
        self.grab_set()
        if geo != 'auto':
            self.geometry(geo)
