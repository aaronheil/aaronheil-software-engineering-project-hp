import sqlite3

import pandas as pd
from tkinter import Canvas
from tkinter import PhotoImage
import sys
import pygame
print(sys.executable)
import tkinter as tk
from PIL import Image, ImageTk

def view_database():
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Abfrage der Daten
    cursor.execute("SELECT * FROM users")

    # Ausgabe der Daten in einer formatierten Tabelle
    print("ID\tUsername")
    print("-" * 20)
    for row in cursor.fetchall():
        print(f"{row[0]}\t{row[1]}")

    # Schließen der Verbindung
    conn.close()

if __name__ == "__main__":
    view_database()


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

def set_frame_background(frame, image_path):
    # Bild laden und an Frame-Größe anpassen
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((frame.winfo_width(), frame.winfo_height()), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Canvas erstellen und im Frame anordnen
    canvas = tk.Canvas(frame, width=frame.winfo_width(), height=frame.winfo_height())
    canvas.pack(fill="both", expand=True)

    # Hintergrundbild auf dem Canvas anordnen
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Speichern Sie das Bild im Canvas-Widget, um Garbage Collection zu vermeiden
    canvas.image = bg_photo




