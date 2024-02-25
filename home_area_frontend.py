import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import home_area_backend
from home_area_backend import UserInterfaceManager, WindowManager
from PIL import Image, ImageTk
from variables import HomeAreaUI



class HomeAreaFrontend:
    def __init__(self, master, home_frame):
        self.master = master
        self.home_frame = home_frame
        self.current_username = home_area_backend.get_or_create_username()
        self.active_button = None
        self.setup_ui()

    def setup_ui(self):
        # Erstellen des Top-Frames für Begrüßung und Aktionen-Button
        self.top_frame = tk.Frame(self.home_frame, bg='#343a40')
        self.top_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.welcome_label = tk.Label(self.top_frame, text=f"Hallo {self.current_username}", font=("Harry P", 30),
                                      relief=tk.RAISED)
        self.welcome_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

        # Aktionen-Menübutton
        self.actions_button = tk.Menubutton(self.top_frame, text="Aktionen", font=("Harry P", 30), relief=tk.RAISED,
                                            width=20)
        self.actions_menu = tk.Menu(self.actions_button, tearoff=0)
        self.actions_button["menu"] = self.actions_menu
        self.actions_button.grid(row=0, column=1, sticky='w', padx=10, pady=10)

    def show_dropdown(self):
        self.dropdown_window = tk.Toplevel(self.master)
        self.dropdown_window.title("User auswählen")
        # Fenster zentrieren
        WindowManager.center_window(self.dropdown_window, 300, 200)

        # Suchleiste hinzufügen
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self.dropdown_window, textvariable=self.search_var)
        search_entry.pack(fill='x')
        search_entry.bind('<KeyRelease>', self.update_dropdown)

        # Erstelle einen Frame für die Listbox und Scrollbar
        listbox_frame = tk.Frame(self.dropdown_window)
        listbox_frame.pack(fill='both', expand=True)

        # Erstelle die Scrollbar
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')

        # Erstelle die Listbox
        self.dropdown_list = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=10)
        self.dropdown_list.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.dropdown_list.yview)

        # Event-Handler für die Listbox
        self.dropdown_list.bind('<Double-1>', self.on_double_click)
        self.dropdown_list.bind('<Button-3>', self.on_right_click)
        self.dropdown_list.bind('<Return>', self.on_enter_pressed)



        # Initialisiere die Listbox mit allen Benutzernamen
       # update_dropdown()



    # Unterbuttons zum Menubutton hinzufügen
    actions_menu.add_command(label="Neuen User anlegen", command=lambda: change_user(welcome_label), font=("Arial", 16),
                             background='white', foreground='black')
    actions_menu.add_separator()  # Fügt eine Trennlinie hinzu
    actions_menu.add_command(label="User auswählen", command=show_dropdown, font=("Arial", 16), background='white',
                             foreground='black')
    actions_menu.add_separator()  # Fügt eine Trennlinie hinzu
    actions_menu.add_command(label="Musik Ein / Aus", command=toggle_music, font=("Arial", 16), background='white',
                             foreground='black')


    button_frame = tk.Frame(home_frame, bg='#343a40')
    button_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
    button_frame.grid_columnconfigure([0, 1, 2, 3], weight=1)
    button_frame.grid_rowconfigure(0, weight=1)

    # Funktionen zum Laden und Skalieren der Bilder
    def load_and_resize_image(image_path, size=(400, 500)):
        original_image = Image.open(image_path)
        resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(resized_image)

    # Hausauswahl-Buttons erstellen und im button_frame positionieren
    image_gryffindor = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\gryffindor.png")
    btn_gryffindor = tk.Button(button_frame, image=image_gryffindor,
                               command=lambda: on_house_select('Gryffindor', current_username))
    btn_gryffindor.grid(row=0, column=0, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

    image_slytherin = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\slytherin.png")
    btn_slytherin = tk.Button(button_frame, image=image_slytherin,
                              command=lambda: on_house_select('Slytherin', current_username))
    btn_slytherin.grid(row=0, column=1, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

    image_hufflepuff = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\hufflepuff.png")
    btn_hufflepuff = tk.Button(button_frame, image=image_hufflepuff,
                               command=lambda: on_house_select('Hufflepuff', current_username))
    btn_hufflepuff.grid(row=0, column=2, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

    image_ravenclaw = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\ravenclaw.png")
    btn_ravenclaw = tk.Button(button_frame, image=image_ravenclaw,
                              command=lambda: on_house_select('Ravenclaw', current_username))
    btn_ravenclaw.grid(row=0, column=3, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

    # Halten Sie die Bildreferenzen, um die automatische Bereinigung durch Garbage Collector zu verhindern
    button_frame.image_gryffindor = image_gryffindor
    button_frame.image_slytherin = image_slytherin
    button_frame.image_hufflepuff = image_hufflepuff
    button_frame.image_ravenclaw = image_ravenclaw

    # Anpassung der on_house_select Funktion
    def on_house_select(house_name, username):
        global house, current_username
        if not current_username:  # Überprüfen, ob der Benutzername leer ist
            messagebox.showinfo("Fehler", "Bitte erst einen Benutzer auswählen.")
            return
        if not house_name:
            messagebox.showinfo("Fehler", "Bitte erst ein Haus auswählen.")
            return
        house = house_name
        current_username = username
        print(f"{house_name} ausgewählt, Benutzer: {username}")
        switch_frame(quiz_frame)
        update_active_button(quiz_button)
        start_quiz(house_name, username)

    def update_active_button(new_active_button):
        global active_button
        # Setzen Sie alle Buttons auf normale Farbe zurück
        for button in [home_button, quiz_button, erfolge_button, statistik_button]:
            button.config(bg='SystemButtonFace')  # Setzen Sie die Standardfarbe zurück
        # Setzen Sie die Farbe des aktiven Buttons
        new_active_button.config(bg='lightgrey')  # Hervorheben des aktiven Buttons
        active_button = new_active_button




    def switch_to_quiz():
        global current_username, house, is_quiz_active
        if is_quiz_active:
            messagebox.showinfo("Info", "Das Quiz läuft bereits.")
            return
        switch_frame(quiz_frame)
        update_active_button(quiz_button)
        # Überprüfe, ob ein Benutzername und ein Haus ausgewählt wurden
        if current_username and house:
            start_quiz(frame_container, house, current_username)
        else:
            # Hinweis: Sie können hier eine Benachrichtigung anzeigen oder die Auswahl erzwingen
            messagebox.showinfo("Info", "Bitte wählen Sie einen Benutzer und ein Haus, bevor Sie das Quiz starten.")
            switch_to_home()


