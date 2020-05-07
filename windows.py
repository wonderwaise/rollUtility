from tkinter import *
from tkinter.messagebox import *
from pickle_tools import Database
from structures import *

DATABASE = Database.load()
print(DATABASE['items'].inventory)
profile_names = [x.name for x in DATABASE['profiles']]
# Profile window class >>> remake field spawning => aside spawn first to evade disappear
# Base parameters such as weight and so on
# Abstract class for creation windows and Concrete classes for create profile, items, quests, etc.
# NPC creation, Item creation, Item list for award on quests.


# --------------------------------------------------------
class MainWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('BackPack by wonder [v.0.0.1]')
        self.geometry('800x600')
        self.maxsize(1000, 600)
        # Existing profile buttons in main window
        self.profile_name_buttons = {}

        self.core_bar = Frame(self)
        self.core_bar.pack(fill=BOTH, padx=30, pady=10)

        self.refresh_profile_buttons()
        self.create_bottom_panel()

    def create_bottom_panel(self):
        low_bar = Frame(self)
        low_bar.pack(side=BOTTOM, fill=X)
        self.create_add_profile_button(low_bar)
        self.create_add_item_button(low_bar)
        self.create_show_items_button(low_bar)

    def create_add_item_button(self, frame):
        Button(frame, text='Add Item', command=self.create_item).pack(side=LEFT, padx=10, pady=10)

    def create_add_profile_button(self, frame):
        Button(frame, text='Add Profile', command=self.get_new_profile_name).pack(side=LEFT, padx=10, pady=10)

    def create_show_items_button(self, frame):
        Button(frame, text='All Items', command=lambda: ItemsList(self)).pack(side=RIGHT, padx=10, pady=10)

    def refresh_profile_buttons(self):
        for profile in DATABASE['profiles']:
            if profile.name not in self.profile_name_buttons:
                profile_button = Button(self.core_bar, text=profile.name.title(),
                                        relief=SOLID, font=('Times New Roman', 40, 'bold'),
                                        command=lambda i=profile: ProfileWindow(i))
                profile_button.pack(fill=X, pady=5)
                self.profile_name_buttons[profile.name.title()] = profile_button

    def get_new_profile_name(self):
        win = Toplevel(self)
        var = StringVar()
        win.geometry('300x100')
        win.grab_set()
        f = Frame(win)
        f.pack(expand=1)
        Label(f, text='Profile Name:').pack(side=LEFT)
        ent = Entry(f, textvariable=var)
        ent.pack(side=LEFT)
        ent.focus_set()
        ent.bind('<Return>', lambda event: self.profile_name_check(var, win))
        Button(win, text='Create', command=lambda: self.profile_name_check(var, win)).pack(expand=1)

    def profile_name_check(self, field, window):
        name = field.get()
        if len(name) > 2:
            print(name.title(), self.profile_name_buttons)
            if name.title() in self.profile_name_buttons:
                showerror('Profile Exists', f'[{name}] already exists. Please choose another profile name')
                return
            window.destroy()
            self.create_profile(name)
        else:
            showerror('Invalid Profile Name', 'Profile Name should have 2 symbols minimum')

    def create_profile(self, name):
        add_profile_window = AskWindowSample(self, 'New Profile', '400x700', ['Name'])
        add_profile_window.create_parameter_field('Space', int)
        add_profile_window.wait_window()
        for field in add_profile_window.box:
            if not add_profile_window.box[field]:
                return
        inv = Inventory('root', int(add_profile_window.box.pop('Space')))
        abcv = Inventory('abstract root')
        p = Profile(name.title(), inv, abcv, **add_profile_window.box)
        DATABASE['profiles'].append(p)
        Database.save(DATABASE)
        self.refresh_profile_buttons()

    def create_item(self):
        add_item_window = NewItemWindow(self)
        add_item_window.create_item_object()
        Database.save(DATABASE)

    def delete_profile(self, window, profile):
        if askyesno('Verify', f'Do you really want to delete {profile.name} profile'):
            window.destroy()
            DATABASE['profiles'].remove(profile)
            self.profile_name_buttons.pop(profile.name).destroy()
            Database.save(DATABASE)
            showinfo('Success!', f'Profile: {profile.name} has been successfully deleted!')


class ItemsList(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.grab_set()
        self.title('Items')
        self.geometry('300x500')
        self.list = Listbox(self, relief=SOLID, selectmode=SINGLE)
        self.scroller = Scrollbar(self, command=self.list.yview)
        self.list.config(yscrollcommand=self.scroller.set)
        self.scroller.pack(side=RIGHT, fill=Y)
        self.list.pack(expand=1, fill=BOTH)
        self.fill_list()
        self.list.bind('<Double-1>', lambda event: self.on_click())

    def fill_list(self):
        for item in DATABASE['items'].inventory:
            self.list.insert(END, f'[{item}]')

    def on_click(self):
        index = self.list.curselection()[0]
        item = DATABASE['items'].inventory[index]
        ItemInfo(self, item)


class ItemInfo(Toplevel):
    def __init__(self, parent, item: Item):
        Toplevel.__init__(self, parent)
        self.geometry('350x500')
        self.title(f'Info about: {item.name}')
        self.item = item
        top_frame = Frame(self)
        top_frame.pack(fill=X)
        for attr in [item.name, f'Weight: {item.weight}']:
            Label(top_frame, text=attr, font=('Times New Roman', 20, 'bold')).pack(side=LEFT, padx=15, expand=1)

        self.canvas = Canvas(self, width=306)
        self.parameters_frame = Frame(self.canvas)
        self.scroller = Scrollbar(self, command=self.canvas.yview)
        self.canvas_setting()
        self.scroller.pack(side=RIGHT, fill=Y)
        self.canvas.pack(fill=Y, expand=1)
        self.iterate_parameters()

    def canvas_setting(self):
        self.parameters_frame.bind('<Configure>',
                                   lambda event: self.canvas.config(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.parameters_frame, anchor='nw')
        self.canvas.config(yscrollcommand=self.scroller.set)

    def iterate_parameters(self):
        params_frame = Frame(self.parameters_frame, pady=20)
        params_frame.pack(fill=BOTH, expand=1)
        for row, stat in enumerate(self.item.stats):
            self.accommodate_parameter(row, stat, self.item.stats[stat], params_frame)

    @staticmethod
    def accommodate_parameter(row, name, value, master):
        Label(master, text=name, width=15, relief=SOLID,
              font=('Times New Roman', 15, 'bold')).grid(row=row, sticky=W)
        Label(master, text=value, width=15, relief=SOLID,
              font=('Times New Roman', 15, 'normal')).grid(row=row, column=1)


class NewItemWindow(AskWindowSample):
    def __init__(self, parent=None):
        super().__init__(parent, 'New Item', '400x700', [])
        self.create_parameter_field('Item name', str)
        self.create_parameter_field('Item weight', int)
        self.wait_window()
        self.check_box()

    def check_box(self):
        for key in self.box:
            if not self.box[key]:
                return 0
        return 1

    def create_item_object(self):
        name = self.box.pop('Item name')
        weight = self.box.pop('Item weight')
        DATABASE['items'].put(Item(name, weight, **self.box))


# -----------------------------------------------------------------------
class Provider:
    def __init__(self, instance):
        self.profile = instance


class ProfileWindow(Toplevel):
    def __init__(self, profile):
        Toplevel.__init__(self, root)
        self.profile = profile
        self.title(f'Profile: {self.profile.name}')
        self.geometry('400x700')
        self.grab_set()

        self.core_frame = Frame(self)
        self.core_frame.pack(side=LEFT, fill=Y, padx=5, pady=10, expand=1)
        self.aside_frame = Frame(self)
        self.aside_frame.pack(side=LEFT, fill=Y, padx=8, pady=10)

        self.left_core_frame = Frame(self.core_frame)
        self.left_core_frame.pack(side=LEFT, fill=Y, padx=2, expand=1)
        self.right_core_frame = Frame(self.core_frame)
        self.right_core_frame.pack(side=LEFT, fill=Y, padx=2, expand=1)

        self.construct()
        self.create_aside_menu()

    def construct(self):
        for parameter in self.profile.stats:
            Label(self.left_core_frame, text=f'{parameter}:', font=('Arial', 20, 'bold')).pack(fill=X, padx=35)
            Label(self.right_core_frame, text=self.profile.stats[parameter],
                  font=('Arial', 20, 'normal')).pack(fill=X, padx=35)

    def create_aside_menu(self):
        samples = {
            'Quests': QuestsWindow,
            'Inventory': InventoryWindow,
            'Achievements': AchievementsWindow
        }
        for sample in samples:
            Button(self.aside_frame, width=10, text=sample,
                   command=lambda i=sample: samples[i](self, self.profile)).pack(pady=5)

        Button(self.aside_frame, text='Delete profile', command=lambda: root.delete_profile(self, self.profile))\
            .pack(side=BOTTOM, anchor=SE)


class QuestsWindow(Toplevel, Provider):
    def __init__(self, parent, profile):
        Toplevel.__init__(self, parent)
        Provider.__init__(self, profile)
        self.title(f'{self.profile.name}\'s quests')
        self.geometry('700x400')
        self.focus_set()
        self.grab_set()

        self.existing_quests = {}
        self.quests_frame = Frame(self)
        self.bottom_frame = Frame(self)
        self.quests_frame.pack(expand=1, fill=BOTH, padx=10)
        self.bottom_frame.pack(fill=X)
        Button(self.bottom_frame, text='Add Quest',
               command=self.add_quest).pack(
            side=LEFT, padx=5, pady=5)
        self.post_quests()

    def add_quest(self):
        self.profile.add_quest(self)
        Database.save(DATABASE)
        self.post_quests()

    def create_quest_environment(self):
        border = Frame(self.quests_frame, bg='black')
        border.pack(fill=X, pady=5)
        quest_frame = Frame(border, height=10)
        right_buttons_frame = Frame(quest_frame, height=5)
        delete_quest_button = Button(right_buttons_frame)
        give_award_button = Button(right_buttons_frame)
        quest_name_frame = Frame(quest_frame)
        quest_description = Frame(quest_frame)
        award_button = Button(quest_frame)
        quest_frame.pack(fill=BOTH, expand=1, pady=2, padx=2)
        right_buttons_frame.pack(side=RIGHT, fill=Y)
        delete_quest_button.pack(fill=BOTH, expand=1)
        give_award_button.pack(fill=BOTH, expand=1)
        quest_name_frame.pack(fill=X)
        award_button.pack(side=RIGHT, fill=Y, pady=4, padx=20)
        quest_description.pack(fill=BOTH, expand=1)
        return border, delete_quest_button, give_award_button, quest_name_frame, quest_description, award_button

    def post_quests(self):
        print('SELF PROFILE QUESTS', self.profile.quests)
        for quest in self.profile.quests:
            if quest not in self.existing_quests:
                b, dqb, gab, qnf, qd, ab = self.create_quest_environment()
                dqb.config(text='Delete Quest', command=lambda i=quest: self.delete_quest_frame(i))
                gab.config(text='Give Awards', command=lambda i=quest: self.give_award(i.award))
                Label(qnf, text=quest.name, font=('Times New Roman', 18, 'bold')).pack(padx=5)
                ab.config(text='Quest Awards', command=lambda i=quest.award: print(i))
                d = quest.desc
                while len(d) > 60:
                    row = d[:60]
                    Label(qd, text=row, font=('Arial', 10, 'normal')).pack()
                    d = d.replace(row, '')
                Label(qd, text=d, font=('Arial', 10, 'normal')).pack()
                self.existing_quests[quest] = b

    def give_award(self, awards: list):
        if not awards:
            print(f'{self.profile.name} got nothing')
        for award in awards:
            print(f'{self.profile.name} is getting {award.name}')

    def delete_quest_frame(self, quest):
        if askyesno('Verify', 'Do you really want to delete this quest?'):
            self.existing_quests.pop(quest).destroy()

    def show_quest_awards(self, quest):
        print('Quest Awards:')
        for award in quest.award:
            print(award)


class InventoryWindow(Toplevel, Provider):
    def __init__(self, parent, profile):
        Toplevel.__init__(self, parent)
        Provider.__init__(self, profile)
        self.title(f'{self.profile.name}\'s inventory')
        self.geometry('700x400')
        self.focus_set()
        self.grab_set()


class AchievementsWindow(Toplevel, Provider):
    def __init__(self, parent, profile):
        Toplevel.__init__(self, parent)
        Provider.__init__(self, profile)
        self.title(f'{self.profile.name}\'s achievements')
        self.geometry('700x400')
        self.focus_set()
        self.grab_set()




root = MainWindow()
if __name__ == '__main__':
    root.mainloop()
