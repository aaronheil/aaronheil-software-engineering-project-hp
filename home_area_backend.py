import tkinter as tk
from tkinter import simpledialog, messagebox
import selection_screen
import pygame
import variables
from variables import User, Session
import main


class WindowManager:
    @staticmethod
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')


class UsernameManager:
    def __init__(self):
        pass

    @staticmethod
    def is_username_existing(username):
        return variables.session.query(User).filter_by(username=username).first() is not None

    @staticmethod
    def add_username(username):
        if not UsernameManager.is_username_existing(username):
            new_user = User(username=username)
            variables.session.add(new_user)
            variables.session.commit()
            return True
        return False

    @staticmethod
    def get_recent_usernames(limit=10):
        return [user.username for user in variables.session.query(User.username).order_by(User.id.desc()).limit(limit)]

    @staticmethod
    def search_username(search_term):
        return variables.session.query(User.username).filter(User.username.like(f"%{search_term}%")).all()



class UserInterfaceManager:
    def __init__(self, home_window):
        self.home_window = home_window
        self.dropdown_var = tk.StringVar(self.home_window)

    def on_name_submit(self):
        username = self.dropdown_var.get()
        if UsernameManager.add_username(username):
            self.update_ui_with_new_username(username)
        else:
            tk.messagebox.showinfo("Info", "Dieser Name existiert bereits.")

    def update_ui_with_new_username(self, username):
        variables.app_state.current_username = username
        # Hier sollte die UI entsprechend aktualisiert werden, z.B. Welcome Label etc.

    def get_all_usernames(self):
        return variables.session.query(User.username).all()

    def get_or_create_username(self):
        session = Session()
        latest_entry = session.query(main.Leaderboard).order_by(main.Leaderboard.played_on.desc()).first()
        if latest_entry:
            user = session.query(User).filter_by(id=latest_entry.user_id).first()
            if user:
                return user.username
        username = simpledialog.askstring("Benutzername", "Wie lautet Ihr Name?")
        if username and not UsernameManager.is_username_existing(username):
            UsernameManager.add_username(username)
        return username if username else "Unbekannter Benutzer"

    def change_user(label):
        create_new_user_window(home_window)

    def update_dropdown(*args):
        search_term = search_var.get()  # Hole den Text aus der Suchleiste
        filtered_names = search_username(search_term)
        dropdown_list.delete(0, 'end')  # Löscht alle Einträge in der Listbox

        if not filtered_names:
            tk.messagebox.showinfo("Suche", "Kein passender Benutzername gefunden.")
        else:
            for item in filtered_names:
                dropdown_list.insert('end', item[0])

    def on_dropdown_select(event):
        selected_index = dropdown_list.curselection()
        selected_name = dropdown_list.get(selected_index)
        update_ui_with_new_username(selected_name)

    def on_double_click(event):
        selected_index = dropdown_list.curselection()
        selected_name = dropdown_list.get(selected_index)
        update_ui_with_new_username(selected_name)

    def on_right_click(event):
        selected_indices = dropdown_list.curselection()  # Holt die Liste der ausgewählten Indizes
        if selected_indices:  # Prüfen, ob die Liste nicht leer ist
            selected_index = selected_indices[0]  # Nehmen Sie den ersten ausgewählten Index
            selected_name = dropdown_list.get(selected_index)  # Holt den Namen aus der Listbox
            if tk.messagebox.askyesno("Löschen", f"Möchten Sie '{selected_name}' löschen?"):
                user_to_delete = session.query(User).filter_by(username=selected_name).first()
                if user_to_delete:
                    session.delete(user_to_delete)
                    session.commit()
                    update_dropdown()  # Aktualisiert die Listbox nach dem Löschen eines Benutzers
        else:
            tk.messagebox.showwarning("Warnung", "Kein Benutzer ausgewählt.")

    def on_enter_pressed(event):
        selected_indices = dropdown_list.curselection()
        if selected_indices:  # Prüfen, ob die Liste nicht leer ist
            selected_index = selected_indices[0]  # Nehmen Sie den ersten ausgewählten Index
            selected_name = dropdown_list.get(selected_index)
            update_ui_with_new_username(selected_name)
        else:
            tk.messagebox.showwarning("Warnung", "Kein Benutzer ausgewählt.")

    def toggle_fullscreen(event=None):
        home_window.attributes("-fullscreen", False)  # Schaltet den Vollbildmodus aus
        home_window.destroy()  # Schließt das Fenster

    def create_new_user_window(parent):
        new_user_window = tk.Toplevel(parent)
        new_user_window.title("Neuen Benutzer anlegen")
        center_window(new_user_window, 400, 200)

        tk.Label(new_user_window, text="Bitte geben Sie den neuen Benutzernamen ein:").pack(pady=20)

        username_entry = tk.Entry(new_user_window)
        username_entry.pack()

        def submit_new_username():
            username = username_entry.get()
            if username:
                if add_username(username):  # Füge den neuen Benutzer hinzu, wenn der Name nicht leer ist
                    new_user_window.destroy()
                    update_ui_with_new_username(username)
                else:
                    tk.messagebox.showwarning("Warnung", "Benutzername existiert bereits!")
            else:
                tk.messagebox.showwarning("Warnung", "Benutzername darf nicht leer sein!")

        submit_button = tk.Button(new_user_window, text="Submit", command=submit_new_username)
        submit_button.pack(pady=20)



class MusicManager:
    """Verwaltet Musik-bezogene Aktionen."""

    @staticmethod
    def toggle_music():
        """Schaltet die Musik ein oder aus."""
        if variables.is_music_playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        variables.is_music_playing = not variables.is_music_playing