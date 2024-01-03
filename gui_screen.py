import tkinter as tk
from tkinter import messagebox
from tkinter import Canvas
from tkinter import PhotoImage
import utils
from main import choose_quiz
from utils import set_house_background
from main import choose_quiz
import datetime
from PIL import Image, ImageTk
from utils import set_frame_background
from utils import set_background
from bots import bots, update_bot_scores
from bots import HogwartsBot, update_bot_scores


# Globale Variablen
global quiz_window, house_window, bot_score_labels, score, question_count, house, bot_scores_frame, quiz_widget_frame, quiz_background_image

# Initialwerte für globale Variablen
quiz_window = None
house_window = None
bot_scores_frame = None
quiz_widget_frame = None
test_frame = None
quiz_background_image = None
bot_score_labels = {}
score_label = None
result_label = None
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
    house_window.attributes("-fullscreen", True)
    #house_window.geometry("1500x1000")  # Beispielgröße, anpassen nach Bedarf

    # Laden des Hintergrundbildes mit PIL und Größenanpassung
    pil_image = Image.open(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_promt_hausauswahl1.png")
    pil_image = pil_image.resize((1400, 335), Image.Resampling.LANCZOS)  # Verwenden Sie Image.Resampling.LANCZOS
    background_image = ImageTk.PhotoImage(pil_image)


    background_label = tk.Label(house_window, image=background_image)
    background_label.grid(row=0, column=0, columnspan=4, sticky="nsew")

    # 1.1 Ein Haus auswählen; Haus-Bild = Button
    image_gryffindor = tk.PhotoImage(file=r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\gryffindor.png")
    image_slytherin = tk.PhotoImage(file=r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\slytherin.png")
    image_hufflepuff = tk.PhotoImage(file=r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\hufflepuff.png")
    image_ravenclaw = tk.PhotoImage(file=r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\ravenclaw.png")

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

def toggle_fullscreen(event=None):
    quiz_window.attributes("-fullscreen", False)  # Schaltet den Vollbildmodus aus
    quiz_window.destroy()  # Schließt das Fenster

#def close_window():
    #quiz_window.destroy()

# 2. Quiz-Fenster öffnen
def start_quiz(house_name=None):
    global quiz_window, score_label, result_label, score, house, bot_score_labels, bots, bot_scores_frame, quiz_widget_frame, question_count, options, user_house, test_frame, quiz_background_image

    # Setze das ausgewählte Haus als das aktuelle Haus
    if house_name:
        house = house_name
        user_house = house_name

    # Überprüfen, ob das Quizfenster bereits existiert
    if quiz_window is None:
        quiz_window = tk.Tk()
        quiz_window.title(f"Harry Potter Quiz - {house}")
        quiz_window.attributes("-fullscreen", True)
        # Schaltfläche zum Schließen des Fensters
        #close_button = tk.Button(quiz_window, text="Schließen", command=close_window)
        #close_button.pack()
        # Tastenkombination zum Verlassen des Vollbildmodus
        quiz_window.bind("<Escape>", toggle_fullscreen)
        score = 0
        question_count = 0


        # Entfernen des ausgewählten Hauses aus den Bots
        if house in bots:
            del bots[house]  # Entfernt das ausgewählte Haus aus den Bots

            # Erstellen des Frames für Bot-Scores, ohne vertikale Ausdehnung
            if bot_scores_frame is None:
                bot_scores_frame = tk.Frame(quiz_window, width=330)  # Beschränkung der Breite

                bg_image = Image.open(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_pergament.png")  # Ersetzen Sie dies durch den Pfad zu Ihrem Bild
                bg_photo = ImageTk.PhotoImage(bg_image)

                # Erstellen eines Labels oder Canvas, um das Bild zu platzieren
                background_label = tk.Label(bot_scores_frame, image=bg_photo)
                background_label.place(x=0, y=0, relwidth=1, relheight=1)
                background_label.image = bg_photo


                # Erstellen eines Labels für die Überschrift innerhalb des bot_scores_frame
                header_label = tk.Label(bot_scores_frame, text="Haeuser-Scores", bg="#f5deb3",
                                        font=("Harry P", 40))
                header_label.pack()  # Packen der Überschrift im bot_scores_frame

                # Packen des bot_scores_frame mit Überschrift
                bot_scores_frame.pack(side='left', anchor='n')


            # hogwarts bots
            for name in bots.keys():
                bot_score_labels[name] = tk.Label(bot_scores_frame, text=f"{name}: 0", bg="#f5deb3", font=("Arial", 19))
                bot_score_labels[name].pack()  # Labels werden jetzt untereinander angeordnet

    for widget in quiz_window.winfo_children():
        # Überprüfe, ob das Widget das Hintergrundbild ist
        if isinstance(widget, tk.Label) and widget.cget("image") == str(quiz_background_image):
            continue  # Überspringe das Hintergrundbild-Widget

        if widget != bot_scores_frame and widget != test_frame:
            widget.destroy()
            if widget == quiz_widget_frame:
                quiz_widget_frame = None

    # Erstellen des Frames für Quiz-Widgets
    if quiz_widget_frame is None:
        quiz_widget_frame = tk.Frame(quiz_window, width=330) # Beschränkung der Breite

        bg_image = Image.open(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_perg_1.png")
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Erstellen eines Labels oder Canvas, um das Bild zu platzieren
        background_label = tk.Label(quiz_widget_frame, image=bg_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        background_label.image = bg_photo

        # Erstellen eines Labels für die Überschrift innerhalb des quiz_widget_frame
        quiz_widget_label = tk.Label(quiz_widget_frame, text="Quiz", bg="#f5deb3",
                                             font=("Harry P", 40))
        quiz_widget_label.pack()  # Packen der Überschrift im quiz_widget_frame

        # Packen des quiz_widget_frame mit Überschrift
        quiz_widget_frame.pack(side='left', anchor='n')


    # Erstellen des Test-Frames
    if test_frame is None:
        test_frame = tk.Frame(quiz_window, padx=10, pady=10)  # Auffällige Farbe für das Testen

        # Laden des Bildes und Anpassen an die Größe des Frames
        bg_image = Image.open(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_perg_1.png")  # Ersetzen Sie dies durch den Pfad zu Ihrem Bild
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Erstellen eines Labels oder Canvas, um das Bild zu platzieren
        background_label = tk.Label(test_frame, image=bg_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        background_label.image = bg_photo  # Verhindert, dass das Bild vom Garbage Collector gelöscht wird

        test_label = tk.Label(test_frame, text="Test", font=("Arial", 16), bg='red')
        test_button = tk.Button(test_frame, text="Button", command=lambda: print("Button gedrückt"))

        # Packen der Widgets im Test-Frame
        test_label.pack(pady=(0, 10))
        test_button.pack()

        # Packen des Test-Frames im quiz_window
        test_frame.pack(side='bottom', fill='x')




    if quiz_background_image is None:
        # Laden des Hintergrundbildes
        quiz_background_image = tk.PhotoImage(file=r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_perg_1.png")  # Ändern Sie den Pfad zum Bild
        # Nachdem alle anderen Widgets hinzugefügt wurden
        quiz_background_label = tk.Label(quiz_window, image=quiz_background_image)
        quiz_background_label.place(x=0, y=0, relwidth=1, relheight=1)
        quiz_background_label.lower()  # Setzt das Hintergrundbild hinter alle anderen Widgets
        # Lade das Bild und skaliere es auf die Größe des Fensters



    # Lade die nächste Frage und zeige sie an
    if question_count < NUM_QUESTIONS:
        question, options, correct_answer = choose_quiz()
        question_label = tk.Label(quiz_widget_frame, text=question, bg='white', font=("Arial", 14, "bold"))
        question_label.pack()

        for i, option in enumerate(options, 1):
            button = tk.Button(quiz_widget_frame, text=option, bg='white', font=("Arial", 14))
            button.pack()
            button.configure(command=lambda b=button, o=option: check_answer(b, o, correct_answer, options))

        # Zerstöre score_label und result_label, wenn sie existieren, und erstelle sie neu
        if score_label is not None:
            score_label.destroy()
        if result_label is not None:
            result_label.destroy()

        score_label = tk.Label(bot_scores_frame, text=f"{user_house} (You): {score}", bg="#f5deb3", font=("Arial", 19))
        score_label.pack()
        result_label = tk.Label(bot_scores_frame, text="", bg="#f5deb3", font=("Arial", 19))
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
        bot_score_labels[bot_house].config(text=f"{bot_house}: {bot.score}")


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
    formatted_time = current_time.strftime("%d.%m.%Y %H:%M:%S")  # Deutsches Datumsformat: Tag.Monat.Jahr Stunde:Minute:Sekunde

    # Speichert die Ergebnisse des Quiz in einer Datei
    with open('results.txt', 'a') as f:
        f.write(f"{house},{score},{formatted_time}\n")  # Fügen Sie das Datum und die Uhrzeit hinzu
    messagebox.showinfo('Erfolg', 'Dein Ergebnis wurde gespeichert.')
    quit_quiz()






