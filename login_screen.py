import tkinter as tk
from tkinter import PhotoImage
from utils import set_background
from gui_screen import open_house_window


def open_quiz():
    # Öffnet das Quiz-Fenster
    login_window.destroy()  # Schließt das Login-Fenster
    open_house_window()  # Öffnet das Hausauswahlfenster


# Hauptfenster erstellen
login_window = tk.Tk()
login_window.title("Harry Potter Quiz")

# Hintergrundbild setzen
set_background(login_window, "/Users/heilscan/Desktop/Software Engineering Project/pictures/prod_pergament.png")

# Foto, das als Button fungiert, hinzufügen
photo = PhotoImage(file="/Users/heilscan/Desktop/Software Engineering Project/pictures/prod_mischief.png")  # Pfad zum Foto
photo_button = tk.Button(login_window, image=photo, command=open_quiz, borderwidth=0, highlightthickness=0,
                         relief=tk.FLAT)
photo_button.pack(pady=50)  # Zentriert das Foto im Fenster

# Hauptfenster-Schleife starten
login_window.mainloop()
