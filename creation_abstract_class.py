from tkinter import *
from tkinter.messagebox import *


class AskWindowSample(Toplevel):
    def __init__(self, parent, title, geometry, forbidden: list, maxparameters=999):
        Toplevel.__init__(self, parent)
        self.maxparams = maxparameters
        self.grab_set()
        self.forbidden_parameters = forbidden
        self.title(title)
        self.geometry(geometry)
        self.box = {}
        self.vars = {}

        self.create_add_parameter_button()
        self.create_confirm_profile_button()

        self.container = Frame(self)
        self.container.pack(fill=BOTH, expand=1, padx=15)

    def create_add_parameter_button(self):
        zone = Frame(self)
        zone.pack(fill=X)
        b = Button(zone, text="Add Parameter", command=self.create_ask_parameter_window)
        b.pack(anchor=NE)

    def create_confirm_profile_button(self):
        zone = Frame(self)
        zone.pack(side=BOTTOM, fill=X)
        b = Button(zone, text="Confirm", command=self.end_process)
        b.pack(expand=1)

    def create_ask_parameter_window(self):
        self.win = Toplevel(self)
        self.win.title('New Parameter')
        self.win.grab_set()
        var = StringVar()
        f = Frame(self.win)
        f.pack(padx=40, pady=20)
        row = Frame(f)
        row.pack()
        Label(row, text="Parameter Name", font=("Times New Roman", 10, 'bold')).pack(side=LEFT)
        ent = Entry(row, textvariable=var)
        ent.bind('<Return>', lambda event: self.check_parameter_name_value(var))
        ent.pack(side=LEFT, padx=5)
        Button(f, text="Confirm", command=lambda: self.check_parameter_name_value(var)).pack(expand=1)

    def check_parameter_name_value(self, field):
        data = field.get()
        if data:
            self.win.destroy()
            self.create_parameter_field(data, str)
        else:
            showerror('Error', 'Invalid Parameter Name')

    def create_parameter_field(self, parameter_name, valuetype: type):
        var = StringVar()
        row = Frame(self.container)
        row.pack(pady=5)
        Label(row, text=parameter_name.title(), font=("Times New Roman", 20, 'bold'), width=10).pack(side=LEFT)
        Entry(row, textvariable=var, width=20).pack(side=LEFT, padx=5)
        self.vars[parameter_name] = {'var': var, 'type': valuetype}
        self.box[parameter_name] = None

    def check_fields(self):
        for field in self.vars:
            if self.vars[field]['var'].get():
                right_value = self.check_type(self.vars[field]['var'].get(), self.vars[field]['type'])
                if not right_value:
                    showerror('Error', f'{field} has invalid value!')
                    return
            else:
                showerror('Error', f'{field} has got empty value!')
                return
        else:
            return 1

    @staticmethod
    def check_type(target, valuetype):
        print(target, valuetype, '***')
        try:
            x = valuetype(target)
        except ValueError:
            pass
        else:
            return x

    def end_process(self):
        if self.check_fields():
            showinfo('Success', 'Success')
            self.box = {x: self.vars[x]['var'].get() for x in self.vars}
            self.destroy()
