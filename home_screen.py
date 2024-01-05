import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import pygame
from tkinter import PhotoImage
from utils import set_background
from quiz_screen import open_house_window

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


def get_or_create_username():
    # Überprüfen, ob bereits ein Benutzername gespeichert ist
    user = session.query(User).first()
    if user:
        return user.username
    else:
        # Eingabeaufforderung für den Benutzernamen
        username = simpledialog.askstring("Benutzername", "Wie lautet Ihr Name?")
        if username:  # Überprüfen, ob der Benutzer tatsächlich einen Namen eingegeben hat
            new_user = User(username=username)
            session.add(new_user)
            session.commit()
            return username
        else:
            return "Unbekannter Benutzer"  # Standardname, falls kein Name eingegeben wurde

def change_user(label):
    # Funktion, um Benutzernamen zu ändern und das Label zu aktualisieren
    new_username = simpledialog.askstring("Neuer Benutzer", "Neuer Benutzername:")
    user = session.query(User).first()
    if user and new_username:
        user.username = new_username
        session.commit()
        label.config(text=f"Hallo {new_username}")

def open_home_screen():
    home_window = tk.Tk()
    home_window.title("Home")
    home_window.attributes("-fullscreen", True)

    style = ttk.Style()
    style.configure('Blue.TFrame', background='light blue')
    style.configure('Green.TFrame', background='light green')
    style.configure('Yellow.TFrame', background='light yellow')

    style.configure('TNotebook.Tab', font=('Harry P', '100'))  # Schriftart und Größe

    tabControl = ttk.Notebook(home_window)

    # Erstellen von Tabs mit spezifischer Hintergrundfarbe
    tab1 = ttk.Frame(tabControl, style='Blue.TFrame')
    tab2 = ttk.Frame(tabControl, style='Green.TFrame')
    tab3 = ttk.Frame(tabControl, style='Yellow.TFrame')

    tabControl.add(tab1, text='⌂ Home')
    tabControl.add(tab2, text='\U0001F3C6 Erfolge')
    tabControl.add(tab3, text='\U0001F4C8 Statistik ')

    tabControl.pack(expand=1, fill="both")

    # Benutzernamen abrufen oder erstellen
    username = get_or_create_username()

    # Inhalte zu Tab 1 (Home) hinzufügen
    welcome_label = tk.Label(tab1, text=f"Hallo {username}")
    welcome_label.pack(padx=10, pady=10)

    # Button zum Ändern des Benutzernamens
    change_user_button = tk.Button(tab1, text="Benutzer wechseln", command=lambda: change_user(welcome_label))
    change_user_button.pack(padx=10, pady=10)

    home_window.mainloop()

