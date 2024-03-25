import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main import choose_quiz
from main import get_db_session, Leaderboard, User
from bots_logic import HogwartsBot
from bots_logic import bots, update_bot_scores
import datetime
from PIL import Image, ImageTk
import pygame
import home_area
from variables import AppState
from home_area import HomeAreaFrontend
from statistics_area import LeaderboardView
from quiz_area import QuizApp


class SelectionScreen:
    def __init__(self, master):
        self.master = master
        self.app_state = AppState()
        #self.app_state.current_username = "NeuerBenutzername"  # Beispiel für eine Benutzervariable
        self.is_quiz_active = False  # Beispielstatus für das Quiz
        self.house = None  # Beispiel für eine Hausvariable
        self.active_button = None  # Speichert den aktuell aktiven Button

        # Hinweis: tk ordnet die widgets immer in der Reihenfolge an, nach welcher sie erstellt wurden.

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

        self.home_area = HomeAreaFrontend(self.master, self.home_frame, self.switch_to_quiz)

        self.switch_to_home()

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

        self.update_active_button(self.home_button)  # Setzen Sie den anfänglichen aktiven Button

    def switch_frame(self, frame_key):
        frame = self.frames.get(frame_key)
        if frame:
            frame.tkraise()
            self.update_active_button(getattr(self, f"{frame_key}_button", None))

    def switch_to_home(self):
        self.switch_frame("home")
        #HomeAreaFrontend(self.home_frame)


    def switch_to_quiz_callback(self):
        self.switch_to_quiz()

    def switch_to_quiz(self):
        if self.app_state.is_quiz_active:
            messagebox.showinfo("Info", "Das Quiz läuft bereits.")
            return
        self.app_state.is_quiz_active = True
        self.switch_frame("quiz")
        # Initialisiere die QuizApp nur, wenn sie noch nicht existiert oder neu initialisiert werden soll
        if not hasattr(self, 'quiz_app'):
            self.quiz_app = QuizApp(self.quiz_frame)

    def switch_to_erfolge(self):
        self.switch_frame("erfolge")

    def switch_to_statistik(self):
        self.switch_frame("statistik")
        # Erstellt und zeigt das Leaderboard im 'statistik_frame'
        LeaderboardView(self.statistik_frame)

    def update_active_button(self, new_active_button):
        if self.active_button:
            self.active_button.config(bg='SystemButtonFace')  # Setzen Sie die Standardfarbe zurück
        if new_active_button:
            new_active_button.config(bg='lightgrey')  # Hervorheben des aktiven Buttons
            self.active_button = new_active_button


def main():
    root = tk.Tk()
    root.title("Auswahlfenster")
    root.attributes("-fullscreen", True)
    app = SelectionScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()





"""
def setup_quiz():
    global quiz_frame, quiz_widget_frame, is_quiz_active, score, question_count

    # Markiere das Quiz als nicht aktiv
    is_quiz_active = False

    # Setze den Score und den Fragezähler zurück
    score = 0
    question_count = 0

    # Entferne alle Widgets im quiz_frame
    for widget in quiz_frame.winfo_children():
        widget.destroy()

    # Erstelle den quiz_widget_frame neu
    quiz_widget_frame = tk.Frame(quiz_frame, bg='#343a40')
    quiz_widget_frame.pack(fill='both', expand=True)

    # Hier kannst du weitere Widgets oder Anweisungen für das Quiz hinzufügen
    print("Quiz-Setup ist bereit.")

"""









