import tkinter as tk
import pygame
from tkinter import PhotoImage
from variables import AppState
from selection_screen import SelectionScreen


# Definition der Hauptklasse für den Startbildschirm der Anwendung.
class StartScreen:

    def __init__(self, master, app_state):
        self.master = master
        self.app_state = app_state
        # Titel des Fensters.
        self.master.title("Harry Potter Quiz")
        # Vollbildmodus.
        self.master.attributes("-fullscreen", True)
        # Hintergrundfarbe dunkelgrau.
        self.master.configure(bg='#343a40')
        # Benutzeroberfläche zu initialisieren.
        self.init_ui()

    # Methode zur Initialisierung der Benutzeroberfläche.
    def init_ui(self):
        # Breite und Höhe des Fensters.
        window_width = self.master.winfo_screenwidth()
        window_height = self.master.winfo_screenheight()

        # Bild, das als Button verwendet wird.
        photo = PhotoImage(file=r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_mischief.png")

        # Position des Buttons, um ihn zentriert zu platzieren.
        x_position = (window_width - photo.width()) / 2
        y_position = (window_height - photo.height()) / 2

        # Label mit dem Quiz-Titel, Platzierung oberhalb des Buttons
        quiz_label = tk.Label(self.master, text="Harry Potter Quiz", font=("Harry P", 150), bg='#343a40', fg='white')
        quiz_label.place(x=window_width / 2, y=y_position - 100, anchor="center")

        # Button mit zuvor geladenem Bild
        photo_button = tk.Button(self.master, image=photo, command=self.open_selection,
                                 borderwidth=3, relief=tk.SOLID, highlightthickness=0)
        photo_button.place(x=x_position, y=y_position)
        # Hält eine Referenz auf das Bild, um sicherzustellen, dass es angezeigt wird.
        photo_button.image = photo

    # Methode zum Abspielen der Musik.
    def play_music(self):
        # Initialisiert den Pygame-Mixer für die Audiowiedergabe.
        pygame.mixer.init()
        # Lädt die Musikdatei.
        pygame.mixer.music.load(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\19 - Hedwig's Theme.mp3")
        # Spielt die Musik in einer Endlosschleife ab.
        pygame.mixer.music.play(-1)

    # Methode, die aufgerufen wird, wenn der Button gedrückt wird.
    def open_selection(self):
        self.play_music()
        self.master.destroy()  # Schließt das aktuelle Startfenster

        # Hauptfenster für die Auswahl
        selection_window = tk.Tk()
        selection_window.attributes("-fullscreen", True)

        # Instanz der SelectionScreen-Klasse mit dem neuen Fenster
        selection_app = SelectionScreen(selection_window)

        # Tkinter-Ereignisschleife für das neue Fenster
        selection_window.mainloop()


# Hauptfunktion, die beim Starten des Skripts ausgeführt wird.

def main():
    # Hauptfenster.
    root = tk.Tk()
    root.title("Start-Fenster")
    app_state = AppState()  # AppState Instanz-Erstellung
    # Instanz der StartScreen-Klasse.
    app = StartScreen(root, app_state)
    # Startet die Tkinter-Ereignisschleife.
    root.mainloop()


# Überprüft, ob das Skript direkt ausgeführt wird und nicht importiert.
if __name__ == "__main__":
    main()
