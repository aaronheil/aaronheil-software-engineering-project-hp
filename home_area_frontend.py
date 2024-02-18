

def open_home_screen():
    global current_username, name_entry, dropdown, dropdown_var, welcome_label, current_username, active_button, home_window


    home_window = tk.Tk()
    home_window.title("Home")
    home_window.attributes("-fullscreen", True)

    # Navigation Frame für die Buttons
    nav_frame = tk.Frame(home_window, bg='#343a40')
    nav_frame.pack(side='top', fill='x')  # Oben im Hauptfenster anordnen

    # Grid-Layout für die Platzierung von Frames

    # Verwenden Sie Grid-Layout für die Platzierung von Frames und Buttons
    frame_container = tk.Frame(home_window)
    frame_container.pack(fill='both', expand=True, side='bottom')
    frame_container.grid_columnconfigure(0, weight=1)
    frame_container.grid_rowconfigure(0, weight=1)

    # Einzelne Frames mit dunkelgrauer Hintergrundfarbe
    home_frame = tk.Frame(frame_container, bg='#343a40')
    quiz_frame = tk.Frame(frame_container, bg='#343a40')
    erfolge_frame = tk.Frame(frame_container, bg='#343a40')
    statistik_frame = tk.Frame(frame_container, bg='#343a40')

    for frame in [home_frame, quiz_frame, erfolge_frame, statistik_frame]:
        frame.grid(row=0, column=0, sticky='nsew')


    # Globale Variable für den aktuell ausgewählten Button
    active_button = None

    current_username = get_or_create_username()  # Aktualisiere den aktuellen Benutzernamen





    # Neuer Frame für Begrüßung und Aktionen-Button
    top_frame = tk.Frame(home_frame, bg='#343a40')
    top_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)

    welcome_label = tk.Label(top_frame, text=f"Hallo {current_username}", font=("Harry P", 30), relief=tk.RAISED)
    welcome_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

    # Aktionen-Button direkt im top_frame ohne zusätzlichen Container
    actions_button = tk.Menubutton(top_frame, text="Aktionen", font=("Harry P", 30), relief=tk.RAISED, width=20)
    actions_menu = tk.Menu(actions_button, tearoff=0)
    actions_button["menu"] = actions_menu
    actions_button.grid(row=0, column=1, sticky='w', padx=10, pady=10)

    # Initialisieren Sie quiz_frame, falls noch nicht geschehen
    quiz_frame = tk.Frame(frame_container, bg='#343a40')
    quiz_frame.grid(row=0, column=0, sticky='nsew')

    # Funktion zum Anzeigen der Dropdown-Suchleiste
    def show_dropdown():
        global dropdown_list, dropdown_var, search_var
        dropdown_window = tk.Toplevel(home_window)
        dropdown_window.title("User auswählen")
        # Fenstergröße und -position einstellen
        center_window(dropdown_window, 300, 200)

        # Suchleiste hinzufügen
        search_var = tk.StringVar()
        search_entry = tk.Entry(dropdown_window, textvariable=search_var)
        search_entry.pack(fill='x')
        search_entry.bind('<KeyRelease>', update_dropdown)

        # Erstelle einen Frame für die Listbox und Scrollbar
        listbox_frame = tk.Frame(dropdown_window)
        listbox_frame.pack(fill='both', expand=True)

        # Erstelle die Scrollbar
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')

        # Erstelle die Listbox
        dropdown_list = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=10)
        dropdown_list.pack(side='left', fill='both', expand=True)

        # Verknüpfung von Scrollbar und Listbox
        scrollbar.config(command=dropdown_list.yview)

        # Initialisiere die Listbox mit allen Benutzernamen
        update_dropdown()

        # Event-Handler für die Listbox
        dropdown_list.bind('<Double-1>', on_double_click)  # Doppelklick
        dropdown_list.bind('<Button-3>', on_right_click)  # Rechtsklick
        dropdown_list.bind('<Return>', on_enter_pressed)  # Enter-Taste

    # Unterbuttons zum Menubutton hinzufügen
    actions_menu.add_command(label="Neuen User anlegen", command=lambda: change_user(welcome_label), font=("Arial", 16),
                             background='white', foreground='black')
    actions_menu.add_separator()  # Fügt eine Trennlinie hinzu
    actions_menu.add_command(label="User auswählen", command=show_dropdown, font=("Arial", 16), background='white',
                             foreground='black')
    actions_menu.add_separator()  # Fügt eine Trennlinie hinzu
    actions_menu.add_command(label="Musik Ein / Aus", command=toggle_music, font=("Arial", 16), background='white',
                             foreground='black')


    button_frame = tk.Frame(home_frame, bg='#343a40')
    button_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
    button_frame.grid_columnconfigure([0, 1, 2, 3], weight=1)
    button_frame.grid_rowconfigure(0, weight=1)

    # Funktionen zum Laden und Skalieren der Bilder
    def load_and_resize_image(image_path, size=(400, 500)):
        original_image = Image.open(image_path)
        resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(resized_image)

    # Hausauswahl-Buttons erstellen und im button_frame positionieren
    image_gryffindor = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\gryffindor.png")
    btn_gryffindor = tk.Button(button_frame, image=image_gryffindor,
                               command=lambda: on_house_select('Gryffindor', current_username))
    btn_gryffindor.grid(row=0, column=0, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

    image_slytherin = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\slytherin.png")
    btn_slytherin = tk.Button(button_frame, image=image_slytherin,
                              command=lambda: on_house_select('Slytherin', current_username))
    btn_slytherin.grid(row=0, column=1, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

    image_hufflepuff = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\hufflepuff.png")
    btn_hufflepuff = tk.Button(button_frame, image=image_hufflepuff,
                               command=lambda: on_house_select('Hufflepuff', current_username))
    btn_hufflepuff.grid(row=0, column=2, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

    image_ravenclaw = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\ravenclaw.png")
    btn_ravenclaw = tk.Button(button_frame, image=image_ravenclaw,
                              command=lambda: on_house_select('Ravenclaw', current_username))
    btn_ravenclaw.grid(row=0, column=3, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

    # Halten Sie die Bildreferenzen, um die automatische Bereinigung durch Garbage Collector zu verhindern
    button_frame.image_gryffindor = image_gryffindor
    button_frame.image_slytherin = image_slytherin
    button_frame.image_hufflepuff = image_hufflepuff
    button_frame.image_ravenclaw = image_ravenclaw

    # Anpassung der on_house_select Funktion
    def on_house_select(house_name, username):
        global house, current_username
        if not current_username:  # Überprüfen, ob der Benutzername leer ist
            messagebox.showinfo("Fehler", "Bitte erst einen Benutzer auswählen.")
            return
        if not house_name:
            messagebox.showinfo("Fehler", "Bitte erst ein Haus auswählen.")
            return
        house = house_name
        current_username = username
        print(f"{house_name} ausgewählt, Benutzer: {username}")
        switch_frame(quiz_frame)
        update_active_button(quiz_button)
        start_quiz(house_name, username)

    def update_active_button(new_active_button):
        global active_button
        # Setzen Sie alle Buttons auf normale Farbe zurück
        for button in [home_button, quiz_button, erfolge_button, statistik_button]:
            button.config(bg='SystemButtonFace')  # Setzen Sie die Standardfarbe zurück
        # Setzen Sie die Farbe des aktiven Buttons
        new_active_button.config(bg='lightgrey')  # Hervorheben des aktiven Buttons
        active_button = new_active_button


    # Funktion, um den Frame zu wechseln
    def switch_frame(frame):
        frame.tkraise()

    # Starten Sie mit dem Anzeigen des Home-Frames
    switch_frame(home_frame)
    show_leaderboard(statistik_frame)  # Leaderboard im Tab Statistik anzeigen


    def switch_to_home():
        switch_frame(home_frame)
        update_active_button(home_button)

    def switch_to_quiz():
        global current_username, house, is_quiz_active
        if is_quiz_active:
            messagebox.showinfo("Info", "Das Quiz läuft bereits.")
            return
        switch_frame(quiz_frame)
        update_active_button(quiz_button)
        # Überprüfe, ob ein Benutzername und ein Haus ausgewählt wurden
        if current_username and house:
            start_quiz(frame_container, house, current_username)
        else:
            # Hinweis: Sie können hier eine Benachrichtigung anzeigen oder die Auswahl erzwingen
            messagebox.showinfo("Info", "Bitte wählen Sie einen Benutzer und ein Haus, bevor Sie das Quiz starten.")
            switch_to_home()

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

    def switch_to_erfolge():
        switch_frame(erfolge_frame)
        update_active_button(erfolge_button)

    def switch_to_statistik():
        switch_frame(statistik_frame)
        update_active_button(statistik_button)


    home_button = tk.Button(nav_frame, text='⌂ Home', command=switch_to_home, font=("Harry P", 40))
    home_button.pack(side='left', fill='x', expand=True)

    quiz_button = tk.Button(nav_frame, text='🎮 Quiz', command=switch_to_quiz, font=("Harry P", 40))
    quiz_button.pack(side='left', fill='x', expand=True)

    erfolge_button = tk.Button(nav_frame, text='\U0001F3C6 Erfolge', command=switch_to_erfolge, font=("Harry P", 40))
    erfolge_button.pack(side='left', fill='x', expand=True)

    statistik_button = tk.Button(nav_frame, text='\U0001F4C8 Statistik', command=switch_to_statistik,
                                 font=("Harry P", 40))
    statistik_button.pack(side='left', fill='x', expand=True)

    # Setzen Sie den anfänglichen aktiven Button
    update_active_button(home_button)



    home_window.mainloop()
