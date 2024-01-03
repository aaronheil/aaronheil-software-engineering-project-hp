import tkinter as tk
import pygame
from tkinter import PhotoImage
from utils import set_background
from gui_screen import open_house_window


def play_music():
    # Musikdatei laden und abspielen
    pygame.mixer.init()  # Initialisieren des Mixers
    pygame.mixer.music.load(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\19 - Hedwig's Theme.mp3")  # Pfad zur MP3-Datei
    pygame.mixer.music.play(-1)  # Endlosschleife: -1 bedeutet, dass die Musik unendlich oft wiederholt wird

def open_quiz():
    play_music()  # Musik abspielen beim Öffnen des Quiz-Fensters
    # Öffnet das Quiz-Fenster
    login_window.destroy()  # Schließt das Login-Fenster
    open_house_window()  # Öffnet das Hausauswahlfenster


# Hauptfenster erstellen
login_window = tk.Tk()
login_window.title("Harry Potter Quiz")

# Hintergrundbild setzen
set_background(login_window, r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_pergament_edit.png")

# Foto, das als Button fungiert, hinzufügen
photo = PhotoImage(file=r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_mischief.png")  # Pfad zum Foto
photo_button = tk.Button(login_window, image=photo, command=open_quiz, borderwidth=0, highlightthickness=0,
                         relief=tk.FLAT)

photo_button.place(x=430, y=300)  # Passen Sie x und y an, um die Position des Fotos zu ändern


# Hauptfenster-Schleife starten
login_window.mainloop()