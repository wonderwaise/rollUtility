from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox
from abstract_window import AbstractWindow


class AskWindowSample(AbstractWindow):
    def __init__(self, parent, title, geo, forbidden: list, maxparameters=999):
        AbstractWindow.__init__(self, parent, title, geo)
        self.maxparams = maxparameters
        self.forbidden_parameters = forbidden
        self.result = {}
        self.vars = {}
        self.rows = 0

        self.create_add_parameter_button()
        self.parameter_frame = Frame(self)
        self.parameter_frame.pack(fill=BOTH, expand=1, padx=30, pady=10)
        self.create_confirm_profile_button()

        self.container = Frame(self)
        self.container.pack(fill=BOTH, expand=1, padx=15)

    def create_add_parameter_button(self):
        zone = Frame(self)
        zone.pack(fill=X)
        Button(zone, width=20, height=2, text="Add Parameter",
               command=self.create_ask_parameter_window).pack(anchor=NE, padx=10, pady=10)

    def create_confirm_profile_button(self):
        zone = Frame(self)
        zone.pack(side=BOTTOM, fill=X)
        Button(zone, text="Confirm", width=25, height=2, command=self.end_process).pack(expand=1, pady=10)

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
        ent.focus_get()
        ent.bind('<Return>', lambda event: self.check_parameter_name_value(var))
        ent.pack(side=LEFT, padx=5)
        Button(f, text="Confirm", command=lambda: self.check_parameter_name_value(var)).pack(expand=1)

    def check_parameter_name_value(self, field):
        data = field.get().title()
        if data:
            if data in self.forbidden_parameters:
                showerror('Error', 'Forbidden Parameter Name!')
                return
            elif data in self.vars:
                showerror('Error', 'Existing parameter name')
                return
            self.win.destroy()
            self.create_text_parameter_field(data, str)
        else:
            showerror('Error', 'Invalid Parameter Name')

    def create_text_parameter_field(self, parameter_name, valuetype: type):
        var = StringVar()
        Label(self.parameter_frame, text=parameter_name, font=("Times New Roman", 20, 'bold'), width=15).grid(row=self.rows, column=0)
        Entry(self.parameter_frame, textvariable=var, width=20).grid(row=self.rows, column=1)
        self.rows += 1
        self.vars[parameter_name] = {'var': var, 'type': valuetype}
        self.result[parameter_name] = None

    def create_combobox_parameter_field(self, parameter_name, iterable):
        var = StringVar()
        Label(self.parameter_frame, text=parameter_name, font=('Times New Roman', 20, 'bold'), width=15).grid(row=self.rows, column=0)
        Combobox(self.parameter_frame, textvariable=var, width=15, values=iterable).grid(row=self.rows, column=1)
        self.rows += 1
        self.vars[parameter_name] = {'var': var, 'type': str}
        self.result[parameter_name] = None

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
            self.result = {x: self.vars[x]['var'].get() for x in self.vars}
            self.destroy()
