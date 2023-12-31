import tkinter as tk
from tkinter import messagebox
from tkinter import Canvas
from tkinter import PhotoImage
from main import choose_quiz
from utils import set_house_background
from main import choose_quiz
import datetime
from PIL import Image, ImageTk
from utils import set_background_image
from bots import bots, update_bot_scores
from bots import HogwartsBot, update_bot_scores


# Globale Variablen
global quiz_window, house_window, bot_score_labels, score, question_count, house, bot_scores_frame

# Initialwerte für globale Variablen
quiz_window = None
house_window = None
bot_scores_frame = None
bot_score_labels = {}
score = 0
question_count = 0
house = ""

# Konstante für die Anzahl der möglichen Antworten
NUM_OPTIONS = 4
# Konstante für die Anzahl der Fragen pro Quiz
NUM_QUESTIONS = 10
# Konstante für die Punkte pro richtiger Antwort
POINTS_PER_ANSWER = 10

# Globale Variablen für die Bilder, um das Problem mit dem Garbage Collector zu vermeiden
global image_gryffindor, image_slytherin, image_hufflepuff, image_ravenclaw, background_image, user_house


#1. Hausauswahl-Fenster öffnen
def open_house_window():
    global house_window, image_slytherin, image_hufflepuff, image_ravenclaw, background_image

    house_window = tk.Tk()
    house_window.title("Harry Potter Quiz")

    # Setzen Sie das Fenster in den Vollbildmodus
    #house_window.attributes("-fullscreen", True)
    house_window.geometry("1500x1000")  # Beispielgröße, anpassen nach Bedarf

    # Hintergrundfoto einfügen
    background_image = tk.PhotoImage(file="/Users/heilscan/Desktop/Software Engineering Project/pictures/prod_promt_hausauswahl.png")
    background_label = tk.Label(house_window, image=background_image)
    background_label.grid(row=0, column=0, columnspan=4, sticky="nsew")

    # 1.1 Ein Haus auswählen; Haus-Bild = Button
    image_gryffindor = tk.PhotoImage(file="/Users/heilscan/Desktop/Software Engineering Project/pictures/gryffindor.png")
    image_slytherin = tk.PhotoImage(file="/Users/heilscan/Desktop/Software Engineering Project/pictures/slytherin.png")
    image_hufflepuff = tk.PhotoImage(file="/Users/heilscan/Desktop/Software Engineering Project/pictures/hufflepuff.png")
    image_ravenclaw = tk.PhotoImage(file="/Users/heilscan/Desktop/Software Engineering Project/pictures/ravenclaw.png")

    # Konfigurieren Sie die Buttons für jedes Haus, um sie im Raster anzuordnen
    btn_gryffindor = tk.Button(house_window, image=image_gryffindor, command=lambda: on_house_select('Gryffindor'))
    btn_gryffindor.grid(row=1, column=0, sticky="nsew")

    btn_slytherin = tk.Button(house_window, image=image_slytherin, command=lambda: on_house_select('Slytherin'))
    btn_slytherin.grid(row=1, column=1, sticky="nsew")

    btn_hufflepuff = tk.Button(house_window, image=image_hufflepuff, command=lambda: on_house_select('Hufflepuff'))
    btn_hufflepuff.grid(row=1, column=2, sticky="nsew")

    btn_ravenclaw = tk.Button(house_window, image=image_ravenclaw, command=lambda: on_house_select('Ravenclaw'))
    btn_ravenclaw.grid(row=1, column=3, sticky="nsew")

    # Konfigurieren Sie das Gewicht der Spalten und Zeilen, um die Größe anzupassen
    for i in range(4):
        house_window.grid_columnconfigure(i, weight=1)

    house_window.grid_rowconfigure(0, weight=1) # Kleinerer Anteil für das Foto
    house_window.grid_rowconfigure(1, weight=3) # Größerer Anteil für die Buttons

    house_window.mainloop()



# Funktion, die aufgerufen wird, wenn ein Haus ausgewählt wird
def on_house_select(house_name):
    global house_window
    print(f"{house_name} ausgewählt")  # Beispielaktion, hier Ihre Logik einfügen
    if house_window is not None:
        house_window.destroy()
    start_quiz(house_name)  # Öffnet das Quizfenster

# 2. Quiz-Fenster öffnen
def start_quiz(house_name=None):
    global quiz_window, score_label, result_label, score, house, bot_score_labels, bots, bot_scores_frame, question_count, options

    # Setze das ausgewählte Haus als das aktuelle Haus
    if house_name:
        house = house_name
        user_house = house_name

    # Überprüfen, ob das Quizfenster bereits existiert
    if quiz_window is None:
        quiz_window = tk.Tk()
        quiz_window.title(f"Harry Potter Quiz - {house}")
        quiz_window.geometry("1000x800")
        score = 0
        question_count = 0

        # Entfernen des ausgewählten Hauses aus den Bots
        if house in bots:
            del bots[house]  # Entfernt das ausgewählte Haus aus den Bots

        # Erstellen des Frames für Bot-Scores, wenn es noch nicht existiert
        if bot_scores_frame is None:
            bot_scores_frame = tk.Frame(quiz_window, bg='light grey')
            bot_scores_frame.pack(side='top', fill='x')
# hogwarts bots
            for name in bots.keys():
                bot_score_labels[name] = tk.Label(bot_scores_frame, text=f"{name} Punktzahl: 0", bg='light grey')
                bot_score_labels[name].pack(side='left')

    # Entfernen aller Widgets, die nicht zum bot_scores_frame gehören
    for widget in quiz_window.winfo_children():
        if widget != bot_scores_frame:
            widget.destroy()

    # Lade die nächste Frage und zeige sie an
    if question_count < NUM_QUESTIONS:
        question, options, correct_answer = choose_quiz()
        question_label = tk.Label(quiz_window, text=question, bg='light grey')
        question_label.pack()

        for i, option in enumerate(options, 1):
            button = tk.Button(quiz_window, text=option, bg='white')
            button.pack()
            button.configure(command=lambda b=button, o=option: check_answer(b, o, correct_answer, options))

        score_label = tk.Label(quiz_window, text=f"Punktzahl: {score}", bg='light grey')
        score_label.pack()
        result_label = tk.Label(quiz_window, text="", bg='light grey')
        result_label.pack()
    else:
        end_quiz()


def check_answer(button, user_answer, correct_answer, options):
    global score, question_count, bots
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
        quiz_window.after(300, start_quiz)  # Startet die nächste Frage nach 0,3 Sekunden
    else:
        end_quiz()

def update_bots_and_scores(options, correct_answer):
    global bots, bot_score_labels

    # Aktualisieren Sie die Antworten und die Scores der Bots
    for bot_house, bot in bots.items():
        bot_choice = bot.choose_answer(options)
        bot.update_score(bot_choice == correct_answer)

        # Aktualisieren Sie die Labels der Bot-Scores
        bot_score_labels[bot_house].config(text=f"{bot_house} Punktzahl: {bot.score}")


def quit_quiz():
    global quiz_window, score, question_count
    score = 0
    question_count = 0

    if quiz_window is not None:
        quiz_window.destroy()
        quiz_window = None

    #open_login_window()

def end_quiz():
    global score, house
    for widget in quiz_window.winfo_children():
        widget.destroy()  # Entfernt alle vorhandenen Widgets

    end_label = tk.Label(quiz_window, text=f"Du hast das Quiz beendet. Deine Punktzahl ist {score}.", bg='light grey')
    end_label.pack()

    save_button = tk.Button(quiz_window, text="Ergebnis speichern", command=save_result)
    save_button.pack()

    cancel_button = tk.Button(quiz_window, text="Abbrechen", command=quit_quiz)
    cancel_button.pack()


def save_result():
    global score, house
    # Erfasse das aktuelle Datum und die Uhrzeit
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")  # Format: Jahr-Monat-Tag Stunde:Minute:Sekunde
 # Speichert die Ergebnisse des Quiz in einer Datei
    with open('results.txt', 'a') as f:
        f.write(f"{house},{score},{formatted_time}\n")  # Fügen Sie das Datum und die Uhrzeit hinzu
    messagebox.showinfo('Erfolg', 'Dein Ergebnis wurde gespeichert.')
    quit_quiz()



def handle_quiz_round():
    global question_count, score_label, result_label, bots, bot_score_labels
    if question_count == NUM_QUESTIONS:
        end_quiz()  # End the quiz if the maximum number of questions is reached
    else:
        question, options, correct_answer = choose_quiz()

        # Entferne alte Label-Werte, bevor sie aktualisiert werden
        for label in bot_score_labels.values():
            label.pack_forget()



        # Display the question and options in the GUI
        question_label = tk.Label(quiz_window, text=question, bg='light grey')
        question_label.pack()

        for i, option in enumerate(options, 1):
            button = tk.Button(quiz_window, text=option, bg='white')
            button.pack()
            button.configure(command=lambda button=button, option=option: check_answer(button, option, correct_answer))



def check_credentials():
    # Überprüfen Sie die Anmeldeinformationen und starten Sie das Quiz, wenn sie korrekt sind
    if username_entry.get() == 'admin' and password_entry.get() == 'password':
        messagebox.showinfo('Erfolg', 'Anmeldung erfolgreich!')
        login_window.destroy()  # Schließt das Anmeldefenster
        open_house_window()  # Öffnet das Hausauswahlfenster
    else:
        messagebox.showerror('Fehler', 'Falscher Benutzername oder Passwort')

    start_quiz()


def handle_quiz_round():
    global question_count, score_label, result_label, bots, bot_score_labels
    if question_count == NUM_QUESTIONS:
        end_quiz()  # End the quiz if the maximum number of questions is reached
    else:
        question, options, correct_answer = choose_quiz()


        # Display the question and options in the GUI
        question_label = tk.Label(quiz_window, text=question, bg='light grey')
        question_label.pack()

        for i, option in enumerate(options, 1):
            button = tk.Button(quiz_window, text=option, bg='white')
            button.pack()
            button.configure(command=lambda button=button, option=option: check_answer(button, option, correct_answer))






