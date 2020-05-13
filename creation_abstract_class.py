from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox
from abstract_window import AbstractWindow
from item_seletion_window import ItemSelectionWindow
import structures


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
        if self.maxparams < len(self.vars) + 1:
            showerror('Error', 'Parameter Limit!')
            return
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
        confirm = Button(f, text="Confirm", command=lambda: self.check_parameter_name_value(var))
        confirm.pack(expand=1)
        confirm.bind('<Return>', lambda event: self.check_parameter_name_value(var))

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
            self.create_entry_parameter_field(data, str)
        else:
            showerror('Error', 'Invalid Parameter Name')

    def create_parameter_field(self, parameter_name, var, valuetype: type):
        Label(self.parameter_frame, text=parameter_name, relief=SOLID,
              font=("Times New Roman", 20, 'bold'), width=12).grid(row=self.rows, column=0, sticky=N+S)
        self.rows += 1
        self.vars[parameter_name] = {'var': var, 'type': valuetype}
        self.result[parameter_name] = None

    def create_entry_parameter_field(self, parameter_name, valuetype: type):
        var = StringVar()
        Entry(self.parameter_frame, textvariable=var, width=40).grid(row=self.rows, column=1, sticky=N+S)
        self.create_parameter_field(parameter_name, var, valuetype)

    def create_combobox_parameter_field(self, parameter_name, iterable):
        var = StringVar()
        Combobox(self.parameter_frame, textvariable=var, width=35,
                 values=iterable).grid(row=self.rows, column=1, sticky=N+S)
        self.create_parameter_field(parameter_name, var, str)

    def create_text_parameter_field(self, parameter_name):
        text = Text(self.parameter_frame, width=30, height=5)
        text.grid(row=self.rows, column=1)
        self.create_parameter_field(parameter_name, text, str)

    def create_item_parameter_field(self, parameter_name, inventory):
        Button(self.parameter_frame, width=20, height=2, text='Choose Items',
               font=('Arial', 15, 'normal'),
               command=lambda: self._create_item_window(parameter_name,
                                                        inventory)).grid(row=self.rows, column=1, sticky=N+S)
        self.create_parameter_field(parameter_name, structures.Inventory('1'), object)

    def _create_item_window(self, pn, inventory):
        item_selection = ItemSelectionWindow(self, 'Choose Items', inventory)
        item_selection.wait_window()
        bag = structures.Inventory('1')
        if item_selection.selected_items:
            for item_name in item_selection.selected_items:
                bag.put(item_selection.all_items[item_name]['instance'])
            self.vars[pn] = {'var': bag, 'type': object}
            self.result[pn] = None

    def check_fields(self):
        for field in self.vars:
            if isinstance(self.vars[field]['var'], Text):
                if self.vars[field]['var'].get('1.0', END+'-1c'):
                    continue
                showerror('Error', f'{field} has empty value!')
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
        try:
            if valuetype is not object:
                target = valuetype(target)
        except ValueError:
            pass
        else:
            return target

    def end_process(self):
        if self.check_fields():
            for x in self.vars:
                if isinstance(self.vars[x]['var'], Text):
                    self.result[x] = self.vars[x]['var'].get('1.0', END+'-1c')
                elif isinstance(self.vars[x]['var'], structures.Inventory):
                    self.result[x] = self.vars[x]['var'].get()
                else:
                    self.result[x] = self.vars[x]['type'](self.vars[x]['var'].get())
            self.destroy()
