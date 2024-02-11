import tkinter as tk
import pygame
from tkinter import PhotoImage
from utils import set_background
#from quiz_screen import open_house_window
import selection_screen

def open_selection():
    play_music()  # Musik abspielen
    start_window.destroy()
    selection_screen.open_home_screen()

def play_music():
    # Musikdatei laden und abspielen
    pygame.mixer.init()  # Initialisieren des Mixers
    pygame.mixer.music.load(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\19 - Hedwig's Theme.mp3")
    pygame.mixer.music.play(-1)  # Endlosschleife: -1 bedeutet, dass die Musik unendlich oft wiederholt wird



# Hauptfenster erstellen
start_window = tk.Tk()
start_window.title("Harry Potter Quiz")
start_window.attributes("-fullscreen", True)
start_window.configure(bg='#343a40')  # Setzen Sie die Hintergrundfarbe auf dunkelgrau

# Größe des Fensters erhalten
start_window.update_idletasks()  # Stellt sicher, dass die Größe aktualisiert wird
window_width = start_window.winfo_screenwidth()
window_height = start_window.winfo_screenheight()

# Laden des Fotos für den Button
photo = PhotoImage(file=r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_mischief.png")



# Größe des Buttons erhalten (Breite und Höhe des Bildes)
button_width = photo.width()
button_height = photo.height()

# Berechnen Sie die Position, um den Button in der Mitte des Fensters zu platzieren
x_position = (window_width - button_width) / 2
y_position = (window_height - button_height) / 2

# Label für den Titel "Harry Potter Quiz" erstellen
quiz_label = tk.Label(start_window, text="Harry Potter Quiz", font=("Harry P", 150), bg='#343a40', fg='white')
# Label über dem Button zentrieren
quiz_label.place(x=window_width / 2, y=y_position - 100, anchor="center")

# Foto, das als Button fungiert, hinzufügen
photo_button = tk.Button(start_window, image=photo, command=open_selection,  # Stellen Sie sicher, dass open_quiz definiert ist
                         borderwidth=3,
                         relief=tk.SOLID,
                         highlightthickness=0)

# Button in der Mitte des Fensters platzieren
photo_button.place(x=x_position, y=y_position)


# Hauptfenster-Schleife starten
start_window.mainloop()