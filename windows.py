from tkinter import *
from tkinter.messagebox import *
from pickle_tools import Database
from structures import *
from abstract_display_window import DisplayWindow

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
        add_profile_window.create_entry_parameter_field('Space', int)
        add_profile_window.wait_window()
        for field in add_profile_window.result:
            if not add_profile_window.result[field]:
                return
        inv = Inventory('root', int(add_profile_window.result.pop('Space')))
        abcv = Inventory('abstract root')
        p = Profile(name.title(), inv, abcv, **add_profile_window.result)
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


class ItemsList(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.grab_set()
        self.title('Items')
        self.geometry('300x500')
        self.create_list()

    def create_list(self):
        self.list = Listbox(self, relief=SOLID, selectmode=SINGLE)
        self.scroller = Scrollbar(self, command=self.list.yview)
        self.list.config(yscrollcommand=self.scroller.set, font=('Arial', 20, 'normal'))
        self.scroller.pack(side=RIGHT, fill=Y)
        self.list.pack(expand=1, fill=BOTH)
        self.fill_list()
        self.list.bind('<Double-1>', lambda event: self.on_click())

    def delete_item(self, child, item):
        DATABASE['items'].inventory.remove(item)
        Database.save(DATABASE)
        child.destroy()
        self.list.destroy()
        self.scroller.destroy()
        self.create_list()

    def fill_list(self):
        for item in DATABASE['items'].inventory:
            self.list.insert(END, f'[{item}]')

    def on_click(self):
        index = self.list.curselection()[0]
        try:
            item = DATABASE['items'].inventory[index]
        except KeyError:
            showinfo('Info', 'Maybe this item was deleted. I cant open its info')
            self.list.delete(index)
        else:
            ItemInfo(self, item)


class ItemInfo(DisplayWindow):
    def __init__(self, parent, item: Item):
        DisplayWindow.__init__(self, parent, f'Info about: {item.name}', 'auto', item.name, f'Weight: {item.weight}', True, **item.stats)
        self.item = item

        Button(self, text='Delete Item',
               command=lambda: parent.delete_item(self, self.item)).pack(side=RIGHT, pady=10, padx=10, anchor=N)

    def delete_item(self, parent):
        if askyesno('Verify', f'Do you really want to delete [{self.item.name}]?'):
            DATABASE['items'].inventory.remove(self.item)
            Database.save(DATABASE)
            parent.destroy()


class NewItemWindow(AskWindowSample):
    def __init__(self, parent=None):
        super().__init__(parent, 'New Item', '400x700', [])
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
            name = self.result.pop('Item name')
            if name in item_names:
                showerror('Error', f'Item with name {name} already exists!')
                return
            weight = self.result.pop('Item weight')
            DATABASE['items'].put(Item(name, weight, **self.result))


# -----------------------------------------------------------------------
class Provider:
    def __init__(self, instance):
        self.profile = instance


class ProfileWindow(DisplayWindow):
    def __init__(self, parent, profile):
        DisplayWindow.__init__(self, parent, f' Profile: {profile.name}', 'auto',
                               profile.name, f'Space: {profile.inventory.space}', True, **profile.stats)
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
        DisplayWindow.__init__(self, parent, f'Quests: {profile.name}', '800x500', profile.name, '', False)
        Provider.__init__(self, profile)

        self.aside = Frame(self)
        self.aside.pack(side=RIGHT, fill=Y)
        self.create_aside_panel()
        self.existing_quests = {}
        self.post_quests()

    def create_aside_panel(self):
        Button(self.aside, text='Add Quest', height=3, width=15, command=self.add_quest).pack(padx=10, pady=10)

    def add_quest(self):
        add_quest_window = AskWindowSample(self, 'New Quest', 'auto', [], 4)
        add_quest_window.create_entry_parameter_field('Name', str)
        add_quest_window.create_text_parameter_field('Description')
        add_quest_window.create_combobox_parameter_field('Given by', ['NPC 1', 'NPC 2', 'NPC 3'])
        add_quest_window.create_entry_parameter_field('Award', int)
        add_quest_window.wait_window()
        result = add_quest_window.result
        for key in result:
            if not result[key]:
                return 0
        q = Quest(result['Description'], result['Given by'], result['Award'], result['Name'])
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
        show_awards = Button(buttons_inside_, text='Show Awards', width=10, command=1)
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
            print(f'{self.profile.name} got nothing')
        for award in awards:
            print(f'{self.profile.name} is getting {award.name}')

    def delete_quest_frame(self, quest):
        print(quest, '\n', self.existing_quests)
        if askyesno('Verify', 'Do you really want to delete this quest?'):
            self.profile.quests.remove(quest)
            Database.save(DATABASE)
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
