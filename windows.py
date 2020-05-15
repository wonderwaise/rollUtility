from tkinter import *
from tkinter.messagebox import *
from pickle_tools import Database
from structures import *
from creation_abstract_class import AskWindowSample
from abstract_display_window import DisplayWindow
from abstract_itemlist_window import ItemsList
from abstract_window import AbstractWindow
from item_seletion_window import ItemSelectionWindow

DATABASE = Database.load()
profile_names = [x.name for x in DATABASE['profiles']]
npc_by_names = {x.name: x for x in DATABASE['npcs']}
# Profile window class >>> remake field spawning => aside spawn first to evade disappear
# NPC creation, Item creation, Item list for award on quests.
# механизм если NPC удален а квест который он выдал остался.


# --------------------------------------------------------
class MainWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('BackPack by wonder [v.0.0.1]')
        self.geometry('800x600')
        self.maxsize(1000, 600)
        # Existing profile buttons in main window
        self.profile_name_buttons = {}

        canvas = Canvas(self, width=650)
        sbar = Scrollbar(self, command=canvas.yview)
        self.core_bar = Frame(self)
        self.core_bar.bind('<Configure>', lambda event: canvas.config(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=self.core_bar)
        canvas.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        canvas.pack(padx=20, expand=1, anchor=N)

        self.refresh_profile_buttons()
        self.create_bottom_panel()

    def create_bottom_panel(self):
        low_bar = Frame(self)
        low_bar.pack(side=BOTTOM, fill=X)
        Button(low_bar, text='Создать новый профиль', width=25,
               command=self.get_new_profile_name).pack(side=LEFT, padx=10, pady=10)
        Button(low_bar, text='Все вещи',
               command=lambda: self.create_all_items_window()).pack(side=RIGHT, padx=10, pady=10)

        Button(low_bar, text='Все NPC',
               command=lambda: NotPlayerCharactersWindow(self, 'NPC Персонажи', (600, 500), 'НИПы',
                                                         'Все NPC')).pack(side=RIGHT, padx=10, pady=10)

    def refresh_profile_buttons(self):
        for profile in DATABASE['profiles']:
            if profile.name not in self.profile_name_buttons:
                profile_button = Button(self.core_bar, width=20, text=profile.name.title(),
                                        relief=SOLID, font=('Times New Roman', 40, 'bold'),
                                        command=lambda i=profile: ProfileWindow(self, i))
                profile_button.pack(fill=X, pady=5, expand=1, anchor=N)
                self.profile_name_buttons[profile.name.title()] = profile_button

    def create_all_items_window(self):
        w = ItemsList(self, 'Все вещи', (800, 600), DATABASE['items'].inventory, True, DATABASE['items'])
        w.wait_window()
        Database.save(DATABASE)

    def get_new_profile_name(self):
        win = Toplevel(self)
        var = StringVar()
        win.geometry('300x100')
        win.grab_set()
        f = Frame(win)
        f.pack(expand=1)
        Label(f, text='Имя профиля:').pack(side=LEFT)
        ent = Entry(f, textvariable=var)
        ent.pack(side=LEFT)
        ent.focus_set()
        ent.bind('<Return>', lambda event: self.profile_name_check(var, win))
        Button(win, text='Создать', command=lambda: self.profile_name_check(var, win)).pack(expand=1)

    def profile_name_check(self, field, window):
        name = field.get()
        if len(name) > 2:
            if name.title() in self.profile_name_buttons:
                showerror('Ошибка', f'[{name}] уже существует. Пожалуйста выбери другое имя')
                return
            window.destroy()
            self.create_profile(name)
        else:
            showerror('Ошибка', 'Имя профиля должно содержать от 2 символов')

    def create_profile(self, name):
        add_profile_window = AskWindowSample(self, 'Новый профиль', (400, 700), ['Name'], 90)
        add_profile_window.create_entry_parameter_field('Объем', int)
        add_profile_window.wait_window()
        for field in add_profile_window.result:
            if not add_profile_window.result[field]:
                return
        inv = Inventory('root', int(add_profile_window.result.pop('Объем')))
        p = Profile(name.title(), inv, **add_profile_window.result)
        profile_names.append(name)
        DATABASE['profiles'].append(p)
        Database.save(DATABASE)
        self.refresh_profile_buttons()

    def delete_profile(self, window, profile):
        if askyesno('Подтвердите действие', f'Вы дейтвительно хотите удалить профиль {profile.name}?'):
            window.destroy()
            DATABASE['profiles'].remove(profile)
            self.profile_name_buttons.pop(profile.name).destroy()
            Database.save(DATABASE)
            showinfo('Готово!', f'Профиль: {profile.name} был успешно удален!')


# ----------------------------------------------------------------------


class ProfileWindow(DisplayWindow):
    def __init__(self, parent, profile):
        DisplayWindow.__init__(self, parent, f'Профиль: {profile.name}', (550, 700),
                               profile.name, profile.inventory.space, True, **profile.stats)
        self.aside_frame = Frame(self)
        self.aside_frame.pack(side=RIGHT, fill=Y, padx=8, pady=10, anchor=NE)
        self.profile = profile

        self.create_aside_menu()

    def create_aside_menu(self):
        samples = {
            'Квесты': QuestsWindow,
            'Инвентарь': InventoryWindow,
            'Достижения': AchievementsWindow
        }
        for sample in samples:
            Button(self.aside_frame, width=15, text=sample, command=lambda i=sample: samples[i](self, self.profile if
                   samples[i] is not InventoryWindow else self.profile.inventory)).pack(pady=5, side=TOP)

        Button(self.aside_frame, text='Удалить профиль', command=lambda: root.delete_profile(self, self.profile))\
            .pack(side=BOTTOM, pady=5, anchor=SE)


class QuestsWindow(DisplayWindow):
    def __init__(self, parent, profile):
        DisplayWindow.__init__(self, parent, f'{profile.name} Квесты', (800, 500), profile.name, 'Квесты', False)
        self.aside = Frame(self)
        self.profile = profile
        self.aside.pack(side=RIGHT, fill=Y)
        self.create_aside_panel()
        self.existing_quests = {}
        self.post_quests()

    def create_aside_panel(self):
        Button(self.aside, text='Создать квест', height=3, width=15, command=self.add_quest).pack(padx=10, pady=10)

    def add_quest(self):
        add_quest_window = AskWindowSample(self, 'Новый квест', (500, 700), [], 4)
        add_quest_window.create_entry_parameter_field('Название', str)
        add_quest_window.create_text_parameter_field('Описание')
        add_quest_window.create_combobox_parameter_field('Получен от', [x.name for x in DATABASE['npcs']])
        add_quest_window.create_item_parameter_field('Награда', DATABASE['items'])
        add_quest_window.wait_window()
        result = add_quest_window.result
        try:
            parent = npc_by_names[result['Получен от']]
        except KeyError:
            showerror('Ошибка', 'Неверный НИП')
            return
        for key in result:
            if not result[key]:
                return 0
        q = Quest(result['Описание'], parent, result['Награда'], result['Название'].title())
        self.profile.quests.append(q)
        Database.save(DATABASE)
        self.post_quests()

    def create_quest_environment(self, q):
        self.canvas.config(width=670, height=400)
        container = Frame(self.frame_inside, bd=2, bg='black')
        container.pack(expand=1, pady=20, padx=20, anchor=N)

        right_buttons_ = Frame(container)
        right_buttons_.pack(side=RIGHT, fill=Y)
        delete_b = Button(right_buttons_, text='Удалить квест', width=10, command=lambda: self.delete_quest_frame(q))
        delete_b.pack(fill=Y, expand=1)
        give_awards = Button(right_buttons_, text='Выдать награду', width=10, command=lambda: self.give_award(q))
        give_awards.pack(fill=Y, expand=1)

        quest_details_ = Frame(container)
        quest_details_.pack(fill=BOTH, expand=1)

        quest_name_ = Frame(quest_details_, bd=2, relief=SOLID)
        quest_name_.pack(fill=X, expand=1, anchor=N)
        quest_name = Label(quest_name_, text=q.name, font=('Times New Roman', 20, 'bold'))
        quest_name.pack(expand=1, pady=5)

        buttons_inside_ = Frame(quest_details_)
        buttons_inside_.pack(fill=Y, side=RIGHT)
        g_by = Button(buttons_inside_, text='Получен от', width=10,
                      command=lambda i=q: NPCWindow(self, i.parent, (500, 600), False))
        g_by.pack(fill=Y, expand=1)
        show_awards = Button(buttons_inside_, text='Показать награды',
                             width=10, command=lambda i=q: ItemsList(self, f'{i.name} награды',
                                                                     (300, 500), i.award, False, 1))
        show_awards.pack(fill=Y, expand=1)

        description_ = Frame(quest_details_, relief=SOLID)
        description = Canvas(quest_details_)
        scroll_desc = Scrollbar(description_, command=description.yview)
        description.config(yscrollcommand=scroll_desc.set, width=450, height=100)
        scroll_desc.pack(side=RIGHT, fill=Y)
        description.pack(fill=BOTH, expand=1)
        return quest_name, description, container

    def post_quests(self):
        for quest in self.profile.quests:
            if quest not in self.existing_quests:
                quest_name, desc, c = self.create_quest_environment(quest)
                self.existing_quests[quest] = c
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

    def give_award(self, quest):
        if quest.award and quest.status:
            for item in quest.award:
                if self.profile.inventory.weight_access_check(quest.award[item]['instance'], 1):
                    self.profile.inventory.put(quest.award[item]['instance'])
                else:
                    showerror('Error', f'{item} слишком велик по размеру и не помещается в ваш инвентарь')
            quest.status = 0
            Database.save(DATABASE)
        else:
            showinfo('Инфо', 'Наград нет или они уже были получены раньше')

    def delete_quest_frame(self, quest):
        if askyesno('Подтвердите действие', 'Вы действительно хотите удалить этот квест?'):
            self.profile.quests.remove(quest)
            Database.save(DATABASE)
            self.existing_quests.pop(quest).destroy()


class InventoryWindow(AbstractWindow):
    def __init__(self, parent, inventory: Inventory, title='Общий инвентарь'):
        AbstractWindow.__init__(self, parent, title, (800, 500))
        self.show_about = Frame(self)
        self.list_frame = Frame(self)
        self.profile_items = inventory
        self.absolute_space = Label(self.list_frame, font=('Arial', 15, 'bold'),
                                    text=f'Заполнено: {self.profile_items.space - self.profile_items.get_abs_space()} /'
                                         f' {self.profile_items.space}')
        self.absolute_space.pack(expand=1, pady=10)
        self.scroll, self.list = self.create_listbox()
        self.list_frame.pack(side=LEFT, expand=1, fill=BOTH, padx=50, pady=50)
        self.active = None

        Button(self, text='Добавить вещь', command=self.add_item_request).pack(side=RIGHT, anchor=N, padx=10, pady=10)

        self.show_about.pack(side=RIGHT, expand=1, fill=BOTH, padx=20, pady=20)
        self.info, self.canvas = self.create_canvas()

    def add_item_request(self):
        add_item_list_window = ItemSelectionWindow(self, 'Выберите вещи', DATABASE['items'])
        add_item_list_window.wait_window()

        if add_item_list_window.selected_items:
            for item_key in add_item_list_window.selected_items:
                item = DATABASE['items'].inventory[item_key]['instance']
                if not self.profile_items.weight_access_check(item, 1):
                    break
                elif not self.quantity_check(1, item_key):
                    break
            else:
                self.sort_item_quantify(add_item_list_window.selected_items)
                Database.save(DATABASE)
                self.update_listbox()

    def sort_item_quantify(self, selected):
        for item in selected:
            self.profile_items.put(DATABASE['items'].inventory[item]['instance'])

    def update_listbox(self):
        self.list.destroy()
        self.scroll.destroy()
        self.absolute_space.config(text=f'Заполнено: {self.profile_items.space - self.profile_items.get_abs_space()} /'
                                        f' {self.profile_items.space}')
        self.scroll, self.list = self.create_listbox()

    def fill_list(self, li):
        on_delete = []
        for key in self.profile_items.inventory:
            if key in DATABASE['items'].inventory:
                li.insert(END, f'[x{self.profile_items.inventory[key]["quantify"]}] {key}')
            else:
                on_delete.append(key)
        for k in on_delete:
            self.profile_items.inventory.pop(k)

    def create_canvas(self):
        canvas = Canvas(self.show_about, relief=SOLID)
        s = Scrollbar(self.show_about, command=canvas.yview)
        inside = Frame(canvas)
        inside.bind('<Configure>', lambda event: canvas.config(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=inside, anchor=NW)
        s.pack(side=RIGHT, fill=Y)
        canvas.config(yscrollcommand=s.set)
        canvas.pack(expand=1, fill=BOTH)
        return inside, canvas

    def create_listbox(self):
        listbox = Listbox(self.list_frame, selectmode=SINGLE, height=200, relief=SOLID)
        s = Scrollbar(self.list_frame, command=listbox.yview)
        s.pack(fill=Y, side=RIGHT)
        listbox.config(yscrollcommand=s.set)
        listbox.bind('<Double-1>', lambda event: self.on_click())
        listbox.bind('<Button-3>', lambda event: self.redirection_to_note_window())
        listbox.pack()
        self.fill_list(listbox)
        return s, listbox

    def redirection_to_note_window(self):
        item = self.get_tools()
        TextNotesWindow(self, f'{item.name}: Заметки', (600, 400), item)

    def get_tools(self):
        index = self.list.curselection()[0]
        itemname = self.list.get(index)[self.list.get(index).find(']') + 2:]
        item = self.profile_items.inventory[itemname]['instance']
        return item

    def on_click(self):
        item = self.get_tools()
        if self.active is not None:
            self.active.destroy()
        self.active = self.show_info(item)

    def show_info(self, item):
        container = Frame(self.info)
        container.pack(expand=1, fill=BOTH)
        header = Frame(container)
        header.pack(fill=X, expand=1, anchor=N)
        Label(header, text=f'{item.name} stats', font=('Times New Roman', 15, 'bold')).pack(side=LEFT)
        Button(header, text='Удалить вещь', command=lambda i=item: self.delete_item(i)).pack(side=RIGHT,
                                                                                             padx=10, pady=10)
        if isinstance(item, Inventory):
            Button(header, text='Открыть...',
                   command=lambda: InventoryWindow(self, item, f'Вложение {item.name}')).pack(expand=1, fill=BOTH)
            Database.save(DATABASE)
            return container
        Button(header, text='Изменить кол-во',
               command=lambda i=item: self.create_change_quantify_window(i)).pack(side=RIGHT, pady=10)
        params_frame = Frame(container)
        params_frame.pack(expand=1, fill=BOTH)
        self.display_row(params_frame, 'Вес', item.weight, 0)
        for n, parameter in enumerate(item.stats):
            self.display_row(params_frame, parameter, item.stats[parameter], n + 1)
        return container

    # change = -1
    def change_quantify(self, txt, key, change: int):
        item = DATABASE['items'].inventory[key]['instance']
        if self.profile_items.weight_access_check(item, change):
            if self.quantity_check(change, key):
                self.profile_items.inventory[key]["quantify"] += change
            else:
                return
        else:
            showerror('Ошибка', 'Инвентарь не вмещает столько по весу!')
            return
        self.update_quantity_number(txt, key)

    def update_quantity_number(self, txt, k):
        txt.config(text=f'Текущее кол-во: {self.profile_items.inventory[k]["quantify"]}')
        Database.save(DATABASE)

    # Расчитывает кол-во вещи, не может принимать ниже 1
    def quantity_check(self, change, item_key):
        try:
            quantity = self.profile_items.inventory[item_key]['quantify']
        except KeyError:
            quantity = 0
        print(quantity + change, quantity, change)
        if change < 0 and quantity + change < 1:
            showerror('Ошибка', 'Вещь не может иметь отрицательно кол-во')
            return False
        return True

    def create_change_quantify_window(self, i: Item):
        win = AbstractWindow(self, 'Изменить кол-во', (300, 200))
        center = Frame(win)
        center.pack(expand=1, padx=20, pady=20)
        text = Label(win, text=f'Текущее кол-во: {self.profile_items.inventory[i.name]["quantify"]}',
                     font=('Times New Roman', 20, 'bold'))
        for n, x in enumerate(['-100', '-10', '-1', '+1', '+10', '+100']):
            Button(center, text=x, command=lambda r=x: self.change_quantify(text, i.name, int(r)),
                   width=5).grid(row=0, column=n)
        text.pack(expand=1, pady=20)
        win.wait_window()
        self.update_listbox()

    def delete_item(self, item: Item):
        if askyesno('Подтвердите', 'Вы действительно хотите удалить эту вещь?'):
            self.profile_items.inventory.pop(item.name)
            self.active.destroy()
            self.active = None
            Database.save(DATABASE)
            self.update_listbox()

    @staticmethod
    def display_row(f, key, value, row):
        for num, text in enumerate([key, value]):
            Label(f, text=text, width=15, height=3,
                  font=('Times New Roman', 15, 'normal'), relief=SOLID).grid(row=row, column=num)


class TextNotesWindow(AbstractWindow):
    def __init__(self, parent, title, msize, item):
        AbstractWindow.__init__(self, parent, title, msize)
        self.item = item
        header = Frame(self)
        header.pack(fill=X, expand=1, anchor=N)

        Button(header, text='Сохранить', command=lambda: self.save_notes()).pack(padx=10)

        self.t = Text(self)
        self.t.pack(padx=10, pady=10)
        self.t.insert('1.0', item.notes)

    def save_notes(self):
        self.item.notes = self.t.get('1.0', END+'-1c')
        Database.save(DATABASE)


class AchievementsWindow(DisplayWindow):
    def __init__(self, parent, profile):
        DisplayWindow.__init__(self, parent, f'{profile.name} Достижения', (700, 500), profile.name, 'Достижения', False)
        self.existing_achieves = {}
        self.profile = profile
        Button(self, text='Создать достижение', command=lambda: self.add_achieve(),
               width=15, height=2).pack(side=RIGHT, anchor=NE, padx=8, pady=8)
        self._iterate_achieves()

    def add_achieve(self):
        ask_achieve_window = AskWindowSample(self, 'Новое достижение', (500, 600), [], 2)
        ask_achieve_window.create_entry_parameter_field('Название', str)
        ask_achieve_window.create_text_parameter_field('Описание')
        ask_achieve_window.wait_window()
        result = ask_achieve_window.result
        if self.check_box(ask_achieve_window.result):
            self.profile.add_achieve(Achievement(result['Название'], result['Описание']))
            Database.save(DATABASE)
            self.update_achieves()

    def update_achieves(self):
        for key in self.existing_achieves:
            self.existing_achieves[key].destroy()
        self._iterate_achieves()

    @staticmethod
    def check_box(box):
        if box:
            for element in box:
                if not box[element]:
                    break
            else:
                return 1
        return 0

    def _iterate_achieves(self):
        self.existing_achieves = {}
        for achieve in self.profile.achievements:
            border, name, description = self.accommodate_achievement_frames()
            Button(border, text='Удалить достижение',
                   command=lambda: self.delete_achievement(achieve)).pack(fill=Y, side=RIGHT)
            Label(name, text=achieve.name, width=20,
                  font=('Times New Roman', 20, 'bold')).pack(padx=10, pady=10, expand=1, anchor=W)
            Label(description, text=achieve.description, relief=SOLID,
                  font=('Arial', 12, 'normal')).pack(padx=5, pady=5, expand=1, fill=BOTH)

            self.existing_achieves[achieve.name] = border

    def delete_achievement(self, ach: Achievement):
        if askyesno('Подтвердите действие', 'Вы действительно хотите удалить это достижение?'):
            self.profile.achievements.remove(ach)
            self.existing_achieves.pop(ach.name).destroy()
            Database.save(DATABASE)
            self.update_achieves()

    def accommodate_achievement_frames(self):
        achieve_area = Frame(self.frame_inside, relief=SOLID, bd=1)
        achieve_area.pack(expand=1, fill=X, anchor=N, padx=10, pady=10)

        achieve_name_area = Frame(achieve_area)
        achieve_name_area.pack(fill=X, expand=1, anchor=N)

        achieve_description_area = Frame(achieve_area)
        achieve_description_area.pack(fill=BOTH, expand=1)

        return achieve_area, achieve_name_area, achieve_description_area


class NotPlayerCharactersWindow(DisplayWindow):
    def __init__(self, parent, title, msize, name, core):
        DisplayWindow.__init__(self, parent, title, msize, name, core, False)
        self.aside_panel = Frame(self)
        self.buttons = {}
        self.aside_panel.pack(side=RIGHT, fill=Y)
        self.canvas.config(height=500)
        self.fill_npc_list()
        Button(self.aside_panel, text='Добавить НИПа', command=self.create_new_npc).pack(padx=10, pady=10)

    def fill_npc_list(self):
        for character in DATABASE['npcs']:
            if character.name not in self.buttons:
                npc_button = Button(self.frame_inside, text=character.name, width=15,
                                    font=('Times New Roman', 30, 'bold'),
                                    command=lambda i=character: NPCWindow(self, i, (500, 700), True), relief=SOLID)
                npc_button.pack(pady=10, padx=10, expand=1, fill=X)
                self.buttons[character.name] = npc_button

    def create_new_npc(self):
        add_npc_window = AskWindowSample(self, 'Новый НИП', (500, 500), [])
        add_npc_window.create_entry_parameter_field('Имя', str)
        add_npc_window.create_entry_parameter_field('Раса', str)
        add_npc_window.create_entry_parameter_field('Где обитает', str)
        add_npc_window.create_entry_parameter_field('Чем занимается', str)
        add_npc_window.wait_window()
        if add_npc_window.result['Имя'] and add_npc_window.result['Имя'].title() in npc_by_names:
            showerror('Ошибка', 'Такой НИП уже существует')
            return
        result = add_npc_window.result
        if self.check_box(result):
            npc = NotPlayerCharacter(result['Имя'], result['Раса'], result['Где обитает'], result['Чем занимается'])
            DATABASE['npcs'].append(npc)
            npc_by_names[npc.name] = npc
            Database.save(DATABASE)
        self.fill_npc_list()

    def delete(self, character):
        self.buttons.pop(character.name).destroy()
        DATABASE['npcs'].remove(character)
        npc_by_names.pop(character.name)
        Database.save(DATABASE)

    @staticmethod
    def check_box(box) -> int:
        for el in box:
            if not box[el]:
                return 0
        else:
            return 1


class NPCWindow(DisplayWindow):
    def __init__(self, parent, npc_object, msize, rootpermissions: bool):
        print(type(npc_object))
        DisplayWindow.__init__(self, parent, f'НИП: {npc_object.name}', msize, npc_object.name,
                               'Профиль НИПа', True, **npc_object.get_stats())

        self.aside_panel = Frame(self)
        self.aside_panel.pack(fill=Y, side=RIGHT)

        if rootpermissions:
            Button(self.aside_panel, text='Удалить НИПа',
                   command=lambda: self.delete_npc(parent, npc_object)).pack(padx=10, pady=10)

    def delete_npc(self, parent, npc):
        parent.delete(npc)
        self.destroy()
        showinfo('Инфо', f'{npc.name} был успешно удален!')


root = MainWindow()
if __name__ == '__main__':
    root.mainloop()
