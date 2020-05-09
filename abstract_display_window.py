from abstract_window import AbstractWindow
from tkinter import *


class DisplayWindow(AbstractWindow):
    def __init__(self, parent, title: str, mgeo: tuple, name, core, automation: bool, **displayable):
        AbstractWindow.__init__(self, parent, title, mgeo)
        self.parameters = displayable
        self.row = 0

        self.header = Frame(self)
        self.container = Frame(self, bg='green')
        self.canvas = Canvas(self.container)
        self.frame_inside = Frame(self.canvas)
        self.scroller = Scrollbar(self, command=self.canvas.yview)

        self.header.pack(fill=X, padx=20)
        self.create_header(name, core)
        self.create_canvas()

        if automation:
            self.__iterate_strings()

    def create_header(self, name, core):
        for text in name, core:
            Label(self.header, text=text, font=('Times New Roman', 25, 'bold')).pack(side=LEFT, padx=10, expand=1)

    def create_canvas(self):
        self.frame_inside.bind('<Configure>',
                               lambda event: self.canvas.config(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.frame_inside, anchor=NW)
        self.canvas.config(yscrollcommand=self.scroller.set)
        self.container.pack(side=LEFT, expand=1, padx=10, pady=10)
        self.scroller.pack(fill=Y, side=RIGHT)
        self.canvas.pack(side=LEFT, expand=1, fill=BOTH)

    def __iterate_strings(self):
        for parameter in self.parameters:
            print('1')
            self.display_row(parameter, self.parameters[parameter])

    def display_row(self, key, value, *, font='Times New Roman', width=15, height=2, font_size=15):
        for num, text in enumerate([key, value]):
            Label(self.frame_inside, text=text, width=width, height=height, relief=SOLID,
                  font=(font, font_size, 'normal')).grid(row=self.row, column=num)
        self.row += 1
