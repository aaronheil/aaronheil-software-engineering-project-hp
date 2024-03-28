import tkinter as tk
from tkinter import messagebox
import datetime
from main import choose_quiz, get_db_session, Leaderboard, User
from variables import QuizConfig, AppState, User, BotConfig
from bots_logic import bots, update_bot_scores


class QuizApp:
    def __init__(self, master, house_name, username, app_state):
        self.master = master
        self.house = house_name
        self.username = username
        self.current_options = []

        # Instanz von QuizConfig aus variables.py
        self.quiz_config = QuizConfig()

        # Instanz von BotConfig aus variables.py
        self.bot_config = BotConfig()

        # Instanz von AppState aus variables.py
        self.app_state = app_state
        self.question_label = None

        self.setup_quiz_area()

        print(f"QuizApp initialisiert mit Haus: {self.house}, Benutzername: {self.username}")

    def setup_quiz_area(self):

        # Bereinige vorherige Inhalte des Quiz-Frames
        for widget in self.master.winfo_children():
            widget.destroy()

        # Entferne das ausgewählte Haus aus den Bots
        if self.house in self.bot_config.bots:
            del self.bot_config.bots[self.house]  # Entfernt das ausgewählte Haus aus den Bots

        self.question_label = tk.Label(self.master, text="", bg='lightgrey', font=("Times New Roman", 20, "bold"))
        self.question_label.place(relx=0.5, rely=0.3, anchor='center')

        # Aktualisiere die Anzeige der Bot-Scores ohne das ausgewählte Haus
        self.display_bot_scores()

        # Lade die erste Frage
        self.load_next_question()

        self.quiz_config.user_score_label = tk.Label(self.master,
                                                     text=f"{self.house} ({self.app_state.current_username}): {self.quiz_config.score} ",
                                                     bg="lightgrey",
                                                     font=("Harry P", 25))
        self.quiz_config.user_score_label.pack(side='top', fill='x', pady=10)



    def display_bot_scores(self):
        # Überprüfe, ob bot_scores_frame bereits existiert, bevor es zerstört wird
        if hasattr(self.quiz_config, 'bot_scores_frame') and self.quiz_config.bot_scores_frame is not None:
            self.quiz_config.bot_scores_frame.destroy()

        # Instanziere bot_scores_frame neu
        self.quiz_config.bot_scores_frame = tk.Frame(self.master, bg="lightgrey")
        self.quiz_config.bot_scores_frame.pack(side='top', fill='x', pady=10)

        header_label = tk.Label(self.quiz_config.bot_scores_frame, text="House Scores", bg="lightgrey",
                                font=("Harry P", 30))
        header_label.pack()

        # Erstelle einen Container für die Bot-Score-Labels
        bot_scores_container = tk.Frame(self.quiz_config.bot_scores_frame, bg="lightgrey")
        bot_scores_container.pack(pady=10)  # Packe den Container in der Mitte

        self.bot_config.bot_score_labels = {}

        # Anzeigen der Scores für die verbleibenden Bots im Container
        for house, bot in self.bot_config.bots.items():
            self.bot_config.bot_score_labels[house] = tk.Label(bot_scores_container,
                                                               text=f"{house}: {bot.score}", bg="lightgrey",
                                                               font=("Harry P", 25))
            self.bot_config.bot_score_labels[house].pack(side='left', padx=10)


    def load_next_question(self):
        if self.quiz_config.question_count < self.quiz_config.NUM_QUESTIONS:
            question, options, correct_answer = choose_quiz()
            self.display_question(question, options, correct_answer)
        else:
            self.end_quiz()

    def display_question(self, question, options, correct_answer):
        self.current_options = options
        self.question_label.config(text=question)

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
            self.quiz_config.user_score_label.config(text=f"{self.house} ({self.app_state.current_username}): {self.quiz_config.score}")


        else:
            button.configure(bg='red')
            self.quiz_config.result_label.config(text="Falsche Antwort!", fg='red', font=("Harry P", 30))

        self.update_bots_and_scores(options, correct_answer)  # Aktualisieren Sie die Bots und deren Scores

        self.quiz_config.question_count += 1  # Erhöht die Anzahl der gestellten Fragen
        if self.quiz_config.question_count < self.quiz_config.NUM_QUESTIONS:
            # Verzögere das Laden der nächsten Frage
            self.master.after(300, self.load_next_question)  # Entfernt die unerwarteten Argumente
        else:
            self.end_quiz()

    def update_bots_and_scores(self, options, correct_answer):
        for bot_house, bot in self.bot_config.bots.items():
            if bot_house in self.bot_config.bot_score_labels:
                bot_choice = bot.choose_answer(options)
                bot.update_score(bot_choice == correct_answer)
                self.bot_config.bot_score_labels[bot_house].config(text=f"{bot_house}: {bot.score}")

    def end_quiz(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        end_message = f"Quiz beendet. Deine Punktzahl: {self.quiz_config.score}."
        messagebox.showinfo("Quiz Ende", end_message)
        end_label = tk.Label(self.master, text=end_message, font=("Arial", 16), bg="#f5deb3")
        end_label.pack(pady=20)

        # Aufruf von save_result(), um das Ergebnis zu speichern
        self.save_result()

    def save_result(self):
        # Erfasse das aktuelle Datum und die Uhrzeit
        current_time = datetime.datetime.now()


        session = get_db_session()
        user = session.query(User).filter_by(username=self.app_state.current_username).first()

        if not user:
            # Erstellt einen neuen User, wenn dieser noch nicht existiert, basierend auf dem aktuellen Benutzernamen aus app_state
            user = User(username=self.app_state.current_username)
            session.add(user)
            session.commit()

        # Neuen Leaderboard-Eintrag erstellen
        new_entry = Leaderboard(user_id=user.id, house=self.house, score=self.quiz_config.score, played_on=current_time)
        session.add(new_entry)
        session.commit()
        print(f"User ID: {user.id}, erreichte Punktzahl: {self.quiz_config.score}")



"""

# Prüfe, ob alle Fragen beantwortet wurden oder ob wir uns in einem Tiebreaker befinden
        if self.quiz_config.question_count < QuizConfig.NUM_QUESTIONS or QuizConfig.in_tiebreaker_round:
            # Lade die nächste Frage
            self.quiz_config.quiz_frame.after(300, lambda: self.load_next_question)
        else:
            # Überprüfe auf Unentschieden nur am Ende des normalen Spiels
            if not self.quiz_config.in_tiebreaker_round:
                max_bot_score = max(bot.score for bot in bots.values())
                if self.quiz_config.score == max_bot_score:
                    # Unentschieden detektiert, starte zusätzliche Runden
                    in_tiebreaker_round = True
                    self.quiz_config.question_count = 0  # Setze die Fragezahl zurück für die zusätzlichen Runden
                    self.quiz_config.quiz_frame.after(300, lambda: self.start_quiz(house_name=self.app_state.house, username=username))
                else:
                    # Kein Unentschieden, Spiel endet
                    self.end_quiz(username)
                    
"""
