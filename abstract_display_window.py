from abstract_window import AbstractWindow
from tkinter import *


class DisplayWindow(AbstractWindow):
    def __init__(self, parent, title: str, geo: str, name, core, automation: bool, **displayable):
        AbstractWindow.__init__(self, parent, title, geo)
        self.parameters = displayable
        self.row = 0

        self.header = Frame(self)
        self.header.pack(fill=X, padx=20)
        for text in name, core:
            Label(self.header, text=text, font=('Times New Roman', 25, 'bold')).pack(side=LEFT, padx=10, expand=1)

        self.container = Frame(self)
        self.container.pack(padx=20, pady=10, fill=BOTH, expand=1, side=LEFT)

        if automation:
            self.__iterate_strings()

    def __iterate_strings(self):
        for parameter in self.parameters:
            self.display_row(parameter, self.parameters[parameter])

    def display_row(self, key, value, *, font='Times New Roman', width=15, height=2, font_size=15):
        for num, text in enumerate([key, value]):
            Label(self.container, text=text, width=width, height=height,
                  font=(font, font_size, 'normal')).grid(row=self.row, column=num)
        self.row += 1
