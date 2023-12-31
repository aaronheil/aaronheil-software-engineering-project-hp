# utils.py
from tkinter import Canvas
from tkinter import PhotoImage
import pillow as PIL
import sys
print(sys.executable)
from PIL import Image, ImageTk


# Hier definieren Sie die Funktion set_background_image
def set_background_image(window, image_path):
    image = Image.open(image_path)
    image = image.resize((window.winfo_width(), window.winfo_height()), Image.ANTIALIAS)
    photo_image = ImageTk.PhotoImage(image)
    background_label = tk.Label(window, image=photo_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    background_label.image = photo_image  # Verhindert, dass das Bild vom Garbage Collector gelöscht wird


def set_background(window, image_path):
    window.state('zoomed')  # Maximiere das Fenster

    # Lade das Bild und skaliere es auf die Größe des Fensters
    img = Image.open(image_path)
    img = img.resize((window.winfo_screenwidth(), window.winfo_screenheight()), Image.LANCZOS)
    window.bg_image = ImageTk.PhotoImage(img)

    # Verwende ein Canvas-Widget, um das Bild zu platzieren
    canvas = Canvas(window, width=window.winfo_screenwidth(), height=window.winfo_screenheight())
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=window.bg_image)

    # Bewege das Canvas-Widget nach unten, um es unter den Anmeldebereich zu legen
    canvas.place(relx=0, rely=0, anchor="nw")

    return window.bg_image


def set_house_background(window, image_path):
    # Maximiere das Fenster
    window.state('zoomed')

    # Warte bis das Fenster aktualisiert wird, um korrekte Abmessungen zu erhalten
    window.update()

    # Lade das Bild und skaliere es auf die Größe des Fensters
    img = Image.open(image_path)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    img = img.resize((screen_width, screen_height), Image.LANCZOS)
    window.bg_image = ImageTk.PhotoImage(img)

    # Erstelle ein Canvas-Widget für das Hintergrundbild
    canvas = Canvas(window, width=screen_width, height=screen_height)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=window.bg_image)
    canvas.lower(window)  # Verschiebe das Canvas-Widget hinter das Hauptfenster

    return window.bg_image
