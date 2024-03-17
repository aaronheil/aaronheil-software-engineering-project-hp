import tkinter as tk
from tkinter import messagebox
import datetime
from main import choose_quiz, get_db_session, Leaderboard, User
from variables import QuizConfig
from bots import bots, update_bot_scores


class QuizApp:
    def __init__(self, master, house_name=None, username=None):
        self.master = master
        self.house = house_name
        self.username = username
        self.score = 0
        self.question_count = 0
        self.bot_score_labels = {}

        self.setup_quiz_area()

    def setup_quiz_area(self):
        # Bereinige vorherige Inhalte des Quiz-Frames
        for widget in self.master.winfo_children():
            widget.destroy()

        # Aktualisiere die Anzeige der Bot-Scores und entferne das ausgewählte Haus
        if self.house in bots:
            del bots[self.house]
        self.display_bot_scores()

        # Lade die erste Frage
        self.load_next_question()

    def display_bot_scores(self):
        self.bot_scores_frame = tk.Frame(self.master, bg="#f5deb3")
        self.bot_scores_frame.pack(side='top', fill='x', pady=10)
        header_label = tk.Label(self.bot_scores_frame, text="Häuser-Scores", bg="#f5deb3", font=("Harry P", 20))
        header_label.pack()

        for name, bot in bots.items():
            self.bot_score_labels[name] = tk.Label(self.bot_scores_frame, text=f"{name}: {bot.score}", bg="#f5deb3", font=("Arial", 19))
            self.bot_score_labels[name].pack(side='left', padx=10)

    def load_next_question(self):
        if self.question_count < QuizConfig.NUM_QUESTIONS:
            question, options, correct_answer = choose_quiz()
            self.display_question(question, options, correct_answer)
        else:
            self.end_quiz()

    def display_question(self, question, options, correct_answer):
        question_label = tk.Label(self.master, text=question, bg='white', font=("Arial", 14, "bold"))
        question_label.pack(pady=(20, 10))

        for option in options:
            button = tk.Button(self.master, text=option, bg='white', font=("Arial", 14))
            button.pack(pady=5)
            button.bind('<Button-1>', lambda event, o=option: self.check_answer(o, correct_answer))

    def check_answer(self, user_answer, correct_answer):
        if user_answer == correct_answer:
            self.score += QuizConfig.POINTS_PER_ANSWER
            messagebox.showinfo("Richtig!", "Richtige Antwort!")
        else:
            messagebox.showerror("Falsch!", "Falsche Antwort.")
        self.master.after(1000, self.load_next_question)

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
