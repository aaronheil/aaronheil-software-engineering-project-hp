import tkinter as tk
from tkinter import simpledialog, messagebox
import selection_screen
import pygame
import variables
from variables import User, Session, HomeAreaUI, UserInteraction, every_username_session, AppState
import main
from main import Leaderboard, Session

# Importe aus


from tkinter import ttk

from home_area_backend import UsernameManager, UserInterfaceManager, WindowManager, MusicManager
from PIL import Image, ImageTk
from variables import HomeAreaUI, AppState, User, UserInteraction, every_username_session
from main import session

"""Backend-Logik"""


class WindowManager:
    @staticmethod
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')


class UsernameManager:
    """
        Verwaltet Benutzeroperationen bezüglich der Überprüfung, Hinzufügung und Abfrage von Benutzernamen.
    """

    @staticmethod
    def is_username_existing(username):
        """
        Prüft, ob ein Benutzername bereits in der Datenbank existiert.

        Args:
            username: Der zu überprüfende Benutzername.

        Returns:
            True, wenn der Benutzername existiert, sonst False.
        """
        return every_username_session.query(User).filter_by(username=username).first() is not None

    @staticmethod
    def add_username(username):
        """
        Fügt einen neuen Benutzernamen hinzu, wenn dieser noch nicht existiert.

        Args:
            username: Der hinzuzufügende Benutzername.

        Returns:
            True, wenn der Benutzername erfolgreich hinzugefügt wurde, sonst False.
        """
        if not UsernameManager.is_username_existing(username):
            new_user = User(username=username)
            every_username_session.add(new_user)
            every_username_session.commit()
            return True
        return False

    @staticmethod
    def get_recent_usernames(limit=10):
        """
        Ruft die neuesten Benutzernamen basierend auf der angegebenen Limitierung ab.

        Args:
            limit: Die maximale Anzahl der zurückzugebenden Benutzernamen.

        Returns:
            Eine Liste der neuesten Benutzernamen.
        """
        return [user.username for user in every_username_session.query(User.username).order_by(User.id.desc()).limit(limit)]

    @staticmethod
    def search_username(search_term):
        """
        Sucht nach Benutzernamen, die den Suchbegriff enthalten.

        Args:
            search_term: Der Begriff, nach dem in Benutzernamen gesucht wird.

        Returns:
            Eine Liste von Benutzernamen, die den Suchbegriff enthalten.
        """
        return every_username_session.query(User.username).filter(User.username.like(f"%{search_term}%")).all()


class UserInterfaceManager:
    def __init__(self, session, home_area_ui, home_frame, app_state, username_manager, user_interaction):
        self.session = session
        self.home_frame = home_frame
        self.app_state = app_state  # Speichert die AppState-Instanz als Attribut
        self.username_manager = username_manager
        self.home_area_ui = home_area_ui
        self.user_interaction = user_interaction


    def on_name_submit(self):
        username = self.user_interaction.dropdown_var.get()
        if self.username_manager.add_username(username):
            self.update_ui_with_new_username(username)
        else:
            tk.messagebox.showinfo("Info", "Dieser Name existiert bereits.")

    def update_ui_with_new_username(self, username):
        self.app_state.current_username = username
        # z.B. für Welcome Label etc.

    def get_all_usernames(self):
        return every_username_session.query(User.username).all()

    def get_or_create_username(self):
        session = Session()
        latest_entry = session.query(main.Leaderboard).order_by(main.Leaderboard.played_on.desc()).first()
        if latest_entry:
            user = session.query(User).filter_by(id=latest_entry.user_id).first()
            if user:
                return user.username
        username = simpledialog.askstring("Benutzername", "Wie lautet Ihr Name?")
        if username and not UsernameManager.is_username_existing(username):
            self.username_manager.add_username(username)
        return username if username else "Unbekannter Benutzer"

    def change_user(label):
        label.create_new_user_window(selection_screen.home_frame)

    def update_dropdown(self, *args):
        search_term = UsernameManager.search_var.get()  # search_var wird genutzt in home_area_frontend.py
        filtered_names = UsernameManager.search_username(search_term)
        self.home_area_ui.dropdown_list.delete(0, 'end')  # Löscht alle Einträge in der Listbox

        if not filtered_names:
            tk.messagebox.showinfo("Suche", "Kein passender Benutzername gefunden.")
        else:
            for item in filtered_names:
                self.home_area_ui.dropdown_list.insert('end', item[0])

    def on_dropdown_select(self, event):
        selected_index = self.home_area_ui.dropdown_list.curselection()
        selected_name = self.home_area_ui.dropdown_list.get(selected_index)
        event.update_ui_with_new_username(selected_name)

    def on_double_click(self, event):
        selected_indices = self.home_area_ui.dropdown_list.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            selected_name = self.home_area_ui.dropdown_list.get(selected_index)
            self.update_ui_with_new_username(selected_name)

    def on_right_click(self, event):
        selected_indices = self.home_area_ui.dropdown_list.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            selected_name = self.home_area_ui.dropdown_list.get(selected_index)
            if tk.messagebox.askyesno("Löschen", f"Möchten Sie '{selected_name}' löschen?"):
                user_to_delete = self.session.query(User).filter_by(username=selected_name).first()
                if user_to_delete:
                    self.session.delete(user_to_delete)
                    self.session.commit()
                    self.update_dropdown()

        else:
            tk.messagebox.showwarning("Warnung", "Kein Benutzer ausgewählt.")

    def on_enter_pressed(self, event):
        selected_indices = self.home_area_ui.dropdown_list.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            selected_name = self.home_area_ui.dropdown_list.get(selected_index)
            self.update_ui_with_new_username(selected_name)
        else:
            tk.messagebox.showwarning("Warnung", "Kein Benutzer ausgewählt.")


# Funktionen zum Handling bei Anlage eines neuen Benutzernamens

    def create_new_user_window(self, home_frame):
        """ Öffnet ein kleines neues Fenster zur Eingabe des neuen Benutzernamens"""
        new_user_window = tk.Toplevel(home_frame)
        new_user_window.title("Neuen Benutzer anlegen")
        WindowManager.center_window(new_user_window, 400, 200)

        tk.Label(new_user_window, text="Bitte geben Sie den neuen Benutzernamen ein:").pack(pady=20)

        username_entry = tk.Entry(new_user_window)
        username_entry.pack()

        def submit_new_username():
            """ Überprüfung und Speicherung des neuen Benutzernamens"""
            username = username_entry.get()
            if username:
                if self.username_manager.add_username(username):  # Verwende die Klasse UsernameManager
                    self.update_ui_with_new_username(username, new_user_window)  # Annahme einer angepassten Methode
                    new_user_window.destroy()
                else:
                    tk.messagebox.showwarning("Warnung", "Benutzername existiert bereits!")
            else:
                tk.messagebox.showwarning("Warnung", "Benutzername darf nicht leer sein!")

        submit_button = tk.Button(new_user_window, text="Submit", command=submit_new_username)
        submit_button.pack(pady=20)


class MusicManager:
    """ Logik zum Musik ein- und ausschalten"""
    def __init__(self, app_state):
        self.app_state = app_state

    def toggle_music(self):
        if self.app_state.is_music_playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.app_state.is_music_playing = not self.app_state.is_music_playing


"""Frontend-Logik"""



class HomeAreaFrontend:
    def __init__(self, master, home_frame):
        self.master = master
        self.home_frame = home_frame
        self.active_button = None
        self.home_area_ui = HomeAreaUI()
        self.app_state = AppState()  # AppState Instanz erstellen
        self.user = User()
        self.music_manager = MusicManager(self.app_state)
        self.username_manger = UsernameManager()
        self.user_interaction = UserInteraction()
        self.ui_manager = UserInterfaceManager(session=home_area_backend,
                                               home_frame=self.home_frame,
                                               app_state=self.app_state,
                                               username_manager=self.username_manger,
                                               user_interaction=self.user_interaction,
                                               home_area_ui=self.home_area_ui)
        self.setup_ui()
        self.set_and_update_username()

    def set_and_update_username(self):
        # Setzt den Benutzernamen und aktualisiert anschließend das Welcome-Label
        username = self.ui_manager.get_or_create_username()  # Diese Methode muss den Benutzernamen synchron zurückgeben
        self.app_state.current_username = username  # Aktualisiere den AppState mit dem neuen Benutzernamen
        self.update_welcome_label()  # Aktualisiere das Welcome-Label mit dem neuen Benutzernamen

    def update_welcome_label(self):
        # Aktualisiert das Welcome-Label mit dem aktuellen Benutzernamen
        welcome_text = f"Hallo {self.app_state.current_username}"
        self.welcome_label.config(text=welcome_text)


    def setup_ui(self):
        # Erstellen des Top-Frames für Begrüßung und Aktionen-Button
        self.top_frame = tk.Frame(self.home_frame, bg='#343a40')
        self.top_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.welcome_label = tk.Label(self.top_frame, text="Hallo",
                                      font=("Harry P", 30),
                                      relief=tk.RAISED)
        self.welcome_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

        # Aktionen-Menübutton
        self.actions_button = tk.Menubutton(self.top_frame, text="Aktionen", font=("Harry P", 30), relief=tk.RAISED,
                                            width=20)
        self.actions_menu = tk.Menu(self.actions_button, tearoff=0)
        self.actions_button["menu"] = self.actions_menu
        self.actions_button.grid(row=0, column=1, sticky='w', padx=10, pady=10)

        # Unterbuttons zum Menubutton hinzufügen
        self.actions_menu.add_command(label="Neuen User anlegen",
                                      command=lambda: self.ui_manager.create_new_user_window(self.home_frame),
                                      font=("Arial", 16), background='white', foreground='black')

        self.actions_menu.add_separator()
        self.actions_menu.add_command(label="User auswählen", command=self.show_dropdown,
                                      font=("Arial", 16),
                                      background='white', foreground='black')

        self.actions_menu.add_separator()
        self.actions_menu.add_command(label="Musik Ein / Aus", command=self.music_manager.toggle_music,
                                      font=("Arial", 16),
                                      background='white', foreground='black')

        # Button-Frame für die Auswahl der Häuser
        self.button_frame = tk.Frame(self.home_frame, bg='#343a40')
        self.button_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
        self.button_frame.grid_columnconfigure([0, 1, 2, 3], weight=1)
        self.button_frame.grid_rowconfigure(0, weight=1)

        # Funktionen zum Laden und Skalieren der Bilder
        def load_and_resize_image(image_path, size=(400, 500)):
            original_image = Image.open(image_path)
            resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(resized_image)

        # Hausauswahl-Buttons erstellen und im button_frame positionieren
        image_gryffindor = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\gryffindor.png")
        btn_gryffindor = tk.Button(self.button_frame, image=image_gryffindor,
                                   command=lambda: self.on_house_select('Gryffindor', self.current_username))
        btn_gryffindor.grid(row=0, column=0, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

        image_slytherin = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\slytherin.png")
        btn_slytherin = tk.Button(self.button_frame, image=image_slytherin,
                                  command=lambda: self.on_house_select('Slytherin', self.current_username))
        btn_slytherin.grid(row=0, column=1, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

        image_hufflepuff = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\hufflepuff.png")
        btn_hufflepuff = tk.Button(self.button_frame, image=image_hufflepuff,
                                   command=lambda: self.on_house_select('Hufflepuff', self.current_username))
        btn_hufflepuff.grid(row=0, column=2, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

        image_ravenclaw = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\ravenclaw.png")
        btn_ravenclaw = tk.Button(self.button_frame, image=image_ravenclaw,
                                  command=lambda: self.on_house_select('Ravenclaw', self.current_username))
        btn_ravenclaw.grid(row=0, column=3, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

        # Halten Sie die Bildreferenzen, um die automatische Bereinigung durch Garbage Collector zu verhindern
        self.button_frame.image_gryffindor = image_gryffindor
        self.button_frame.image_slytherin = image_slytherin
        self.button_frame.image_hufflepuff = image_hufflepuff
        self.button_frame.image_ravenclaw = image_ravenclaw

    def on_house_select(self, house_name):
        if not self.current_username:
            messagebox.showinfo("Fehler", "Bitte erst einen Benutzer auswählen.")
            return
        if not house_name:
            messagebox.showinfo("Fehler", "Bitte erst ein Haus auswählen.")
            return
        self.house = house_name  # Verwende self.house statt global
        print(f"{house_name} ausgewählt, Benutzer: {self.current_username}")
        # switch_frame und start_quiz müssen entsprechend angepasst werden
        """
               switch_frame(quiz_frame)
               update_active_button(quiz_button)
               start_quiz(house_name, username)
       """

    def switch_to_quiz(self):
        if self.is_quiz_active:
            messagebox.showinfo("Info", "Das Quiz läuft bereits.")
            return
        # Die Methode switch_frame muss angepasst werden, um innerhalb der Klasse zu funktionieren
        self.switch_frame("quiz")
        self.update_active_button(self.quiz_button)
        # Überprüfe, ob ein Benutzername und ein Haus ausgewählt wurden
        if self.current_username and self.house:
            # Die Methode start_quiz muss angepasst werden, um innerhalb der Klasse zu funktionieren
            self.start_quiz(self.house, self.current_username)
        else:
            messagebox.showinfo("Info", "Bitte wählen Sie einen Benutzer und ein Haus, bevor Sie das Quiz starten.")
            self.switch_to_home()  # Stellt sicher, dass auch diese Methode entsprechend angepasst ist

    def show_dropdown(self):
        # Erstellt ein neues Fenster für das Dropdown-Menü
        self.dropdown_window = tk.Toplevel(self.master)
        self.dropdown_window.title("User auswählen")
        # Zentriert das Dropdown-Fenster auf dem Bildschirm
        WindowManager.center_window(self.dropdown_window, 300, 200)

        # Fügt eine Suchleiste hinzu, um Benutzern zu ermöglichen, nach Namen zu suchen
        search_var = tk.StringVar()
        search_entry = tk.Entry(self.dropdown_window, textvariable=search_var)
        search_entry.pack(fill='x')  # Fügt die Suchleiste zum Fenster hinzu

        # Initialisiert einen Frame, der die Listbox und Scrollbar enthält
        listbox_frame = tk.Frame(self.dropdown_window)
        listbox_frame.pack(fill='both', expand=True)

        # Fügt eine Scrollbar hinzu, um durch die Listbox scrollen zu können
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')

        # Initialisiert die Listbox, die die Namen anzeigt
        self.dropdown_list = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=10)
        self.dropdown_list.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.dropdown_list.yview)  # Verbindet die Scrollbar mit der Listbox

        # Definiert eine Wrapper-Funktion für das KeyRelease-Event der Suchleiste
        def on_search_key_release(*args):
            # Ruft update_dropdown mit dem aktuellen Wert der Suchleiste und der Dropdown-Liste als Argumente auf
            search_term = self.search_var.get()  # Erhält den aktuellen Text der Suchleiste
            self.ui_manager.update_dropdown(search_term, self.dropdown_list)  # Korrekter Aufruf der Methode

        search_entry.bind('<KeyRelease>', on_search_key_release)

        # Bindet verschiedene Event-Handler für die Listbox, um auf Benutzeraktionen zu reagieren
        self.dropdown_list.bind('<Double-1>', self.ui_manager.on_double_click)  # Doppelklick
        self.dropdown_list.bind('<Button-3>', self.ui_manager.on_right_click)  # Rechtsklick
        self.dropdown_list.bind('<Return>', self.ui_manager.on_enter_pressed)  # Enter-Taste


"""
# Initialisiere die Listbox mit allen Benutzernamen
#update_dropdown()



    def update_active_button(new_active_button):
        global active_button
        # Setzen Sie alle Buttons auf normale Farbe zurück
        for button in [home_button, quiz_button, erfolge_button, statistik_button]:
            button.config(bg='SystemButtonFace')  # Setzen Sie die Standardfarbe zurück
        # Setzen Sie die Farbe des aktiven Buttons
        new_active_button.config(bg='lightgrey')  # Hervorheben des aktiven Buttons
        active_button = new_active_button
"""




