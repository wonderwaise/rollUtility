from tkinter import *
from tkinter.messagebox import *
from pickle_tools import Database
from structures import *
from abstract_display_window import DisplayWindow
from abstract_itemlist_window import ItemsList

DATABASE = Database.load()
profile_names = [x.name for x in DATABASE['profiles']]
item_names = [x.name for x in DATABASE['items'].inventory]
# Profile window class >>> remake field spawning => aside spawn first to evade disappear
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
        Button(low_bar, text='Add Item', command=self.create_item).pack(side=LEFT, padx=10, pady=10)
        Button(low_bar, text='Add Profile', command=self.get_new_profile_name).pack(side=LEFT, padx=10, pady=10)
        Button(low_bar, text='All Items',
               command=lambda: ItemsList(self, 'All Items', (500, 600),
                                         DATABASE['items'].inventory, True)).pack(side=RIGHT, padx=10, pady=10)

        Button(low_bar, text='All NPCs',
               command=lambda: NotPlayerCharactersWindow(self, 'NPCs', (600, 500), 'Not Player Characters',
                                                         'All NPCs')).pack(side=RIGHT, padx=10, pady=10)

    def refresh_profile_buttons(self):
        for profile in DATABASE['profiles']:
            if profile.name not in self.profile_name_buttons:
                profile_button = Button(self.core_bar, text=profile.name.title(),
                                        relief=SOLID, font=('Times New Roman', 40, 'bold'),
                                        command=lambda i=profile: ProfileWindow(self, i))
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
            if name.title() in self.profile_name_buttons:
                showerror('Profile Exists', f'[{name}] already exists. Please choose another profile name')
                return
            window.destroy()
            self.create_profile(name)
        else:
            showerror('Invalid Profile Name', 'Profile Name should have 2 symbols minimum')

    def create_profile(self, name):
        add_profile_window = AskWindowSample(self, 'New Profile', (400, 700), ['Name'], 90)
        add_profile_window.create_entry_parameter_field('Space', int)
        add_profile_window.wait_window()
        for field in add_profile_window.result:
            if not add_profile_window.result[field]:
                return
        inv = Inventory('root', int(add_profile_window.result.pop('Space')))
        abcv = Inventory('abstract root')
        p = Profile(name.title(), inv, abcv, **add_profile_window.result)
        profile_names.append(name)
        DATABASE['profiles'].append(p)
        Database.save(DATABASE)
        self.refresh_profile_buttons()

    def create_item(self):
        NewItemWindow(self)
        Database.save(DATABASE)

    def delete_profile(self, window, profile):
        if askyesno('Verify', f'Do you really want to delete {profile.name} profile'):
            window.destroy()
            DATABASE['profiles'].remove(profile)
            self.profile_name_buttons.pop(profile.name).destroy()
            Database.save(DATABASE)
            showinfo('Success!', f'Profile: {profile.name} has been successfully deleted!')


class NewItemWindow(AskWindowSample):
    def __init__(self, parent=None):
        super().__init__(parent, 'New Item', (400, 700), [])
        self.create_entry_parameter_field('Item name', str)
        self.create_entry_parameter_field('Item weight', int)
        self.wait_window()
        self.create_item_object()

    def check_box(self):
        for key in self.result:
            if not self.result[key]:
                return 0
        return 1

    def create_item_object(self):
        if self.check_box():
            name = self.result.pop('Item name').title()
            if name in item_names:
                showerror('Error', f'Item with name {name} already exists!')
                return
            weight = self.result.pop('Item weight')
            item_names.append(name)
            DATABASE['items'].put(Item(name, weight, **self.result))


# -----------------------------------------------------------------------
class Provider:
    def __init__(self, instance):
        self.profile = instance


class ProfileWindow(DisplayWindow):
    def __init__(self, parent, profile):
        DisplayWindow.__init__(self, parent, f'Profile: {profile.name}', (500, 700),
                               profile.name, profile.inventory.space, True, **profile.stats)
        self.aside_frame = Frame(self)
        self.aside_frame.pack(side=RIGHT, fill=Y, padx=8, pady=10, anchor=NE)
        self.profile = profile

        self.create_aside_menu()

    def create_aside_menu(self):
        samples = {
            'Quests': QuestsWindow,
            'Inventory': InventoryWindow,
            'Achievements': AchievementsWindow
        }
        for sample in samples:
            Button(self.aside_frame, width=10, text=sample,
                   command=lambda i=sample: samples[i](self, self.profile)).pack(pady=5, side=TOP)

        Button(self.aside_frame, text='Delete profile', command=lambda: root.delete_profile(self, self.profile))\
            .pack(side=BOTTOM, pady=5, anchor=SE)


class QuestsWindow(DisplayWindow, Provider):
    def __init__(self, parent, profile):
        DisplayWindow.__init__(self, parent, f'Quests: {profile.name}', (800, 500), profile.name, '', False)
        Provider.__init__(self, profile)

        self.aside = Frame(self)
        self.aside.pack(side=RIGHT, fill=Y)
        self.create_aside_panel()
        self.existing_quests = {}
        self.post_quests()

    def create_aside_panel(self):
        Button(self.aside, text='Add Quest', height=3, width=15, command=self.add_quest).pack(padx=10, pady=10)

    def add_quest(self):
        add_quest_window = AskWindowSample(self, 'New Quest', (500, 700), [], 4)
        add_quest_window.create_entry_parameter_field('Name', str)
        add_quest_window.create_text_parameter_field('Description')
        add_quest_window.create_combobox_parameter_field('Given by', [x.name for x in DATABASE['npcs']])
        add_quest_window.create_item_parameter_field('Award', DATABASE['items'])
        add_quest_window.wait_window()
        result = add_quest_window.result
        for key in result:
            if not result[key]:
                return 0
        q = Quest(result['Description'], result['Given by'], result['Award'], result['Name'].title())
        self.profile.quests.append(q)
        Database.save(DATABASE)
        self.post_quests()

    def create_quest_environment(self, q):
        # self.frame_inside = master frame
        self.canvas.config(width=670, height=400)
        container = Frame(self.frame_inside, bd=2, bg='black')
        container.pack(expand=1, pady=20, padx=20, anchor=N)

        # side=RIGHT
        right_buttons_ = Frame(container)
        right_buttons_.pack(side=RIGHT, fill=Y)
        delete_b = Button(right_buttons_, text='Delete Quest', width=10, command=lambda: self.delete_quest_frame(q))
        delete_b.pack(fill=Y, expand=1)
        give_w = Button(right_buttons_, text='Give Awards', width=10)
        give_w.pack(fill=Y, expand=1)

        quest_details_ = Frame(container)
        quest_details_.pack(fill=BOTH, expand=1)

        # fill=X, side=TOP
        quest_name_ = Frame(quest_details_, bd=2, relief=SOLID)
        quest_name_.pack(fill=X, expand=1, anchor=N)
        quest_name = Label(quest_name_, text=q.name, font=('Times New Roman', 20, 'bold'))
        quest_name.pack(expand=1, pady=5)

        # fill=Y, side=RIGHT .pack(fill=Y, padx=5)
        buttons_inside_ = Frame(quest_details_)
        buttons_inside_.pack(fill=Y, side=RIGHT)
        g_by = Button(buttons_inside_, text='Given by', width=10, command=1)
        g_by.pack(fill=Y, expand=1)
        show_awards = Button(buttons_inside_, text='Show Awards', width=10, command=lambda i=q: self.show_quest_awards(i))
        show_awards.pack(fill=Y, expand=1)

        description_ = Frame(quest_details_, relief=SOLID)
        description = Canvas(quest_details_)
        scroll_desc = Scrollbar(description_, command=description.yview)
        description.config(yscrollcommand=scroll_desc.set, width=450, height=100)
        scroll_desc.pack(side=RIGHT, fill=Y)
        description.pack(fill=BOTH, expand=1)
        return quest_name, give_w, description, container

    def post_quests(self):
        for quest in self.profile.quests:
            if quest not in self.existing_quests:
                quest_name, g, desc, c = self.create_quest_environment(quest)
                self.existing_quests[quest] = c
                g.config(command=1)
                self.fill_quest_description(quest, desc)

    @staticmethod
    def fill_quest_description(quest, canvas):
        string = quest.desc
        n = 0
        while string:
            n += 1
            cut = string[:80]
            string = string[80:]
            canvas.create_text(10, 0 + (15 * n), text=cut, fill='black', anchor=NW)

    def give_award(self, awards: list):
        if not awards:
            pass
        for award in awards:
            pass

    def delete_quest_frame(self, quest):
        if askyesno('Verify', 'Do you really want to delete this quest?'):
            self.profile.quests.remove(quest)
            Database.save(DATABASE)
            self.existing_quests.pop(quest).destroy()

    @staticmethod
    def show_quest_awards(quest):
        for award in quest.award:
            print(award.name)


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


class NotPlayerCharactersWindow(DisplayWindow):
    def __init__(self, parent, title, msize, name, core):
        DisplayWindow.__init__(self, parent, title, msize, name, core, False)
        self.aside_panel = Frame(self)
        self.buttons = {}
        self.aside_panel.pack(side=RIGHT, fill=Y)
        self.fill_npc_list()
        Button(self.aside_panel, text='Add NPC', command=self.create_new_npc).pack(padx=10, pady=10)

    def fill_npc_list(self):
        for character in DATABASE['npcs']:
            if character.name not in self.buttons:
                npc_button = Button(self.frame_inside, text=character.name, width=15,
                                    font=('Times New Roman', 30, 'bold'),
                                    command=lambda i=character: NPCWindow(self, i, (500, 700)), relief=SOLID)
                npc_button.pack(pady=10, padx=10, expand=1, fill=X)
                self.buttons[character.name] = npc_button

    def create_new_npc(self):
        add_npc_window = AskWindowSample(self, 'New NPC', (500, 500), [], 4)
        add_npc_window.create_entry_parameter_field('Name', str)
        add_npc_window.create_entry_parameter_field('Race', str)
        add_npc_window.create_entry_parameter_field('Home', str)
        add_npc_window.create_entry_parameter_field('Occupation', str)
        add_npc_window.wait_window()
        result = add_npc_window.result
        if self.check_box(result):
            DATABASE['npcs'].append(NotPlayerCharacter(result['Name'], result['Race'],
                                                       result['Home'], result['Occupation']))
            Database.save(DATABASE)
        self.fill_npc_list()

    def delete(self, character):
        self.buttons.pop(character.name).destroy()
        DATABASE['npcs'].remove(character)
        Database.save(DATABASE)


    @staticmethod
    def check_box(box) -> int:
        for el in box:
            if not box[el]:
                return 0
        else:
            return 1


class NPCWindow(DisplayWindow):
    def __init__(self, parent, npc_object, msize):
        DisplayWindow.__init__(self, parent, f'NPC: {npc_object.name}', msize, npc_object.name,
                               'NPC Profile', True, **npc_object.get_stats())

        self.aside_panel = Frame(self)
        self.aside_panel.pack(fill=Y, side=RIGHT)
        Button(self.aside_panel, text='Delete NPC', command=lambda: self.delete_npc(parent,
                                                                                    npc_object)).pack(padx=10, pady=10)

    def delete_npc(self, parent, npc):
        parent.delete(npc)
        self.destroy()
        showinfo('Info', f'{npc.name} was successfully deleted!')





root = MainWindow()
if __name__ == '__main__':
    root.mainloop()
