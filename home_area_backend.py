import tkinter as tk
from tkinter import simpledialog, messagebox
import selection_screen
import pygame
import variables
from variables import User, Session, HomeAreaUI, UserInteraction, every_username_session, AppState
import main
from main import Leaderboard, Session


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

    def on_dropdown_select(event):
        selected_index = HomeAreaUI.dropdown_list.curselection()
        selected_name = HomeAreaUI.dropdown_list.get(selected_index)
        event.update_ui_with_new_username(selected_name)

    def on_double_click(self, event):
        selected_indices = self.dropdown_list.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            selected_name = self.dropdown_list.get(selected_index)
            self.update_ui_with_new_username(selected_name)

    def on_right_click(self, dropdown_list, event):
        selected_indices = dropdown_list.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            selected_name = dropdown_list.get(selected_index)
            if tk.messagebox.askyesno("Löschen", f"Möchten Sie '{selected_name}' löschen?"):
                user_to_delete = self.session.query(User).filter_by(username=selected_name).first()
                if user_to_delete:
                    self.session.delete(user_to_delete)
                    self.session.commit()
                    self.update_dropdown(
                        dropdown_list)  # Angenommen, diese Methode existiert und aktualisiert die Listbox
        else:
            tk.messagebox.showwarning("Warnung", "Kein Benutzer ausgewählt.")

    def on_enter_pressed(self, dropdown_list, event):
        selected_indices = dropdown_list.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            selected_name = dropdown_list.get(selected_index)
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
