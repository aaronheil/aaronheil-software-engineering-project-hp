"""
# Initialisieren Sie quiz_frame, falls noch nicht geschehen
    quiz_frame = tk.Frame(frame_container, bg='#343a40')
    quiz_frame.grid(row=0, column=0, sticky='nsew')


def start_quiz(house_name=None, username=''):
    global quiz_frame, score_label, result_label, score, house, bot_score_labels, bots, bot_scores_frame, quiz_widget_frame, question_count, options, user_house, quiz_background_image

    # Setze das ausgewählte Haus als das aktuelle Haus
    if house_name:
        house = house_name
        user_house = house_name

    # Überprüfen, ob das Quizfenster bereits existiert
    if quiz_frame is None:
        quiz_frame = tk.Tk()
        quiz_frame.title(f"Harry Potter Quiz - {house}")
        quiz_frame.attributes("-fullscreen", True)
        # Schaltfläche zum Schließen des Fensters
        # close_button = tk.Button(quiz_frame, text="Schließen", command=close_window)
        # close_button.pack()
        # Tastenkombination zum Verlassen des Vollbildmodus
        quiz_frame.bind("<Escape>", toggle_fullscreen)
        score = 0
        question_count = 0

    # Entfernen des ausgewählten Hauses aus den Bots
    if house in bots:
        del bots[house]  # Entfernt das ausgewählte Haus aus den Bots

    # Erstellen des Frames für Bot-Scores, ohne vertikale Ausdehnung
    if bot_scores_frame is None:
        bot_scores_frame = tk.Frame(quiz_frame)  # Beschränkung der Breite


        # Erstellung einer Überschrift
        header_label = tk.Label(bot_scores_frame, text="Haeuser-Scores", bg="#f5deb3",
                                font=("Harry P", 40))
        header_label.pack()  # Packen der Überschrift im bot_scores_frame

        # Packen des bot_scores_frame mit Überschrift
        bot_scores_frame.pack(side='right', anchor='n')

        # hogwarts bots
        for name in bots.keys():
            bot_score_labels[name] = tk.Label(bot_scores_frame, text=f"{name}: 0", bg="#f5deb3",
                                              font=("Arial", 19))
            bot_score_labels[name].pack()  # Labels werden jetzt untereinander angeordnet

    for widget in quiz_frame.winfo_children():
        # Überprüfe, ob das Widget das Hintergrundbild ist
        if isinstance(widget, tk.Label) and widget.cget("image") == str(quiz_background_image):
            continue  # Überspringe das Hintergrundbild-Widget

        if widget != bot_scores_frame:
            widget.destroy()
            if widget == quiz_widget_frame:
                quiz_widget_frame = None

    # Erstellen des Frames für Quiz-Widgets
    if quiz_widget_frame is None:
        quiz_widget_frame = tk.Frame(quiz_frame, width=330)  # Beschränkung der Breite





        # Erstellen eines Labels für die Überschrift innerhalb des quiz_widget_frame
        quiz_widget_label = tk.Label(quiz_widget_frame, text="Quiz", bg="#f5deb3",
                                     font=("Harry P", 40))
        quiz_widget_label.pack()  # Packen der Überschrift im quiz_widget_frame

        # Packen des quiz_widget_frame mit Überschrift
        quiz_widget_frame.pack(side='left', anchor='n')



    # Lade die nächste Frage und zeige sie an
    if question_count < NUM_QUESTIONS:
        question, options, correct_answer = choose_quiz()
        question_label = tk.Label(quiz_widget_frame, text=question, bg='white', font=("Arial", 14, "bold"))
        question_label.pack()

        for i, option in enumerate(options, 1):
            button = tk.Button(quiz_widget_frame, text=option, bg='white', font=("Arial", 14))
            button.pack()
            button.configure(
                command=lambda b=button, o=option: check_answer(b, o, correct_answer, options, username))

        # Zerstöre score_label und result_label, wenn sie existieren, und erstelle sie neu
        if score_label is not None:
            score_label.destroy()
        if result_label is not None:
            result_label.destroy()

        score_label = tk.Label(bot_scores_frame, text=f"{user_house} ({username}): {score}", bg="#f5deb3",
                               font=("Arial", 19))
        score_label.pack()
        result_label = tk.Label(bot_scores_frame, text="", bg="#f5deb3", font=("Arial", 19))
        result_label.pack()
    else:
        end_quiz(username)

def check_answer(button, user_answer, correct_answer, options, username):
    global score, question_count, bots, in_tiebreaker_round

    if user_answer == correct_answer:
        button.configure(bg='green')
        result_label.config(text="Richtige Antwort!", fg='green')
        score += POINTS_PER_ANSWER  # Erhöht die Punktzahl
    else:
        button.configure(bg='red')
        result_label.config(text="Falsche Antwort.", fg='red')

    update_bots_and_scores(options, correct_answer)  # Aktualisieren Sie die Bots und deren Scores

    question_count += 1  # Erhöht die Anzahl der gestellten Fragen
    if question_count < NUM_QUESTIONS:
        quiz_frame.after(300, lambda: start_quiz(house_name=house,
                                                 username=username))  # Weitergabe des Benutzernamens
    else:
        end_quiz(username)  # Weitergabe des Benutzernamens

    # Prüfe, ob alle Fragen beantwortet wurden oder ob wir uns in einem Tiebreaker befinden
    if question_count < NUM_QUESTIONS or in_tiebreaker_round:
        # Lade die nächste Frage
        quiz_frame.after(300, lambda: start_quiz(house_name=house, username=username))
    else:
        # Überprüfe auf Unentschieden nur am Ende des normalen Spiels
        if not in_tiebreaker_round:
            max_bot_score = max(bot.score for bot in bots.values())
            if score == max_bot_score:
                # Unentschieden detektiert, starte zusätzliche Runden
                in_tiebreaker_round = True
                question_count = 0  # Setze die Fragezahl zurück für die zusätzlichen Runden
                quiz_frame.after(300, lambda: start_quiz(house_name=house, username=username))
            else:
                # Kein Unentschieden, Spiel endet
                end_quiz(username)

def update_bots_and_scores(options, correct_answer):
    global bots, bot_score_labels

    # Aktualisieren Sie die Antworten und die Scores der Bots
    for bot_house, bot in bots.items():
        bot_choice = bot.choose_answer(options)
        bot.update_score(bot_choice == correct_answer)

        # Aktualisieren Sie die Labels der Bot-Scores
        bot_score_labels[bot_house].config(text=f"{bot_house}: {bot.score}")

def quit_quiz():
    global quiz_frame, score, question_count
    score = 0
    question_count = 0

    if quiz_frame is not None:
        quiz_frame.destroy()
        quiz_frame = None
        setup_quiz()



def end_quiz(username=''):
    global score, house, in_tiebreaker_round, bots, bot_score_labels, question_count

    if in_tiebreaker_round:
        max_bot_score = max(bot.score for bot in bots.values())
        if score > max_bot_score:
            # Spieler hat gewonnen, Spiel endet
            in_tiebreaker_round = False
            messagebox.showinfo("Spielende", f"Herzlichen Glückwunsch {username}, du hast gewonnen!")
        elif score == max_bot_score:
            # Unentschieden besteht weiterhin, starte weitere zusätzliche Runden
            in_tiebreaker_round = True
            question_count = 0  # Setze die Fragezahl zurück für die zusätzlichen Runden
            messagebox.showinfo("Unentschieden", "Das Spiel ist unentschieden, wir starten zusätzliche Runden!")
            quiz_frame.after(300, lambda: start_quiz(house_name=house, username=username))
            return  # Verhindere die Ausführung des restlichen Codes, da das Spiel fortgesetzt wird
        else:
            # Ein Bot hat gewonnen, Spiel endet
            in_tiebreaker_round = False
            winning_bot = max(bots.items(), key=lambda bot: bot[1].score)[0]
            messagebox.showinfo("Spielende",
                                f"{winning_bot} hat gewonnen. Viel Glück beim nächsten Mal, {username}!")
    elif not in_tiebreaker_round and question_count == NUM_QUESTIONS:
        # Normaler Spielabschluss, wenn nicht in zusätzlichen Runden
        # Prüfe auf Unentschieden am regulären Spielende
        max_bot_score = max(bot.score for bot in bots.values())
        if score > max_bot_score:
            messagebox.showinfo("Spielende", f"Herzlichen Glückwunsch {username}, du hast gewonnen!")
        elif score == max_bot_score:
            # Unentschieden detektiert, starte zusätzliche Runden
            in_tiebreaker_round = True
            question_count = 0  # Setze die Fragezahl zurück für die zusätzlichen Runden
            messagebox.showinfo("Unentschieden", "Das Spiel ist unentschieden, wir starten zusätzliche Runden!")
            quiz_frame.after(300, lambda: start_quiz(house_name=house, username=username))
            return  # Verhindere die Ausführung des restlichen Codes, da das Spiel fortgesetzt wird
        else:
            winning_bot = max(bots.items(), key=lambda bot: bot[1].score)[0]
            messagebox.showinfo("Spielende",
                                f"{winning_bot} hat gewonnen. Viel Glück beim nächsten Mal, {username}!")

    # Entferne alle vorhandenen Widgets
    for widget in quiz_frame.winfo_children():
        widget.destroy()

    # Zeige das Ergebnis an
    end_label = tk.Label(quiz_frame,
                         text=f"Du hast das Quiz beendet, {username}. Deine Punktzahl ist {score}.",
                         bg='light grey')
    end_label.pack()


    # Buttons zum Speichern und Abbrechen
    save_button = tk.Button(quiz_frame, text="Ergebnis speichern", command=lambda: save_result(username))
    save_button.pack()

    cancel_button = tk.Button(quiz_frame, text="Abbrechen", command=quit_quiz)
    cancel_button.pack()

    setup_quiz()  # Quiz neu initialisieren

    # Schalte zum Home-Frame und aktualisiere den aktiven Button
    switch_frame(home_frame)
    update_active_button(home_button)




def save_result(username):
    global score, house
    # Erfasse das aktuelle Datum und die Uhrzeit
    current_time = datetime.datetime.now()

    session = get_db_session()
    user = session.query(User).filter_by(username=username).first()

    if user is None:
        # Wenn der Benutzer nicht existiert, fügen Sie ihn hinzu
        user = User(username=username)
        session.add(user)
        session.commit()

    # Neuen Leaderboard-Eintrag erstellen
    new_entry = Leaderboard(user_id=user.id, house=house, score=score, played_on=current_time)
    session.add(new_entry)
    session.commit()

    messagebox.showinfo('Erfolg', 'Dein Ergebnis wurde gespeichert.')
    quit_quiz()
    setup_quiz()





home_window.mainloop()

"""