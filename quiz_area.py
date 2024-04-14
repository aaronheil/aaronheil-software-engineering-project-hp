import tkinter as tk
from tkinter import messagebox
import datetime
from main import (choose_quiz, get_db_session, save_user_progress, load_user_progress, Leaderboard, User,
                  update_user_progress_on_win)
from variables import QuizConfig, User, BotConfig


class QuizApp:
    def __init__(self, master, house_name, username, app_state, success_area, _selection_screen=None):
        self.master = master
        self.house = house_name
        self.username = username
        self.current_options = []

        # Instanz von QuizConfig aus variables.py
        self.quiz_config = QuizConfig()

        # Instanz von BotConfig aus variables.py
        self.bot_config = BotConfig()
        self.success_area = success_area

        # Instanz von AppState aus variables.py
        self.app_state = app_state
        self.question_label = None
        self.asked_questions_ids = set()  # Hinzufügen einer Instanzvariable zur Speicherung der IDs gestellter Fragen

        self.setup_quiz_area()
        self.selection_screen = _selection_screen

        print(f"QuizApp initialisiert mit Haus: {self.house}, Benutzername: {self.username}")

    def setup_quiz_area(self):

        # Bereinigt vorherige Inhalte des Quiz-Frames
        for widget in self.master.winfo_children():
            widget.destroy()

        # Entferne das ausgewählte Haus aus den Bots
        if self.house in self.bot_config.bots:
            del self.bot_config.bots[self.house]  # Entfernt das ausgewählte Haus aus den Bots

        self.question_label = tk.Label(self.master, text="", bg='lightgrey', font=("Times New Roman", 20, "bold"))
        self.question_label.place(relx=0.5, rely=0.3, anchor='center')

        # Aktualisiert die Anzeige der Bot-Scores ohne das ausgewählte Haus
        self.display_bot_scores()

        # Lade die erste Frage
        self.load_next_question()

        self.quiz_config.user_score_label = tk.Label(self.master,
                                                     text=f"{self.house} ({self.app_state.current_username}): {self.quiz_config.score} ",
                                                     bg="lightgrey",
                                                     font=("Harry P", 25))
        self.quiz_config.user_score_label.pack(side='top', fill='x', pady=10)

    def display_bot_scores(self):
        # Überprüft, ob bot_scores_frame bereits existiert, bevor es zerstört wird
        if hasattr(self.quiz_config, 'bot_scores_frame') and self.quiz_config.bot_scores_frame is not None:
            self.quiz_config.bot_scores_frame.destroy()

        # Instanziert bot_scores_frame neu
        self.quiz_config.bot_scores_frame = tk.Frame(self.master, bg="lightgrey")
        self.quiz_config.bot_scores_frame.pack(side='top', fill='x', pady=10)

        header_label = tk.Label(self.quiz_config.bot_scores_frame, text="House Scores", bg="lightgrey",
                                font=("Harry P", 30))
        header_label.pack()

        # Erstellt einen Container für die Bot-Score-Labels
        bot_scores_container = tk.Frame(self.quiz_config.bot_scores_frame, bg="lightgrey")
        bot_scores_container.pack(pady=10)  # Packt den Container in der Mitte

        self.bot_config.bot_score_labels = {}

        # Anzeigen der Scores für die verbleibenden Bots im Container
        for house, bot in self.bot_config.bots.items():
            self.bot_config.bot_score_labels[house] = tk.Label(bot_scores_container,
                                                               text=f"{house}: {bot.score}", bg="lightgrey",
                                                               font=("Harry P", 25))
            self.bot_config.bot_score_labels[house].pack(side='left', padx=10)

    def load_next_question(self):
        if self.quiz_config.question_count < self.quiz_config.NUM_QUESTIONS:
            question, options, correct_answer, question_id = choose_quiz(self.asked_questions_ids)
            self.asked_questions_ids.add(question_id)
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
            self.quiz_config.score += self.quiz_config.POINTS_PER_ANSWER
            self.quiz_config.user_score_label.config(
                text=f"{self.house} ({self.app_state.current_username}): {self.quiz_config.score}")
        else:
            button.configure(bg='red')
            self.quiz_config.result_label.config(text="Falsche Antwort!", fg='red', font=("Harry P", 30))

        # Verzögert das Entfernen des Textes im result_label um 1 Sekunde (1000 Millisekunden)
        self.master.after(300, lambda: self.quiz_config.result_label.config(text=""))

        self.update_bots_and_scores(options, correct_answer)

        self.quiz_config.question_count += 1
        if self.quiz_config.question_count < self.quiz_config.NUM_QUESTIONS:
            # Verzögere das Laden der nächsten Frage
            self.master.after(300, self.load_next_question)
        else:
            self.end_quiz()

    def update_bots_and_scores(self, options, correct_answer):
        for bot_house, bot in self.bot_config.bots.items():
            if bot_house in self.bot_config.bot_score_labels:
                bot_choice = bot.choose_answer(options)
                bot.update_score(bot_choice == correct_answer)
                self.bot_config.bot_score_labels[bot_house].config(text=f"{bot_house}: {bot.score}")

    def restart_quiz(self):
        # Reset der internen Zustände
        self.quiz_config.score = 0
        self.quiz_config.question_count = 0
        self.quiz_config.in_tiebreaker_round = False
        self.asked_questions_ids = set()  # Reset der bereits gestellten Fragen IDs

        # Reset der Bots' Scores
        for bot in self.bot_config.bots.values():
            bot.reset_bot_scores()

        # UI zurücksetzen
        self.setup_quiz_area()

        # Erneutes Laden der ersten Frage
        self.load_next_question()

    def end_quiz(self):
        def show_restart_button():
            # Entfernt alle Widgets aus dem Quiz-Bereich
            for widget in self.master.winfo_children():
                widget.destroy()

            # Zeigt den Button zum Neustarten des Quiz
            restart_button = tk.Button(self.master, text='\U0001F501 Neue Quiz-Session starten.',
                                       font=("Harry P", 35, "bold"), bg="lightgrey",
                                       command=self.restart_quiz)
            restart_button.config(command=lambda: self.selection_screen.restart_quiz_from_button())
            restart_button.place(relx=0.5, rely=0.5, anchor='center')

        def handle_game_end(message):
            # Zeigt die Spielende-Nachricht
            messagebox.showinfo("Spielende", message)
            # Fügt den Neustart-Button hinzu nachdem die Nachrichtenbox geschlossen wurde
            show_restart_button()

        max_bot_score = max(bot.score for bot in self.bot_config.bots.values())
        player_score = self.quiz_config.score

        if self.quiz_config.in_tiebreaker_round:
            if player_score > max_bot_score:
                self.quiz_config.in_tiebreaker_round = False
                self.user_won_quiz()
                handle_game_end(f"Herzlichen Glückwunsch {self.app_state.current_username},"
                                f" du hast gewonnen und ein Erfolgs-Bild freigeschaltet!")
                self.selection_screen.switch_to_erfolge()
            elif player_score == max_bot_score:
                # Wenn Unentschieden, direkt die nächste Frage laden, ohne Widgets zu entfernen
                self.quiz_config.in_tiebreaker_round = True
                self.quiz_config.question_count = 0
                messagebox.showinfo("Unentschieden", "Das Spiel ist unentschieden, wir starten zusätzliche Runden!")
                self.master.after(300, self.load_next_question)
                return
            else:
                self.quiz_config.in_tiebreaker_round = False
                winning_bot = max(self.bot_config.bots.items(), key=lambda item: item[1].score)[0]
                handle_game_end(
                    f"{winning_bot} hat gewonnen. Viel Glück beim nächsten Mal, {self.app_state.current_username}!")
        elif not self.quiz_config.in_tiebreaker_round and self.quiz_config.question_count == QuizConfig.NUM_QUESTIONS:
            # Analog für den Fall, dass der Spieler oder der Bot gewinnt, ohne in einer Tiebreaker-Runde zu sein
            if player_score > max_bot_score:
                self.user_won_quiz()
                handle_game_end(f"Herzlichen Glückwunsch {self.app_state.current_username},"
                                f" du hast gewonnen und ein Erfolgs-Bild freigeschaltet!")
                self.selection_screen.switch_to_erfolge()
            elif player_score == max_bot_score:
                self.quiz_config.in_tiebreaker_round = True
                self.quiz_config.question_count = 0
                messagebox.showinfo("Unentschieden", "Das Spiel ist unentschieden, wir starten zusätzliche Runden!")
                self.master.after(300, self.load_next_question)
                return
            else:
                winning_bot = max(self.bot_config.bots.items(), key=lambda item: item[1].score)[0]
                handle_game_end(
                    f"{winning_bot} hat gewonnen. Viel Glück beim nächsten Mal, {self.app_state.current_username}!")

        # Aufruf von save_result(), um das Ergebnis zu speichern
        self.save_result()

    def user_won_quiz(self):

        update_user_progress_on_win(self.app_state.current_username)
        # Lade den aktuellen Fortschritt des Benutzers
        unlocked_images = load_user_progress(self.app_state.current_username)

        # Speichern des aktualisierten Fortschritts
        save_user_progress(self.app_state.current_username, unlocked_images)

        self.success_area.update_unlocked_images()
        self.success_area.refresh_images()

    def save_result(self):
        # Erfasse das aktuelle Datum und die Uhrzeit
        current_time = datetime.datetime.now()

        session = get_db_session()
        user = session.query(User).filter_by(username=self.app_state.current_username).first()

        if not user:
            user = User(username=self.app_state.current_username)
            session.add(user)
            session.commit()

        # Neuen Leaderboard-Eintrag erstellen
        new_entry = Leaderboard(user_id=user.id, house=self.house, score=self.quiz_config.score, played_on=current_time)
        session.add(new_entry)
        session.commit()
        print(f"User ID: {user.id}, erreichte Punktzahl: {self.quiz_config.score}")
