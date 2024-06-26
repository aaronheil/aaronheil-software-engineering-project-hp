import tkinter as tk
from tkinter import messagebox
from variables import AppState
from home_area import HomeAreaFrontend
from statistics_area import LeaderboardView
from quiz_area import QuizApp
from success_area import SuccessArea


class SelectionScreen:
    def __init__(self, master):
        self.master = master
        self.app_state = AppState()
        self.is_quiz_active = False  # Beispielstatus für das Quiz
        self.house = None  # Beispiel für eine Hausvariable
        self.active_button = None  # Speichert den aktuell aktiven Button

        self.nav_frame = tk.Frame(self.master, bg='#343a40')
        self.nav_frame.pack(side='top', fill='x')
        self.setup_nav_buttons()

        self.frame_container = tk.Frame(self.master)
        self.frame_container.pack(fill='both', expand=True)
        self.frame_container.grid_columnconfigure(0, weight=1)
        self.frame_container.grid_rowconfigure(0, weight=1)

        self.home_frame = tk.Frame(self.frame_container, bg='#343a40')
        self.quiz_frame = tk.Frame(self.frame_container, bg='#343a40')
        self.erfolge_frame = tk.Frame(self.frame_container, bg='#343a40')
        self.statistik_frame = tk.Frame(self.frame_container, bg='#343a40')
        self.frames = {
            "home": self.home_frame,
            "quiz": self.quiz_frame,
            "erfolge": self.erfolge_frame,
            "statistik": self.statistik_frame
        }

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky='nsew')

        self.home_area = HomeAreaFrontend(self.master, self.home_frame, self.switch_to_quiz,
                                          self.get_switch_frame_callback(), self, self.app_state)

        self.switch_to_home()
        self.success_area = SuccessArea(self.erfolge_frame, self.app_state.current_username)


    def setup_nav_buttons(self):
        self.home_button = tk.Button(self.nav_frame, text='⌂ Home', font=("Harry P", 40),
                                     command=self.switch_to_home)
        self.home_button.pack(side='left', fill='x', expand=True)

        self.quiz_button = tk.Button(self.nav_frame, text='🎮 Quiz', font=("Harry P", 40),
                                     command=self.switch_to_quiz)
        self.quiz_button.pack(side='left', fill='x', expand=True)

        self.erfolge_button = tk.Button(self.nav_frame, text='\U0001F3C6 Erfolge', font=("Harry P", 40),
                                        command=self.switch_to_erfolge)
        self.erfolge_button.pack(side='left', fill='x', expand=True)

        self.statistik_button = tk.Button(self.nav_frame, text='\U0001F4C8 Statistik', font=("Harry P", 40),
                                          command=self.switch_to_statistik)
        self.statistik_button.pack(side='left', fill='x', expand=True)

        self.update_active_button(self.home_button)

    def switch_frame(self, frame_key):
        frame = self.frames.get(frame_key)
        if frame:
            frame.tkraise()
            self.update_active_button(getattr(self, f"{frame_key}_button", None))

    def get_switch_frame_callback(self):
        # Für Frame-Wechsel
        return self.switch_frame

    def switch_to_home(self):
        self.switch_frame("home")

    def switch_to_quiz_callback(self):
        self.switch_to_quiz()

    def switch_to_quiz(self):
        house_name = self.app_state.house
        username = self.app_state.current_username

        # Prüfe, ob ein Haus ausgewählt wurde
        if not house_name:
            messagebox.showinfo("Fehler", "Bitte erst ein Haus auswählen.")
            self.switch_frame("home")
            return  # Beendet die Funktion, um zu verhindern, dass das Quiz gestartet wird

        self.app_state.is_quiz_active = False
        self.switch_frame("quiz")

        # Initialisierung von QuizApp nur, wenn sie noch nicht existiert oder neu initialisiert werden soll
        if not hasattr(self, 'quiz_app'):
            self.quiz_app = QuizApp(self.quiz_frame, house_name, username, self.app_state, _selection_screen=self,
                                    success_area=self.success_area)

    def restart_quiz_from_button(self):
        # Überprüfen, ob `self.quiz_app` existiert und eine Instanz von QuizApp ist
        if self.quiz_app is None or not isinstance(self.quiz_app, QuizApp):
            # Reinitialisiere die QuizApp Instanz
            house_name = self.house
            username = self.app_state.current_username
            self.quiz_app = QuizApp(self.quiz_frame, house_name, username, self.app_state, _selection_screen=self,
                                    success_area=self.success_area)

        # Sicherstellen, dass self.quiz_app nicht None ist und dann restart_quiz aufrufen
        if self.quiz_app:
            self.quiz_app.restart_quiz()
        else:
            print("Fehler: QuizApp Instanz konnte nicht initialisiert werden.")

    def update_success_area_for_new_user(self, new_username):
        # Aktualisiere den aktuellen Benutzernamen im AppState
        self.app_state.current_username = new_username
        # Rufe die Aktualisierungsmethode in SuccessArea auf, falls diese existiert
        if hasattr(self, 'success_area'):
            self.success_area.refresh_for_new_user(new_username)


    def switch_to_erfolge(self):
        self.switch_frame("erfolge")

    def switch_to_statistik(self):
        self.switch_frame("statistik")
        # Erstellt und zeigt das Leaderboard im 'statistik_frame'
        LeaderboardView(self.statistik_frame)

    def update_active_button(self, new_active_button):
        if self.active_button:
            self.active_button.config(bg='SystemButtonFace')
        if new_active_button:
            new_active_button.config(bg='lightgrey')
            self.active_button = new_active_button


def main():
    root = tk.Tk()
    root.title("Auswahlfenster")
    root.attributes("-fullscreen", True)
    app = SelectionScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()








