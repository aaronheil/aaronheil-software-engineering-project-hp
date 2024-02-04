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

# Globale Variablen
dropdown_list = None
dropdown_var = None


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

# Hilfsfunktion, um Fenster in der Mitte des Bildschirms zu zentrieren
def center_window(window, width, height):
    # Bildschirmgröße abrufen
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Berechnen der x und y Koordinaten, um das Fenster in der Mitte des Bildschirms zu platzieren
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)

    window.geometry('%dx%d+%d+%d' % (width, height, x, y))

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
    search_term = search_var.get()  # Hole den Text aus der Suchleiste
    filtered_names = search_username(search_term)
    dropdown_list.delete(0, 'end')  # Löscht alle Einträge in der Listbox

    if not filtered_names:
        tk.messagebox.showinfo("Suche", "Kein passender Benutzername gefunden.")
    else:
        for item in filtered_names:
            dropdown_list.insert('end', item[0])


def on_dropdown_select(event):
    selected_index = dropdown_list.curselection()
    selected_name = dropdown_list.get(selected_index)
    update_ui_with_new_username(selected_name)


def on_double_click(event):
    selected_index = dropdown_list.curselection()
    selected_name = dropdown_list.get(selected_index)
    update_ui_with_new_username(selected_name)


def on_right_click(event):
    selected_indices = dropdown_list.curselection()  # Holt die Liste der ausgewählten Indizes
    if selected_indices:  # Prüfen, ob die Liste nicht leer ist
        selected_index = selected_indices[0]  # Nehmen Sie den ersten ausgewählten Index
        selected_name = dropdown_list.get(selected_index)  # Holt den Namen aus der Listbox
        if tk.messagebox.askyesno("Löschen", f"Möchten Sie '{selected_name}' löschen?"):
            user_to_delete = session.query(User).filter_by(username=selected_name).first()
            if user_to_delete:
                session.delete(user_to_delete)
                session.commit()
                update_dropdown()  # Aktualisiert die Listbox nach dem Löschen eines Benutzers
    else:
        tk.messagebox.showwarning("Warnung", "Kein Benutzer ausgewählt.")

def on_enter_pressed(event):
    selected_indices = dropdown_list.curselection()
    if selected_indices:  # Prüfen, ob die Liste nicht leer ist
        selected_index = selected_indices[0]  # Nehmen Sie den ersten ausgewählten Index
        selected_name = dropdown_list.get(selected_index)
        update_ui_with_new_username(selected_name)
    else:
        tk.messagebox.showwarning("Warnung", "Kein Benutzer ausgewählt.")


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
    center_window(new_user_window, 400, 200)

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
    actions_container.pack(pady=10)

    # Menubutton für Aktionen
    actions_button = tk.Menubutton(actions_container, text="Aktionen", font=("Arial", 20), relief=tk.RAISED, width=20)
    actions_menu = tk.Menu(actions_button, tearoff=0)
    actions_button["menu"] = actions_menu
    actions_button.pack(side='top', anchor='center')


    # Benutzernamen abrufen oder erstellen
    username = get_or_create_username()

    # Inhalte zu Home Frame hinzufügen
    welcome_label = tk.Label(top_frame, text=f"Hallo {username}", font=("Arial", 20))
    welcome_label.pack(padx=450, pady=10, side='left', anchor='nw')

    # Musiksteuerungs-Button
    music_control_button = tk.Button(top_frame, text="Musik Ein/Aus", command=toggle_music)
    music_control_button.pack(padx=10, pady=10)

    # Funktion zum Anzeigen der Dropdown-Suchleiste
    def show_dropdown():
        global dropdown_list, dropdown_var, search_var
        dropdown_window = tk.Toplevel(home_window)
        dropdown_window.title("User auswählen")
        # Fenstergröße und -position einstellen
        center_window(dropdown_window, 300, 200)

        # Suchleiste hinzufügen
        search_var = tk.StringVar()
        search_entry = tk.Entry(dropdown_window, textvariable=search_var)
        search_entry.pack(fill='x')
        search_entry.bind('<KeyRelease>', update_dropdown)

        # Erstelle einen Frame für die Listbox und Scrollbar
        listbox_frame = tk.Frame(dropdown_window)
        listbox_frame.pack(fill='both', expand=True)

        # Erstelle die Scrollbar
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')

        # Erstelle die Listbox
        dropdown_list = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=10)
        dropdown_list.pack(side='left', fill='both', expand=True)

        # Verknüpfung von Scrollbar und Listbox
        scrollbar.config(command=dropdown_list.yview)

        # Initialisiere die Listbox mit allen Benutzernamen
        update_dropdown()

        # Event-Handler für die Listbox
        dropdown_list.bind('<Double-1>', on_double_click)  # Doppelklick
        dropdown_list.bind('<Button-3>', on_right_click)  # Rechtsklick
        dropdown_list.bind('<Return>', on_enter_pressed)  # Enter-Taste

    # Hinzufügen der Funktionen zum Menubutton
    actions_menu.add_command(label="Neuen User anlegen", command=lambda: change_user(welcome_label))
    actions_menu.add_command(label="User auswählen", command=show_dropdown)

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

    home_window.mainloop()









