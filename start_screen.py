import tkinter as tk
import pygame
from tkinter import PhotoImage
from utils import set_background
from quiz_screen import open_house_window
import home_screen

def open_quiz():
    play_music()  # Musik abspielen
    login_window.destroy()
    #open_house_window()
    home_screen.open_home_screen()

def play_music():
    # Musikdatei laden und abspielen
    pygame.mixer.init()  # Initialisieren des Mixers
    pygame.mixer.music.load(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\19 - Hedwig's Theme.mp3")
    pygame.mixer.music.play(-1)  # Endlosschleife: -1 bedeutet, dass die Musik unendlich oft wiederholt wird





# Hauptfenster erstellen
login_window = tk.Tk()
login_window.title("Harry Potter Quiz")

# Hintergrundbild setzen
set_background(login_window, r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_pergament_edit.png")


# Foto, das als Button fungiert, hinzufügen
photo = PhotoImage(file=r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_mischief.png")
photo_button = tk.Button(login_window, image=photo, command=open_quiz,
                         borderwidth=3,
                         relief=tk.SOLID,
                         highlightthickness=0)

photo_button.place(x=430, y=300)

photo_button.place(x=430, y=300)



# Hauptfenster-Schleife starten
login_window.mainloop()