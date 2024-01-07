import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PIL import Image, ImageTk


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
    new_username = simpledialog.askstring("Neuer Benutzer", "Neuer Benutzername:")
    if new_username:
        add_username(new_username)
        label.config(text=f"Hallo {new_username}")

# ... [Vorherige Funktionsdefinitionen wie is_username_existing, add_username, usw.]

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

def open_home_screen():
    global name_entry, dropdown, dropdown_var, welcome_label

    def open_house_selection():
        home_window.destroy()
        open_house_window()

    home_window = tk.Tk()
    home_window.title("Home")
    home_window.attributes("-fullscreen", True)

    # Konfigurieren des Stils für die Tabs
    style = ttk.Style()
    style.configure('TNotebook.Tab', font=('Harry P', '100'))  # Beibehalten der Schriftart und Größe

    # Laden des Hintergrundbildes
    background_image_path = r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_perg_1.png"
    bg_image = Image.open(background_image_path)
    bg_photo = ImageTk.PhotoImage(bg_image)

    tabControl = ttk.Notebook(home_window)

    # Erstellen der Tabs
    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)
    tab3 = ttk.Frame(tabControl)

    # Hintergrundbilder hinzufügen
    for tab in [tab1, tab2, tab3]:
        bg_label = tk.Label(tab, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg_photo

    tabControl.add(tab1, text='⌂ Home')
    tabControl.add(tab2, text='\U0001F3C6 Erfolge')
    tabControl.add(tab3, text='\U0001F4C8 Statistik')

    tabControl.pack(expand=1, fill="both")

    # Benutzernamen abrufen oder erstellen
    username = get_or_create_username()

    # Inhalte zu Tab 1 (Home) hinzufügen
    welcome_label = tk.Label(tab1, text=f"Hallo {username}")
    welcome_label.pack(padx=10, pady=10)

    # Button zum Ändern des Benutzernamens
    change_user_button = tk.Button(tab1, text="Neuen User anlegen", command=lambda: change_user(welcome_label))
    change_user_button.pack(padx=10, pady=10)

    # Dropdown-Menü für die Namenseingabe und -suche
    dropdown_var = tk.StringVar()
    dropdown = ttk.Combobox(tab1, textvariable=dropdown_var, values=get_recent_usernames())

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
    submit_button = tk.Button(tab1, text="User auswählen", command=on_name_submit)
    submit_button.pack()

    # Laden des Bildes und Größenänderung
    original_image = Image.open(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\prod_hogwarts_houses.png")  # Ersetzen Sie "Pfad_zum_Bild.png" mit dem tatsächlichen Pfad Ihres Bildes
    resized_image = original_image.resize((300, 300),
                                          Image.Resampling.LANCZOS)  # Ändern Sie die Größenwerte (200, 100) entsprechend Ihren Bedürfnissen
    house_selection_image = ImageTk.PhotoImage(resized_image)

    # Button zum Öffnen des Hausauswahl-Bildschirms mit dem Bild
    house_selection_button = tk.Button(tab1, image=house_selection_image, command=open_house_selection, borderwidth=3, relief="solid")
    house_selection_button.image = house_selection_image  # Dies ist notwendig, um das Bildreferenzproblem zu vermeiden
    house_selection_button.pack(padx=10, pady=10)

    home_window.mainloop()

