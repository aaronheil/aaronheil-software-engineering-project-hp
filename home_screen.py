import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main import User, Leaderboard, get_db_session
from PIL import Image, ImageTk


import pygame
from tkinter import PhotoImage
from utils import set_background
from quiz_screen import open_house_window

# Globale Variable für den aktuellen Benutzernamen
current_username = ""


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

def is_username_existing(username):
    return session.query(User).filter_by(username=username).first() is not None

def add_username(username):
    if not is_username_existing(username):
        new_user = User(username=username)
        session.add(new_user)
        session.commit()
        return True
    return False

def get_recent_usernames(limit=10):
    return [user.username for user in session.query(User.username).order_by(User.id.desc()).limit(limit)]

def search_username(search_term):
    return session.query(User.username).filter(User.username.like(f"%{search_term}%")).all()


def on_name_submit():
    username = dropdown_var.get()
    if add_username(username):
        update_ui_with_new_username(username)  # Update your UI accordingly
    else:
        tk.messagebox.showinfo("Info", "Dieser Name existiert bereits.")

def update_ui_with_new_username(username):
    global current_username
    current_username = username
    welcome_label.config(text=f"Hallo {username}")
    # Update the dropdown menu with recent usernames
    dropdown['values'] = get_recent_usernames()

def get_all_usernames():
    return session.query(User.username).all()

def get_or_create_username():
    usernames = get_all_usernames()
    if usernames:
        return usernames[-1][0]  # Letzter Benutzername
    else:
        username = simpledialog.askstring("Benutzername", "Wie lautet Ihr Name?")
        add_username(username)
        return username if username else "Unbekannter Benutzer"

def change_user(label):
    global current_username
    new_username = simpledialog.askstring("Neuer Benutzer", "Neuer Benutzername:")
    if new_username:
        add_username(new_username)
        current_username = new_username  # Aktualisieren der globalen Variable
        label.config(text=f"Hallo {new_username}")



def update_dropdown(*args):
    search_term = dropdown_var.get()
    filtered_names = search_username(search_term)
    dropdown['values'] = [name[0] for name in filtered_names]
    if not filtered_names:
        tk.messagebox.showinfo("Suche", "Kein passender Benutzername gefunden.")


def on_dropdown_select(event):
    selected_name = dropdown.get()
    update_ui_with_new_username(selected_name)

def on_double_click(event):
    selected_name = dropdown.get()
    update_ui_with_new_username(selected_name)

def on_enter_pressed(event):
    update_dropdown()  # Aktualisiert die Liste basierend auf dem eingegebenen Suchbegriff
    dropdown.event_generate('<Down>')  # Öffnet das Dropdown-Menü

    # Sie können hier noch eine zusätzliche Logik einfügen, falls erforderlich



def on_right_click(event):
    selected_name = dropdown.get()
    if tk.messagebox.askyesno("Löschen", f"Möchten Sie '{selected_name}' löschen?"):
        user_to_delete = session.query(User).filter_by(username=selected_name).first()
        if user_to_delete:
            session.delete(user_to_delete)
            session.commit()
            update_ui_with_new_username("Unbekannter Benutzer")
            dropdown['values'] = get_recent_usernames()


def show_leaderboard(tab):
    style = ttk.Style()
    style = ttk.Style()
    style.configure('Treeview', background='#343a40', fieldbackground='#343a40',
                    foreground='white')  # Dunkelgraue Hintergrund- und weiße Textfarbe für das Leaderboard
    style.configure('Treeview.Heading', background='#343a40',
                    foreground='white')  # Dunkelgraue Hintergrund- und weiße Textfarbe für die Überschriften

    session = get_db_session()
    leaderboard_data = session.query(Leaderboard).order_by(Leaderboard.score.desc()).all()

    # Tabelle für das Leaderboard erstellen
    columns = ('user', 'house', 'score', 'played_on')
    leaderboard_table = ttk.Treeview(tab, columns=columns, show='headings')

    # Spaltenüberschriften definieren
    leaderboard_table.heading('user', text='User')
    leaderboard_table.heading('house', text='Haus')
    leaderboard_table.heading('score', text='Punktzahl')
    leaderboard_table.heading('played_on', text='Gespielt am')

    # Daten in die Tabelle einfügen
    for entry in leaderboard_data:
        user = session.query(User).filter_by(id=entry.user_id).first()
        leaderboard_table.insert('', 'end', values=(user.username, entry.house, entry.score, entry.played_on))

    # Tabelle im Tab platzieren
    leaderboard_table.pack(expand=True, fill='both')



def open_home_screen():
    global name_entry, dropdown, dropdown_var, welcome_label, current_username

    def open_house_selection():
        home_window.destroy()
        open_house_window(username=current_username)  # Benutzernamen als Argument übergeben

    home_window = tk.Tk()
    home_window.title("Home")
    home_window.attributes("-fullscreen", True)

    # Container für Frames
    frame_container = tk.Frame(home_window)
    frame_container.pack(fill='both', expand=True)

    # Einzelne Frames mit dunkelgrauer Hintergrundfarbe
    home_frame = tk.Frame(frame_container, bg='#343a40')
    erfolge_frame = tk.Frame(frame_container, bg='#343a40')
    statistik_frame = tk.Frame(frame_container, bg='#343a40')

    # Alle Frames im selben Raum stapeln
    for frame in [home_frame, erfolge_frame, statistik_frame]:
        frame.place(x=0, y=0, relwidth=1, relheight=1)

    # Funktion, um den Frame zu wechseln
    def switch_frame(frame):
        frame.tkraise()

    # Inhalte für home_frame

    # Benutzernamen abrufen oder erstellen
    username = get_or_create_username()

    # Inhalte zu Home Frame hinzufügen
    welcome_label = tk.Label(home_frame, text=f"Hallo {username}", font=("Arial", 30))  # Schriftgröße auf 30 gesetzt
    welcome_label.pack(padx=10, pady=10, side='left', anchor='nw')  # Links ausrichten und oben anheften

    # Button zum Ändern des Benutzernamens
    change_user_button = tk.Button(home_frame, text="Neuen User anlegen", command=lambda: change_user(welcome_label))
    change_user_button.pack(padx=10, pady=10)

    # Dropdown-Menü für die Namenseingabe und -suche
    dropdown_var = tk.StringVar()
    dropdown = ttk.Combobox(home_frame, textvariable=dropdown_var, values=get_recent_usernames())

    # Bindet ein Ereignis, um auf Doppelklick zu reagieren
    dropdown.bind("<Double-1>", on_double_click)

    # Bindet ein Ereignis, um auf Rechtsklick zu reagieren
    dropdown.bind("<Button-3>", on_right_click)

    # Bindet die Enter-Taste, um die update_dropdown Funktion aufzurufen und das Dropdown-Menü zu öffnen
    dropdown.bind("<Return>", on_enter_pressed)

    # Bindet die Auswahl im Dropdown, um die Auswahl zu behandeln
    dropdown.bind("<<ComboboxSelected>>", on_dropdown_select)

    # Automatische Aktualisierung der Dropdown-Liste bei Textänderung
    dropdown_var.trace("w", update_dropdown)

    # Platzieren des Dropdown-Menüs im GUI
    dropdown.pack()

    # Button-Text ändern
    submit_button = tk.Button(home_frame, text="User auswählen", command=on_name_submit)
    submit_button.pack()

    # Laden des Bildes und Größenänderung
    original_image = Image.open(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_hgw_houses.png")
    resized_image = original_image.resize((300, 400), Image.Resampling.LANCZOS)
    house_selection_image = ImageTk.PhotoImage(resized_image)

    # Container-Frame für den Button
    button_frame = tk.Frame(home_frame)
    button_frame.pack(expand=True)  # Zentriert den Frame im Home Frame

    # Button zum Öffnen des Hausauswahl-Bildschirms mit dem Bild
    house_selection_button = tk.Button(button_frame, image=house_selection_image, command=open_house_selection,
                                       borderwidth=3, relief="solid")
    house_selection_button.image = house_selection_image  # Vermeiden des Bildreferenzproblems
    house_selection_button.pack()  # Button im zentrierten Frame platzieren

    # Buttons für den Wechsel zwischen Frames
    home_button = tk.Button(home_window, text='⌂ Home', command=lambda: switch_frame(home_frame))
    home_button.pack(side='left', fill='x', expand=True)

    erfolge_button = tk.Button(home_window, text='\U0001F3C6 Erfolge', command=lambda: switch_frame(erfolge_frame))
    erfolge_button.pack(side='left', fill='x', expand=True)

    statistik_button = tk.Button(home_window, text='\U0001F4C8 Statistik',
                                 command=lambda: switch_frame(statistik_frame))
    statistik_button.pack(side='left', fill='x', expand=True)

    # Starten Sie mit dem Anzeigen des Home-Frames
    switch_frame(home_frame)
    show_leaderboard(statistik_frame)  # Leaderboard im Tab Statistik anzeigen

    home_window.mainloop()









