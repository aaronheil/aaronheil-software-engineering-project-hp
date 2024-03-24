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
        self.current_options = []

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

        # Initialisierung result_label
        self.quiz_config.result_label = tk.Label(self.master, text="", bg='#343a40', font=("Arial", 14))
        self.quiz_config.result_label.pack(pady=(10, 20))

    def display_bot_scores(self):
        self.quiz_config.bot_scores_frame = tk.Frame(self.master, bg="lightgrey")
        self.quiz_config.bot_scores_frame.pack(side='top', fill='x', pady=10)
        header_label = tk.Label(self.quiz_config.bot_scores_frame, text="Häuser-Scores", bg="lightgrey",
                                font=("Harry P", 20))
        header_label.pack()

        for name, bot in bots.items():
            self.bot_config.bot_score_labels[name] = tk.Label(self.quiz_config.bot_scores_frame,
                                                              text=f"{name}: {bot.score}", bg="lightgrey",
                                                              font=("Arial", 19))

            self.bot_config.bot_score_labels[name].pack(side='left', padx=10)

    def load_next_question(self):
        if self.quiz_config.question_count < self.quiz_config.NUM_QUESTIONS:
            question, options, correct_answer = choose_quiz()
            self.display_question(question, options, correct_answer)
        else:
            self.end_quiz()

    def display_question(self, question, options, correct_answer):
        question_label = tk.Label(self.master, text=question, bg='white', font=("Arial", 14, "bold"))
        question_label.pack(pady=(20, 10))

        button_width = 80  # Erhöhte Breite für größere Buttons
        button_height = 3  # Erhöhte Höhe für größere Buttons
        font_size = 25  # Größere Schriftgröße für die Button-Texte

        options_frame = tk.Frame(self.master)
        options_frame.pack(pady=(10, 20))

        # Anpassung der Frames für jede Zeile
        row_frames = [tk.Frame(options_frame) for _ in range(2)]
        for frame in row_frames:
            frame.pack(pady=(5, 5), fill='x', expand=True)

        for i, option in enumerate(options):
            parent_frame = row_frames[0] if i < 2 else row_frames[1]
            # Anpassen der Größe und Schriftgröße der Buttons
            button = tk.Button(parent_frame, text=option, bg='white', font=("Times New Roman", font_size), width=button_width,
                               height=button_height)
            button.pack(side='left', padx=10, pady=5)
            button.bind('<Button-1>',
                        lambda event, b=button, o=option: self.check_answer(b, o, correct_answer, self.current_options,
                                                                            self.username))

    def check_answer(self, button, user_answer, correct_answer, options, username):

        if user_answer == correct_answer:
            button.configure(bg='green')
            self.quiz_config.result_label.config(text="Richtige Antwort!", fg='green')
            self.quiz_config.score += self.quiz_config.POINTS_PER_ANSWER  # Erhöht die Punktzahl
        else:
            button.configure(bg='red')
            self.quiz_config.result_label.config(text="Falsche Antwort.", fg='red')

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
