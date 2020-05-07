from tkinter import *


class AbstractEditWindow(Toplevel):
    def __init__(self, parent, title, geo, forbidden: list, maxparameters=999):
