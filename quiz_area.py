import tkinter as tk
from tkinter import messagebox
import datetime
from main import choose_quiz, get_db_session, Leaderboard, User
from variables import QuizConfig, AppState, User, BotConfig
from bots import bots, update_bot_scores


class QuizApp:
    def __init__(self, master, house_name=None, username=None):
        self.master = master
        self.house = house_name
        self.username = username

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

    def check_answer(self, user_answer, correct_answer, options, username):

        if user_answer == correct_answer:
            #self.configure(bg='green')
            self.quiz_config.result_label.config(text="Richtige Antwort!", fg='green')
            self.quiz_config.score += QuizConfig.POINTS_PER_ANSWER  # Erhöht die Punktzahl
        else:
            #self.configure(bg='red')
            self.quiz_config.result_label.config(text="Falsche Antwort.", fg='red')

        self.update_bots_and_scores(options, correct_answer)  # Aktualisieren Sie die Bots und deren Scores

        QuizConfig.question_count += 1  # Erhöht die Anzahl der gestellten Fragen
        if QuizConfig.question_count < QuizConfig.NUM_QUESTIONS:
            quiz_frame.after(300, lambda: self.start_quiz(house_name=house,
                                                          username=username))  # Weitergabe des Benutzernamens
        else:
            self.end_quiz(username)  # Weitergabe des Benutzernamens

        # Prüfe, ob alle Fragen beantwortet wurden oder ob wir uns in einem Tiebreaker befinden
        if QuizConfig.question_count < QuizConfig.NUM_QUESTIONS or QuizConfig.in_tiebreaker_round:
            # Lade die nächste Frage
            quiz_frame.after(300, lambda: self.start_quiz(house_name=house, username=username))
        else:
            # Überprüfe auf Unentschieden nur am Ende des normalen Spiels
            if not QuizConfig.in_tiebreaker_round:
                max_bot_score = max(bot.score for bot in bots.values())
                if score == max_bot_score:
                    # Unentschieden detektiert, starte zusätzliche Runden
                    in_tiebreaker_round = True
                    question_count = 0  # Setze die Fragezahl zurück für die zusätzlichen Runden
                    quiz_frame.after(300, lambda: self.start_quiz(house_name=house, username=username))
                else:
                    # Kein Unentschieden, Spiel endet
                    self.end_quiz(username)

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
