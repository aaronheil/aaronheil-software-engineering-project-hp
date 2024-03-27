import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

import selection_screen

import pygame
from variables import User, Session, HomeAreaUI, UserInteraction, every_username_session, AppState
import main
from main import Leaderboard, Session, session
from PIL import Image, ImageTk


import datetime
from main import choose_quiz, get_db_session, Leaderboard, User
from variables import QuizConfig, AppState, User, BotConfig
from bots_logic import bots, update_bot_scores



# Backend-Logik


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
    def __init__(self, session, home_area_ui, home_frame, app_state, username_manager, user_interaction, home_area_frontend):
        self.session = session
        self.home_frame = home_frame
        self.app_state = app_state  # Speichert die AppState-Instanz als Attribut
        self.username_manager = username_manager
        self.home_area_ui = home_area_ui
        self.user_interaction = user_interaction
        self.search_var = tk.StringVar()
        self.home_area_frontend = home_area_frontend


    def on_name_submit(self):
        username = self.user_interaction.dropdown_var.get()
        if self.username_manager.add_username(username):
            self.update_ui_with_new_username(username)
        else:
            tk.messagebox.showinfo("Info", "Dieser Name existiert bereits.")

    def update_ui_with_new_username(self, username):
        self.app_state.current_username = username
        self.home_area_frontend.update_welcome_label()
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
        search_term = self.search_var.get()  # search_var wird genutzt in home_area_frontend.py
        filtered_names = UsernameManager.search_username(search_term)
        self.home_area_ui.dropdown_list.delete(0, 'end')  # Löscht alle Einträge in der Listbox

        if not filtered_names:
            tk.messagebox.showinfo("Suche", "Kein passender Benutzername gefunden.")
        else:
            for item in filtered_names:
                self.home_area_ui.dropdown_list.insert('end', item[0])

    def on_dropdown_select(self, event):
        selected_index = self.home_area_ui.dropdown_list.curselection()
        if selected_index:
            selected_name = self.home_area_ui.dropdown_list.get(selected_index)
            self.update_ui_with_new_username(
                selected_name)  # Stellt sicher, dass diese Zeile korrekt den Namen übergibt

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
                if self.username_manager.add_username(username):
                    self.update_ui_with_new_username(username)  # Aufruf über die HomeAreaFrontend Instanz
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


# Frontend-Logik



class HomeAreaFrontend:
    def __init__(self, master, home_frame, switch_to_quiz_callback, switch_frame_callback, selection_screen_instance):
        self.master = master
        self.home_frame = home_frame
        self.active_button = None
        self.home_area_ui = HomeAreaUI()
        self.app_state = AppState()  # AppState Instanz erstellen
        self.user = User()
        self.bot_config = BotConfig()
        self.music_manager = MusicManager(self.app_state)
        self.username_manger = UsernameManager()
        self.user_interaction = UserInteraction()
        self.ui_manager = UserInterfaceManager(session=session,
                                               home_frame=self.home_frame,
                                               app_state=self.app_state,
                                               username_manager=self.username_manger,
                                               user_interaction=self.user_interaction,
                                               home_area_ui=self.home_area_ui,
                                               home_area_frontend=self,
                                               )
        self.setup_ui()
        self.set_and_update_username()
        self.switch_to_quiz_callback = switch_to_quiz_callback
        self.switch_frame_callback = switch_frame_callback
        self.selection_screen_instance = selection_screen_instance


    def set_and_update_username(self):
        # Setzt den Benutzernamen und aktualisiert anschließend das Welcome-Label
        username = self.ui_manager.get_or_create_username()  # Diese Methode muss den Benutzernamen synchron zurückgeben
        self.app_state.current_username = username  # Aktualisiere den AppState mit dem neuen Benutzernamen
        self.update_welcome_label()  # Aktualisiere das Welcome-Label mit dem neuen Benutzernamen

    def update_welcome_label(self):
        # Aktualisiert das Welcome-Label mit dem aktuellen Benutzernamen
        welcome_text = f"Hallo {self.app_state.current_username}"
        self.home_area_ui.welcome_label.config(text=welcome_text)


    def setup_ui(self):
        # Erstellen des Top-Frames für Begrüßung und Aktionen-Button
        self.home_area_ui.top_frame = tk.Frame(self.home_frame, bg='#343a40')
        self.home_area_ui.top_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.home_area_ui.welcome_label = tk.Label(self.home_area_ui.top_frame, text="Hallo",
                                      font=("Harry P", 30),
                                      relief=tk.RAISED)
        self.home_area_ui.welcome_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

        # Aktionen-Menübutton
        self.home_area_ui.actions_button = tk.Menubutton(self.home_area_ui.top_frame, text="Aktionen",
                                                         font=("Harry P", 30), relief=tk.RAISED, width=20)
        self.actions_menu = tk.Menu(self.home_area_ui.actions_button, tearoff=0)
        self.home_area_ui.actions_button["menu"] = self.actions_menu
        self.home_area_ui.actions_button.grid(row=0, column=1, sticky='w', padx=10, pady=10)

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

        # Initialisierung von self.button_frame mit erweitertem Padding für mehr Zentrierung
        self.home_area_ui.button_frame = tk.Frame(self.home_frame, bg='#343a40')
        self.home_area_ui.button_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Anpassen des Grid-Layouts im home_frame für Zentrierung
        self.home_frame.grid_rowconfigure(0, weight=1)  # Leerer Puffer oben
        self.home_frame.grid_rowconfigure(1, weight=2)  # Hauptinhalt
        self.home_frame.grid_rowconfigure(2, weight=1)  # Leerer Puffer unten
        self.home_frame.grid_columnconfigure(0, weight=1)  # Leerer Puffer links
        self.home_frame.grid_columnconfigure(1, weight=2)  # Hauptinhalt
        self.home_frame.grid_columnconfigure(2, weight=1)  # Leerer Puffer rechts



        # Hausauswahl-Buttons erstellen und im button_frame positionieren mit grid()
        self.create_house_button(0, r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\gryffindor.png",
                                 'Gryffindor', size=(400, 500))
        self.create_house_button(1, r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\slytherin.png",
                                 'Slytherin', size=(400, 500))
        self.create_house_button(2, r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\hufflepuff.png",
                                 'Hufflepuff', size=(400, 500))
        self.create_house_button(3, r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\ravenclaw.png",
                                 'Ravenclaw', size=(400, 500))

    # Funktion zum Erstellen und Platzieren der Buttons
    def create_house_button(self, column, image_path, house_name, size=(100, 125)):  # Size Parameter hinzugefügt
        image = self.load_and_resize_image(image_path, size)  # Verwenden des neuen Size Parameters
        button = tk.Button(self.home_area_ui.button_frame, image=image,
                           command=lambda: self.on_house_select(house_name, self.app_state.current_username))
        button.grid(row=0, column=column, sticky='nsew', padx=10, pady=10)
        button.image = image  # Referenz auf das Bild behalten, um GC zu verhindern

    # Methode zum Laden und Skalieren der Bilder (sofern noch nicht vorhanden)
    def load_and_resize_image(self, image_path, size=(100, 125)):
        original_image = Image.open(image_path)
        resized_image = original_image.resize(size, Image.Resampling.LANCZOS)  # Aktualisiert von Image.ANTIALIAS
        return ImageTk.PhotoImage(resized_image)

    def show_dropdown(self):
        # Erstellt ein neues Fenster für das Dropdown-Menü
        self.dropdown_window = tk.Toplevel(self.master)
        self.dropdown_window.title("User auswählen")
        # Zentriert das Dropdown-Fenster auf dem Bildschirm
        WindowManager.center_window(self.dropdown_window, 300, 200)

        # Fügt eine Suchleiste hinzu, um Benutzern zu ermöglichen, nach Namen zu suchen
        self.ui_manager.search_var = tk.StringVar()
        search_entry = tk.Entry(self.dropdown_window, textvariable=self.ui_manager.search_var)
        search_entry.pack(fill='x')  # Fügt die Suchleiste zum Fenster hinzu
        search_entry.bind('<KeyRelease>', self.ui_manager.update_dropdown)

        # Initialisiert einen Frame, der die Listbox und Scrollbar enthält
        listbox_frame = tk.Frame(self.dropdown_window)
        listbox_frame.pack(fill='both', expand=True)

        # Fügt eine Scrollbar hinzu, um durch die Listbox scrollen zu können
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')

        # Initialisiert die Listbox, die die Namen anzeigt
        self.home_area_ui.dropdown_list = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=10)
        self.home_area_ui.dropdown_list.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.home_area_ui.dropdown_list.yview)  # Verbindet die Scrollbar mit der Listbox

        self.ui_manager.update_dropdown()

        # Bindet verschiedene Event-Handler für die Listbox, um auf Benutzeraktionen zu reagieren
        self.home_area_ui.dropdown_list.bind('<Double-1>', self.ui_manager.on_double_click)  # Doppelklick
        self.home_area_ui.dropdown_list.bind('<Button-3>', self.ui_manager.on_right_click)  # Rechtsklick
        self.home_area_ui.dropdown_list.bind('<Return>', self.ui_manager.on_enter_pressed)  # Enter-Taste

    def on_house_select(self, house_name, username):
        if not self.app_state.current_username:
            messagebox.showinfo("Fehler", "Bitte erst einen Benutzer auswählen.")
            return
        if not house_name:
            messagebox.showinfo("Fehler", "Bitte erst ein Haus auswählen.")
            return

        self.app_state.house = house_name
        self.app_state.current_username = username
        print(f"{house_name} ausgewählt, Username: {username}")

        # Entferne das ausgewählte Haus aus den Bots, falls vorhanden
        if house_name in self.bot_config.bots:
            del self.bot_config.bots[house_name]

        # Direkter Übergang zum Quiz ohne explizite Manipulation von bot_scores_frame
        self.switch_to_quiz_callback()
        # switch_frame und start_quiz müssen entsprechend angepasst werden
        """
               switch_frame(quiz_frame)
               update_active_button(quiz_button)
               start_quiz(house_name, username)
       """




# Quiz-Logik

class QuizGame:
    def __init__(self, master, house_name, username):
        self.master = master
        self.house = house_name
        self.username = username
        self.current_options = []
        #self.bot_scores_frame = None

        # Instanz von QuizConfig aus variables.py
        self.quiz_config = QuizConfig()

        # Instanz von BotConfig aus variables.py
        self.bot_config = BotConfig()

        # Instanz von AppState aus variables.py
        self.app_state = AppState()

        self.setup_quiz_area()

    def setup_quiz_area(self):



        # Bereinige vorherige Inhalte des Quiz-Frames
        for widget in self.master.winfo_children():
            widget.destroy()

        # Entferne das ausgewählte Haus aus den Bots (falls erforderlich)
        if self.house in self.bot_config.bots:
            del self.bot_config.bots[self.house]


        # Lade die erste Frage
        self.load_next_question()

        score_label = tk.Label(self.master, text=f"{self.app_state.house} ({self.app_state.current_username}): 0", bg="lightgrey",
                               font=("Harry P", 25))
        score_label.pack(side='top', fill='x', pady=10)

    def display_bot_scores(self):
        # Erstelle und konfiguriere bot_scores_frame
        self.bot_scores_frame = tk.Frame(self.master, bg="lightgrey")
        self.bot_scores_frame.pack(side='top', fill='x', pady=10)

        header_label = tk.Label(self.bot_scores_frame, text="Houses Scores", bg="lightgrey", font=("Harry P", 30))
        header_label.pack()

        for house, bot in self.bot_config.bots.items():
            bot_score_label = tk.Label(self.bot_scores_frame, text=f"{house}: {bot.score}", bg="lightgrey",
                                       font=("Harry P", 25))
            bot_score_label.pack(side='left', padx=180)


    

    def load_next_question(self):
        if self.quiz_config.question_count < self.quiz_config.NUM_QUESTIONS:
            question, options, correct_answer = choose_quiz()
            self.display_question(question, options, correct_answer)
        else:
            self.end_quiz()

    def display_question(self, question, options, correct_answer):
        question_label = tk.Label(self.master, text=question, bg='lightgrey', font=("Times New Roman", 20, "bold"))
        question_label.place(relx=0.5, rely=0.3, anchor='center')

        button_width = 80  # Erhöhte Breite für größere Buttons
        button_height = 5  # Erhöhte Höhe für größere Buttons
        font_size = 16  # Größere Schriftgröße für die Button-Texte

        options_frame = tk.Frame(self.master)
        options_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Anpassung der Frames für jede Zeile
        row_frames = [tk.Frame(options_frame) for _ in range(2)]
        for frame in row_frames:
            frame.pack(pady=(5, 5), fill='x', expand=True)

        for i, option in enumerate(options):
            parent_frame = row_frames[0] if i < 2 else row_frames[1]
            # Anpassen der Größe und Schriftgröße der Buttons
            button = tk.Button(parent_frame, text=option, bg='white', font=("Times New Roman", font_size, "bold"),
                               width=button_width,
                               height=button_height)
            button.pack(side='left', padx=10, pady=5)
            button.bind('<Button-1>',
                        lambda event, b=button, o=option: self.check_answer(b, o, correct_answer, self.current_options,
                                                                            self.username))
        # Initialisierung result_label
        self.quiz_config.result_label = tk.Label(self.master, text="", bg='#343a40', font=("Arial", 14))
        self.quiz_config.result_label.place(relx=0.5, rely=0.8, anchor='center')

    def check_answer(self, button, user_answer, correct_answer, options, username):

        if user_answer == correct_answer:
            button.configure(bg='green')
            self.quiz_config.result_label.config(text="Richtige Antwort!", fg='green', font=("Harry P", 30))
            self.quiz_config.score += self.quiz_config.POINTS_PER_ANSWER  # Erhöht die Punktzahl
        else:
            button.configure(bg='red')
            self.quiz_config.result_label.config(text="Falsche Antwort!", fg='red', font=("Harry P", 30))

        self.update_bots_and_scores(options, correct_answer)  # Aktualisieren Sie die Bots und deren Scores

        self.quiz_config.question_count += 1  # Erhöht die Anzahl der gestellten Fragen
        if self.quiz_config.question_count < self.quiz_config.NUM_QUESTIONS:
            self.quiz_config.quiz_frame.after(300, lambda: self.start_quiz(house_name=self.app_state.house,
                                                          username=username))  # Weitergabe des Benutzernamens
        else:
            self.end_quiz(username)  # Weitergabe des Benutzernamens

        # Prüfe, ob alle Fragen beantwortet wurden oder ob wir uns in einem Tiebreaker befinden
        if self.quiz_config.question_count < QuizConfig.NUM_QUESTIONS or QuizConfig.in_tiebreaker_round:
            # Lade die nächste Frage
            self.quiz_config.quiz_frame.after(300, lambda: self.start_quiz(house_name=self.app_state.house, username=username))
        else:
            # Überprüfe auf Unentschieden nur am Ende des normalen Spiels
            if not self.quiz_config.in_tiebreaker_round:
                max_bot_score = max(bot.score for bot in bots.values())
                if self.quiz_config.score == max_bot_score:
                    # Unentschieden detektiert, starte zusätzliche Runden
                    in_tiebreaker_round = True
                    question_count = 0  # Setze die Fragezahl zurück für die zusätzlichen Runden
                    self.quiz_config.quiz_frame.after(300, lambda: self.start_quiz(house_name=self.app_state.house, username=username))
                else:
                    # Kein Unentschieden, Spiel endet
                    self.end_quiz(username)

    def update_bots_and_scores(self, options, correct_answer):

        # Aktualisieren Sie die Antworten und die Scores der Bots
        for bot_house, bot in bots.items():
            bot_choice = bot.choose_answer(options)
            bot.update_score(bot_choice == correct_answer)

            # Aktualisieren der Bots
            self.bot_config.bot_score_labels[bot_house].config(text=f"{bot_house}: {bot.score}")

    def end_quiz(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        end_message = f"Quiz beendet. Deine Punktzahl: {self.score}."
        messagebox.showinfo("Quiz Ende", end_message)
        end_label = tk.Label(self.master, text=end_message, font=("Arial", 16), bg="#f5deb3")
        end_label.pack(pady=20)

        # Zurück-Button könnte hier implementiert werden, um zum Hauptmenü zurückzukehren

    def save_result(self):
        # Erfasse das aktuelle Datum und die Uhrzeit
        current_time = datetime.datetime.now()

        session = get_db_session()
        user = session.query(User).filter_by(username=self.username).first()

        if not user:
            user = User(username=self.username)
            session.add(user)
            session.commit()

        # Neuen Leaderboard-Eintrag erstellen
        new_entry = Leaderboard(user_id=user.id, house=self.house, score=self.score, played_on=current_time)
        session.add(new_entry)
        session.commit()

        messagebox.showinfo('Erfolg', 'Dein Ergebnis wurde gespeichert.')





