import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main import User, Leaderboard, get_db_session
from PIL import Image, ImageTk
from quiz_screen import start_quiz
import pygame


# Globale Variable für den aktuellen Benutzernamen
current_username = ""

# Globale Variable für den Musikstatus
is_music_playing = True


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
    create_new_user_window(home_window)



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
    style.configure('Treeview', background='#343a40', fieldbackground='#343a40',
                    foreground='white')  # Dunkelgraue Hintergrund- und weiße Textfarbe für das Leaderboard
    style.configure('Treeview.Heading', background='#343a40',
                    foreground='black')  # Dunkelgraue Hintergrundfarbe und schwarze Textfarbe für die Überschriften

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

def create_new_user_window(parent):
    new_user_window = tk.Toplevel(parent)
    new_user_window.title("Neuen Benutzer anlegen")
    new_user_window.geometry("400x200")  # Größe des Fensters

    tk.Label(new_user_window, text="Bitte geben Sie den neuen Benutzernamen ein:").pack(pady=20)

    username_entry = tk.Entry(new_user_window)
    username_entry.pack()

    def submit_new_username():
        username = username_entry.get()
        if username:
            if add_username(username):  # Füge den neuen Benutzer hinzu, wenn der Name nicht leer ist
                new_user_window.destroy()
                update_ui_with_new_username(username)
            else:
                tk.messagebox.showwarning("Warnung", "Benutzername existiert bereits!")
        else:
            tk.messagebox.showwarning("Warnung", "Benutzername darf nicht leer sein!")

    submit_button = tk.Button(new_user_window, text="Submit", command=submit_new_username)
    submit_button.pack(pady=20)


def toggle_music():
    global is_music_playing
    if is_music_playing:
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()
    is_music_playing = not is_music_playing


def open_home_screen():
    global name_entry, dropdown, dropdown_var, welcome_label, current_username, active_button, home_window


    home_window = tk.Tk()
    home_window.title("Home")
    home_window.attributes("-fullscreen", True)

    # Navigation Frame für die Buttons
    nav_frame = tk.Frame(home_window, bg='#343a40')
    nav_frame.pack(side='top', fill='x')  # Oben im Hauptfenster anordnen


    # Container für Frames
    frame_container = tk.Frame(home_window)
    frame_container.pack(fill='both', expand=True, side='bottom')  # Füllt den restlichen Raum, aber unten

    # Einzelne Frames mit dunkelgrauer Hintergrundfarbe
    home_frame = tk.Frame(frame_container, bg='#343a40')
    erfolge_frame = tk.Frame(frame_container, bg='#343a40')
    statistik_frame = tk.Frame(frame_container, bg='#343a40')

    # Alle Frames im selben Raum stapeln
    for frame in [home_frame, erfolge_frame, statistik_frame]:
        frame.place(x=0, y=0, relwidth=1, relheight=1)

    # Globale Variable für den aktuell ausgewählten Button
    active_button = None

    # Neuer Frame für Begrüßung und Aktionen-Button
    top_frame = tk.Frame(home_frame, bg='#343a40')
    top_frame.pack(fill='x', pady=10)

    # Erstellen eines Containers für Aktionen-Button und Dropdown-Menü
    actions_container = tk.Frame(top_frame, bg='#343a40')
    actions_container.pack(side='left', padx=10)

    # Menubutton für Aktionen
    actions_button = tk.Menubutton(top_frame, text="Aktionen", relief=tk.RAISED, width=20)  # Breite auf 10 gesetzt
    actions_menu = tk.Menu(actions_button, tearoff=0)
    actions_button["menu"] = actions_menu

    # Funktion zum Anzeigen der Dropdown-Suchleiste
    def show_dropdown():
        # Aktualisieren Sie die Position des Buttons, bevor Sie die Koordinaten erhalten
        actions_button.update_idletasks()

        # Berechnen Sie die Position für das Dropdown-Menü, basierend auf der Position und Größe des `actions_button`
        x_position = actions_button.winfo_x() + actions_button.winfo_width()
        y_position = actions_button.winfo_y()

        # Debug-Ausgaben
        print(f"Button X: {actions_button.winfo_x()}, Button Y: {actions_button.winfo_y()}")
        print(f"Button Width: {actions_button.winfo_width()}, Button Height: {actions_button.winfo_height()}")
        print(f"Dropdown X: {x_position}, Dropdown Y: {y_position}")

        # Platzieren Sie das Dropdown-Menü rechts und direkt neben dem `actions_button`
        # `anchor="nw"` bedeutet, dass die obere linke Ecke des Dropdowns an den Koordinaten ausgerichtet wird
        dropdown.place(in_=actions_container, x=x_position, y=y_position, anchor="nw")

        # Nach der Platzierung, führen Sie eine Aktualisierung durch, um sicherzustellen, dass Änderungen angezeigt werden
        actions_container.update_idletasks()

        # Öffnen Sie das Dropdown-Menü automatisch, wenn der Benutzer auf "User auswählen" klickt
        dropdown.event_generate('<Button-1>')  # Simuliert einen Mausklick auf das Dropdown-Menü
        dropdown.focus()  # Setzt den Fokus auf das Dropdown-Menü

    # Hinzufügen der Funktionen zum Menubutton
    actions_menu.add_command(label="Neuen User anlegen", command=lambda: change_user(welcome_label))
    actions_menu.add_command(label="User auswählen", command=show_dropdown)

    actions_button.pack(side='left', fill='y')

    # Dropdown-Menü für die Namenseingabe und -suche
    dropdown_var = tk.StringVar()
    dropdown = ttk.Combobox(actions_container, textvariable=dropdown_var, values=get_recent_usernames(), width=20)
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


    # Benutzernamen abrufen oder erstellen
    username = get_or_create_username()

    # Inhalte zu Home Frame hinzufügen
    welcome_label = tk.Label(top_frame, text=f"Hallo {username}", font=("Arial", 30))
    welcome_label.pack(padx=450, pady=10, side='left', anchor='nw')

    # Musiksteuerungs-Button
    music_control_button = tk.Button(top_frame, text="Musik Ein/Aus", command=toggle_music)
    music_control_button.pack(padx=10, pady=10, side='left')  # side='left' hinzugefügt


    # Container-Frame für die Buttons
    button_frame = tk.Frame(home_frame, bg='#343a40')
    button_frame.pack(expand=True, padx=20, pady=20)

    # Funktionen zum Laden und Skalieren der Bilder
    def load_and_resize_image(image_path, size=(400, 500)):
        original_image = Image.open(image_path)
        resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(resized_image)

    # Hausauswahl-Buttons erstellen und im button_frame positionieren
    image_gryffindor = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\gryffindor.png")
    btn_gryffindor = tk.Button(button_frame, image=image_gryffindor,
                               command=lambda: on_house_select('Gryffindor', current_username))
    btn_gryffindor.pack(side='left', fill='both', expand=True, padx=200, pady=30)  # Abstand zwischen den Buttons

    image_slytherin = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\slytherin.png")
    btn_slytherin = tk.Button(button_frame, image=image_slytherin,
                              command=lambda: on_house_select('Slytherin', current_username))
    btn_slytherin.pack(side='left', fill='both', expand=True, padx=200, pady=30)  # Abstand zwischen den Buttons

    image_hufflepuff = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\hufflepuff.png")
    btn_hufflepuff = tk.Button(button_frame, image=image_hufflepuff,
                               command=lambda: on_house_select('Hufflepuff', current_username))
    btn_hufflepuff.pack(side='left', fill='both', expand=True, padx=200, pady=30)  # Abstand zwischen den Buttons

    image_ravenclaw = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\ravenclaw.png")
    btn_ravenclaw = tk.Button(button_frame, image=image_ravenclaw,
                              command=lambda: on_house_select('Ravenclaw', current_username))
    btn_ravenclaw.pack(side='left', fill='both', expand=True, padx=200, pady=30)  # Abstand zwischen den Buttons

    # Halten Sie die Bildreferenzen, um die automatische Bereinigung durch Garbage Collector zu verhindern
    button_frame.image_gryffindor = image_gryffindor
    button_frame.image_slytherin = image_slytherin
    button_frame.image_hufflepuff = image_hufflepuff
    button_frame.image_ravenclaw = image_ravenclaw


    def on_house_select(house_name, username):
        print(f"{house_name} ausgewählt, Benutzer: {username}")
        # Stellen Sie sicher, dass die Funktion start_quiz verfügbar ist und korrekt implementiert wird
        home_window.destroy()
        start_quiz(house_name, username)

    def update_active_button(new_active_button):
        global active_button
        # Setzen Sie alle Buttons auf normale Farbe zurück
        for button in [home_button, erfolge_button, statistik_button]:
            button.config(bg='SystemButtonFace')  # Setzen Sie die Standardfarbe zurück
        # Setzen Sie die Farbe des aktiven Buttons
        new_active_button.config(bg='lightgrey')  # Hervorheben des aktiven Buttons
        active_button = new_active_button


    # Funktion, um den Frame zu wechseln
    def switch_frame(frame):
        frame.tkraise()

    # Inhalte für home_frame



    # Starten Sie mit dem Anzeigen des Home-Frames
    switch_frame(home_frame)
    show_leaderboard(statistik_frame)  # Leaderboard im Tab Statistik anzeigen

    def update_active_button(new_active_button):
        global active_button
        # Setzen Sie alle Buttons auf normale Farbe zurück
        for button in [home_button, erfolge_button, statistik_button]:
            button.config(bg='SystemButtonFace')  # Setzen Sie die Standardfarbe zurück
        # Setzen Sie die Farbe des aktiven Buttons
        new_active_button.config(bg='lightgrey')  # Hervorheben des aktiven Buttons
        active_button = new_active_button

    def switch_to_home():
        switch_frame(home_frame)
        update_active_button(home_button)

    def switch_to_erfolge():
        switch_frame(erfolge_frame)
        update_active_button(erfolge_button)

    def switch_to_statistik():
        switch_frame(statistik_frame)
        update_active_button(statistik_button)

    home_button = tk.Button(nav_frame, text='⌂ Home', command=switch_to_home, font=("Harry P", 40))
    home_button.pack(side='left', fill='x', expand=True)

    erfolge_button = tk.Button(nav_frame, text='\U0001F3C6 Erfolge', command=switch_to_erfolge, font=("Harry P", 40))
    erfolge_button.pack(side='left', fill='x', expand=True)

    statistik_button = tk.Button(nav_frame, text='\U0001F4C8 Statistik', command=switch_to_statistik,
                                 font=("Harry P", 40))
    statistik_button.pack(side='left', fill='x', expand=True)

    # Setzen Sie den anfänglichen aktiven Button
    update_active_button(home_button)

    home_window.after(100, show_dropdown)  # Zeigt das Dropdown-Menü korre

    home_window.mainloop()









