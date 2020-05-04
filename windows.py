from tkinter import *
from tkinter.messagebox import *
from pickle_tools import Database
from structures import *


PROFILES = Database.load()
profile_names = [x.name for x in PROFILES]
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
        low_bar = Frame(self)
        low_bar.pack(side=BOTTOM, fill=X)

        self.refresh_profile_buttons()
        Button(low_bar, text='New Profile', command=self.get_new_profile_name).pack(side=LEFT, padx=10, pady=10)

    def refresh_profile_buttons(self):
        for profile in PROFILES:
            if profile.name not in self.profile_name_buttons:
                profile_button = Button(self.core_bar, text=profile.name.title(),
                                        relief=SOLID, font=('Times New Roman', 40, 'bold'),
                                        command=lambda i=profile: ProfileWindow(i))
                profile_button.pack(fill=X, pady=5)
                self.profile_name_buttons[profile.name] = profile_button

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

    @staticmethod
    def profile_name_check(field, window):
        name = field.get()
        if len(name) > 2:
            if name.title() in profile_names:
                showerror('Profile Exists', f'[{name}] already exists. Please choose another profile name')
                return
            window.destroy()
            AddProfile(name)
        else:
            showerror('Invalid Profile Name', 'Profile Name should have 2 symbols minimum')

    def delete_profile(self, window, profile):
        print(profile)
        if askyesno('Verify', f'Do you really want to delete {profile.name} profile'):
            window.destroy()
            PROFILES.remove(profile)
            self.profile_name_buttons[profile.name].destroy()
            del self.profile_name_buttons[profile.name]
            Database.save(PROFILES)
            showinfo('Success!', f'Profile: {profile.name} has been successfully deleted!')


# -----------------------------------------------------------------------
class AddProfile(Toplevel):
    def __init__(self, profile_name):
        Toplevel.__init__(self, root)
        self.title('New profile')
        self.geometry('400x600')
        self.grab_set()
        self.profile_name = profile_name
    
        # Button creation
        x = Frame(self)
        x.pack(fill=X)
        self.add_parameter = Button(x, text='Add new parameter', command=self.create_add_parameter_window)
        self.add_parameter.pack(side=RIGHT, anchor=NE, padx=10, pady=10)

        self.vars = {}
        self.parameters_frame = Frame(self)
        self.parameters_frame.pack(expand=1, fill=BOTH)

        Button(self, text='Create profile', command=self.parameters_check).pack()
        self.progress = Label(self, text='0%')
        self.progress.pack(anchor=NW)

    def change_progress_number(self, percent_num):
        self.progress.config(text=f'{(str(percent_num) + "%") if isinstance(percent_num, int) else percent_num}')

    def create_add_parameter_window(self):
        self.dialog = Toplevel(self)
        self.dialog.geometry('300x50')
        self.dialog.title('New parameter')
        self.dialog.grab_set()
        var = StringVar()

        x = Frame(self.dialog)
        x.pack(expand=1, fill=X)
        Label(x, text='Parameter Name:').pack(side=LEFT)
        ent = Entry(x, textvariable=var)
        ent.pack(side=LEFT, expand=1)
        ent.focus_set()
        ent.bind('<Return>', lambda event: self.parameter_name_check(var.get()))
        Button(self.dialog, text='Confirm', command=lambda: self.parameter_name_check(var.get())).pack()

    # Check parameter name on emptiness and other symbols
    def parameter_name_check(self, parameter_name):
        self.dialog.destroy()
        if not parameter_name:
            showerror('Empty Parameter Name', 'Parameter name fields is empty')
            return
        if parameter_name in self.vars.keys():
            showerror('Existing Parameter', 'This parameter already exists!')
            return
        self.create_parameter(parameter_name)

    # Check parameters for profile at all
    def parameters_check(self):
        stats = {}
        self.change_progress_number(0)
        if not self.vars:
            showerror('No parameters', f'[{self.profile_name}] has not any parameters. Please create any new one')
            self.change_progress_number('Error')
            return
        for key in self.vars:
            if not self.vars[key].get():
                self.change_progress_number('Error')
                showerror('Empty Parameter', f'[{key}] has empty value. Please fill this field!')
                return
            stats[key.title()] = self.vars[key].get()
            print(f'[DELETE ME][{key} >>> {self.vars[key].get()}] - Good!')
        self.end_profile_creation(stats)

    # Create an Entry field with label
    def create_parameter(self, parameter_name):
        x = Frame(self.parameters_frame)
        var = StringVar()
        x.pack(fill=X, padx=20, pady=2)
        Label(x, text=parameter_name.title(), width=15, font=('Arial', 10, 'bold')).pack(side=LEFT, padx=5)
        Entry(x, textvariable=var, width=40).pack(side=LEFT, fill=X, padx=10)
        self.vars[parameter_name] = var

    # Make an instance of Profile class
    def create_profile(self, stats):
        # Profile: name, inv, abcv, stats
        # Inventory: name, space
        inv = Inventory('root', 10)
        abcv = Inventory('root', 100)
        p = Profile(self.profile_name, inv, abcv)
        p.edit_stats(stats)
        return p

    # Write in a dictionary
    def end_profile_creation(self, stats):
        self.change_progress_number(50)
        PROFILES.append(self.create_profile(stats))
        Database.save(PROFILES)
        self.change_progress_number(100)
        root.refresh_profile_buttons()
        showinfo('Profile created', f'"{self.profile_name}" profile has successfully created!')
        self.destroy()


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

        self.existing_quests = []
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
        Database.save(PROFILES)
        self.post_quests()

    def create_quest_environment(self):
        border = Frame(self.quests_frame, bg='black')
        border.pack(fill=X, pady=5)
        quest_frame = Frame(border, height=10)
        close_quest_button = Button(quest_frame, height=5)
        quest_name_frame = Frame(quest_frame)
        quest_description = Frame(quest_frame)
        award_button = Button(quest_frame)
        quest_frame.pack(fill=BOTH, expand=1, pady=2, padx=2)
        close_quest_button.pack(side=RIGHT, fill=Y)
        quest_name_frame.pack(fill=X)
        award_button.pack(side=RIGHT, fill=Y, pady=4, padx=20)
        quest_description.pack(fill=BOTH, expand=1)
        return close_quest_button, quest_name_frame, quest_description, award_button

    def post_quests(self):
        print('SELF PROFILE QUESTS', self.profile.quests)
        for quest in self.profile.quests:
            if quest not in self.existing_quests:
                cqb, qnf, qd, ab = self.create_quest_environment()
                cqb.config(text='Finish quest', command=lambda i=quest.name: print(i))
                Label(qnf, text=quest.name, font=('Times New Roman', 18, 'bold')).pack(padx=5)
                ab.config(text='Quest Awards', command=lambda i=quest.award: print(i))
                d = quest.desc
                while len(d) > 60:
                    row = d[:60]
                    Label(qd, text=row, font=('Arial', 10, 'normal')).pack()
                    d = d.replace(row, '')
                Label(qd, text=d, font=('Arial', 10, 'normal')).pack()
                self.existing_quests.append(quest)

    def finish_quest(self, quest):
        if askyesno('Verify', 'Give awards?'):
            print(self.profile.name, 'will give', quest.award)

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
    print(PROFILES)
    root.mainloop()
