import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main import choose_quiz
from main import get_db_session, Leaderboard, User
import datetime
from PIL import Image, ImageTk
import pygame


# Globale Variable für den aktuellen Benutzernamen
current_username = ""

# Globale Variable für den Musikstatus
is_music_playing = True

# Globale Variablen
dropdown_list = None
dropdown_var = None

# Globale Variablen für das Quizspiel
score = 0
question_count = 0
house = ""
in_tiebreaker_round = False
bot_score_labels = {}
score_label = None
result_label = None
NUM_OPTIONS = 4
NUM_QUESTIONS = 10
POINTS_PER_ANSWER = 10
bots = {}


# Datenbankmodell
Base = declarative_base()
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)

# Datenbankverbindung
engine = create_engine('sqlite:///users.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Hilfsfunktion, um Fenster in der Mitte des Bildschirms zu zentrieren
def center_window(window, width, height):
    # Bildschirmgröße abrufen
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Berechnen der x und y Koordinaten, um das Fenster in der Mitte des Bildschirms zu platzieren
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)

    window.geometry('%dx%d+%d+%d' % (width, height, x, y))

def is_username_existing(username):
    return session.query(User).filter_by(username=username).first() is not None

def add_username(username):
    if not is_username_existing(username):
        new_user = User(username=username)
        session.add(new_user)
        session.commit()
        return True
    return False

def get_recent_usernames(limit=10):
    return [user.username for user in session.query(User.username).order_by(User.id.desc()).limit(limit)]

def search_username(search_term):
    return session.query(User.username).filter(User.username.like(f"%{search_term}%")).all()


def on_name_submit():
    username = dropdown_var.get()
    if add_username(username):
        update_ui_with_new_username(username)  # Update your UI accordingly
    else:
        tk.messagebox.showinfo("Info", "Dieser Name existiert bereits.")

def update_ui_with_new_username(username):
    global current_username
    current_username = username
    welcome_label.config(text=f"Hallo {username}")

def get_all_usernames():
    return session.query(User.username).all()

def get_or_create_username():
    usernames = get_all_usernames()
    if usernames:
        return usernames[-1][0]  # Letzter Benutzername
    else:
        username = simpledialog.askstring("Benutzername", "Wie lautet Ihr Name?")
        add_username(username)
        return username if username else "Unbekannter Benutzer"

def change_user(label):
    global current_username
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

def start_quiz(house_name=None, username=''):
    global score_label, result_label, score, house, bot_score_labels, bots, bot_scores_frame, quiz_frame, question_count, options, user_house, quiz_background_image, quiz_frame

    # Setze das ausgewählte Haus als das aktuelle Haus
    if house_name:
        house = house_name
        user_house = house_name

        # Entfernen des ausgewählten Hauses aus den Bots
        if house in bots:
            del bots[house]  # Entfernt das ausgewählte Haus aus den Bots

            # Erstellen des Frames für Bot-Scores, ohne vertikale Ausdehnung
            if bot_scores_frame is None:
                bot_scores_frame = tk.Frame(quiz_frame, width=330)  # Beschränkung der Breite

                # Erstellung einer Überschrift
                header_label = tk.Label(bot_scores_frame, text="Haeuser-Scores", bg="#f5deb3",
                                        font=("Harry P", 40))
                header_label.pack()  # Packen der Überschrift im bot_scores_frame

                # Packen des bot_scores_frame mit Überschrift
                bot_scores_frame.pack(side='left', anchor='n')

            # hogwarts bots
            for name in bots.keys():
                bot_score_labels[name] = tk.Label(bot_scores_frame, text=f"{name}: 0", bg="#f5deb3",
                                                  font=("Arial", 19))
                bot_score_labels[name].pack()  # Labels werden jetzt untereinander angeordnet

    # Erstellen des Frames für Quiz-Widgets
    if quiz_frame is None:
        quiz_frame = tk.Frame(quiz_frame, width=330)  # Beschränkung der Breite

        bg_image = Image.open(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_perg_1.png")
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Erstellen eines Labels oder Canvas, um das Bild zu platzieren
        background_label = tk.Label(quiz_frame, image=bg_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        background_label.image = bg_photo

        # Erstellen eines Labels für die Überschrift innerhalb des quiz_widget_frame
        quiz_widget_label = tk.Label(quiz_frame, text="Quiz", bg="#f5deb3",
                                     font=("Harry P", 40))
        quiz_widget_label.pack()  # Packen der Überschrift im quiz_widget_frame

        # Packen des quiz_widget_frame mit Überschrift
        quiz_frame.pack(side='left', anchor='n')

    if quiz_background_image is None:
        # Laden des Hintergrundbildes
        quiz_background_image = ImageTk.PhotoImage(
            file=r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_perg_1.png")
        # Nachdem alle anderen Widgets hinzugefügt wurden
        quiz_background_label = tk.Label(quiz_frame, image=quiz_background_image)
        quiz_background_label.place(x=0, y=0, relwidth=1, relheight=1)
        quiz_background_label.lower()

        # Lade die nächste Frage und zeige sie an
    if question_count < NUM_QUESTIONS:
        question, options, correct_answer = choose_quiz()
        question_label = tk.Label(quiz_frame, text=question, bg='white', font=("Arial", 14, "bold"))
        question_label.pack()

        for i, option in enumerate(options, 1):
            button = tk.Button(quiz_frame, text=option, bg='white', font=("Arial", 14))
            button.pack()
            button.configure(command=lambda b=button, o=option: check_answer(b, o, correct_answer, options, username))

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
        quiz_window.after(300, lambda: start_quiz(house_name=house, username=username))  # Weitergabe des Benutzernamens
    else:
        end_quiz(username)  # Weitergabe des Benutzernamens

    # Prüfe, ob alle Fragen beantwortet wurden oder ob wir uns in einem Tiebreaker befinden
    if question_count < NUM_QUESTIONS or in_tiebreaker_round:
        # Lade die nächste Frage
        quiz_window.after(300, lambda: start_quiz(house_name=house, username=username))
    else:
        # Überprüfe auf Unentschieden nur am Ende des normalen Spiels
         if not in_tiebreaker_round:
            max_bot_score = max(bot.score for bot in bots.values())
            if score == max_bot_score:
                # Unentschieden detektiert, starte zusätzliche Runden
                in_tiebreaker_round = True
                question_count = 0  # Setze die Fragezahl zurück für die zusätzlichen Runden
                quiz_window.after(300, lambda: start_quiz(house_name=house, username=username))
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
    global quiz_window, score, question_count
    score = 0
    question_count = 0

    if quiz_window is not None:
        quiz_window.destroy()
        quiz_window = None

    #open_login_window()

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
            quiz_window.after(300, lambda: start_quiz(house_name=house, username=username))
            return  # Verhindere die Ausführung des restlichen Codes, da das Spiel fortgesetzt wird
        else:
            # Ein Bot hat gewonnen, Spiel endet
            in_tiebreaker_round = False
            winning_bot = max(bots.items(), key=lambda bot: bot[1].score)[0]
            messagebox.showinfo("Spielende", f"{winning_bot} hat gewonnen. Viel Glück beim nächsten Mal, {username}!")
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
            quiz_window.after(300, lambda: start_quiz(house_name=house, username=username))
            return  # Verhindere die Ausführung des restlichen Codes, da das Spiel fortgesetzt wird
        else:
            winning_bot = max(bots.items(), key=lambda bot: bot[1].score)[0]
            messagebox.showinfo("Spielende", f"{winning_bot} hat gewonnen. Viel Glück beim nächsten Mal, {username}!")

    # Entferne alle vorhandenen Widgets
    for widget in quiz_window.winfo_children():
        widget.destroy()

    # Zeige das Ergebnis an
    end_label = tk.Label(quiz_window, text=f"Du hast das Quiz beendet, {username}. Deine Punktzahl ist {score}.", bg='light grey')
    end_label.pack()

    # Buttons zum Speichern und Abbrechen
    save_button = tk.Button(quiz_window, text="Ergebnis speichern", command=lambda: save_result(username))
    save_button.pack()

    cancel_button = tk.Button(quiz_window, text="Abbrechen", command=quit_quiz)
    cancel_button.pack()



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


def show_leaderboard(tab):
    style = ttk.Style()
    style.configure('Treeview', background='#343a40', fieldbackground='#343a40',
                    foreground='white')  # Dunkelgraue Hintergrund- und weiße Textfarbe für das Leaderboard
    style.configure('Treeview.Heading', background='#343a40',
                    foreground='black')  # Dunkelgraue Hintergrundfarbe und schwarze Textfarbe für die Überschriften

    session = get_db_session()
    leaderboard_data = session.query(Leaderboard).order_by(Leaderboard.score.desc()).all()

    # Tabelle für das Leaderboard erstellen
    columns = ('user', 'house', 'score', 'played_on')
    leaderboard_table = ttk.Treeview(tab, columns=columns, show='headings')

    # Spaltenüberschriften definieren
    leaderboard_table.heading('user', text='User')
    leaderboard_table.heading('house', text='Haus')
    leaderboard_table.heading('score', text='Punktzahl')
    leaderboard_table.heading('played_on', text='Gespielt am')

    # Daten in die Tabelle einfügen
    for entry in leaderboard_data:
        user = session.query(User).filter_by(id=entry.user_id).first()
        leaderboard_table.insert('', 'end', values=(user.username, entry.house, entry.score, entry.played_on))

    # Tabelle im Tab platzieren
    leaderboard_table.pack(expand=True, fill='both')

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


def toggle_music():
    global is_music_playing
    if is_music_playing:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()
    is_music_playing = not is_music_playing


def open_home_screen():
    global name_entry, dropdown, dropdown_var, welcome_label, current_username, active_button, home_window


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

    # Benutzernamen abrufen oder erstellen
    username = get_or_create_username()


    # Neuer Frame für Begrüßung und Aktionen-Button
    top_frame = tk.Frame(home_frame, bg='#343a40')
    top_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)

    welcome_label = tk.Label(top_frame, text=f"Hallo {username}", font=("Harry P", 30), relief=tk.RAISED)
    welcome_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

    # Aktionen-Button direkt im top_frame ohne zusätzlichen Container
    actions_button = tk.Menubutton(top_frame, text="Aktionen", font=("Harry P", 30), relief=tk.RAISED, width=20)
    actions_menu = tk.Menu(actions_button, tearoff=0)
    actions_button["menu"] = actions_menu
    actions_button.grid(row=0, column=1, sticky='w', padx=10, pady=10)

    # Erstellen des Quiz-Frames innerhalb von frame_container
    quiz_frame = tk.Frame(frame_container, bg='#343a40')
    quiz_frame.place(x=0, y=0, relwidth=1, relheight=1)

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
    btn_gryffindor.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)  # Abstand zwischen den Buttons

    image_slytherin = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\slytherin.png")
    btn_slytherin = tk.Button(button_frame, image=image_slytherin,
                              command=lambda: on_house_select('Slytherin', current_username))
    btn_slytherin.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)  # Abstand zwischen den Buttons

    image_hufflepuff = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\hufflepuff.png")
    btn_hufflepuff = tk.Button(button_frame, image=image_hufflepuff,
                               command=lambda: on_house_select('Hufflepuff', current_username))
    btn_hufflepuff.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)  # Abstand zwischen den Buttons

    image_ravenclaw = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\ravenclaw.png")
    btn_ravenclaw = tk.Button(button_frame, image=image_ravenclaw,
                              command=lambda: on_house_select('Ravenclaw', current_username))
    btn_ravenclaw.grid(row=0, column=3, sticky='nsew', padx=10, pady=10)  # Abstand zwischen den Buttons

    # Halten Sie die Bildreferenzen, um die automatische Bereinigung durch Garbage Collector zu verhindern
    button_frame.image_gryffindor = image_gryffindor
    button_frame.image_slytherin = image_slytherin
    button_frame.image_hufflepuff = image_hufflepuff
    button_frame.image_ravenclaw = image_ravenclaw

    def on_house_select(house_name, username):
        if not username:  # Überprüfen, ob der Benutzername leer ist
            messagebox.showinfo("Fehler", "Bitte erst ein Haus auswählen.")
            return
        print(f"{house_name} ausgewählt, Benutzer: {username}")
        # Hier, anstatt das home_window zu zerstören, einfach den quiz_frame in den Vordergrund bringen
        switch_frame(quiz_frame)
        update_active_button(quiz_button)
        # Starte das Quiz mit dem ausgewählten Haus und Benutzernamen
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
        switch_frame(quiz_frame)
        update_active_button(quiz_button)

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









