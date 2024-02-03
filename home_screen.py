import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main import User, Leaderboard, get_db_session
from PIL import Image, ImageTk
from quiz_screen import start_quiz


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

    # Neuer Frame für Begrüßung und Dropdown
    top_frame = tk.Frame(home_frame, bg='#343a40')
    top_frame.pack(fill='x')

    # Benutzernamen abrufen oder erstellen
    username = get_or_create_username()

    # Inhalte zu Home Frame hinzufügen
    welcome_label = tk.Label(top_frame, text=f"Hallo {username}", font=("Arial", 30))  # Schriftgröße auf 30 gesetzt
    welcome_label.pack(padx=10, pady=10, side='left', anchor='nw')  # Links ausrichten und oben anheften

    # Button zum Ändern des Benutzernamens
    change_user_button = tk.Button(top_frame, text="Neuen User anlegen", command=lambda: change_user(welcome_label))
    change_user_button.pack(padx=10, pady=10)

    # Dropdown-Menü für die Namenseingabe und -suche
    dropdown_var = tk.StringVar()
    dropdown = ttk.Combobox(top_frame, textvariable=dropdown_var, values=get_recent_usernames())

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
    submit_button = tk.Button(top_frame, text="User auswählen", command=on_name_submit)
    submit_button.pack()

    # Container-Frame für die Buttons
    button_frame = tk.Frame(home_frame, bg='#343a40')
    button_frame.pack(expand=True)

    # Funktionen zum Laden und Skalieren der Bilder
    def load_and_resize_image(image_path, size=(300, 400)):
        original_image = Image.open(image_path)
        resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(resized_image)

    # Hausauswahl-Buttons erstellen
    image_gryffindor = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\gryffindor.png")
    btn_gryffindor = tk.Button(button_frame, image=image_gryffindor,
                               command=lambda: on_house_select('Gryffindor', current_username))

    image_slytherin = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\slytherin.png")
    btn_slytherin = tk.Button(button_frame, image=image_slytherin,
                              command=lambda: on_house_select('Slytherin', current_username))

    image_hufflepuff = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\hufflepuff.png")
    btn_hufflepuff = tk.Button(button_frame, image=image_hufflepuff,
                               command=lambda: on_house_select('Hufflepuff', current_username))

    image_ravenclaw = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\ravenclaw.png")
    btn_ravenclaw = tk.Button(button_frame, image=image_ravenclaw,
                              command=lambda: on_house_select('Ravenclaw', current_username))

    # Buttons im button_frame positionieren
    btn_gryffindor.pack(side='left', fill='both', expand=True)
    btn_slytherin.pack(side='left', fill='both', expand=True)
    btn_hufflepuff.pack(side='left', fill='both', expand=True)
    btn_ravenclaw.pack(side='left', fill='both', expand=True)

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









