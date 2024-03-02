import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import home_area_backend
from home_area_backend import UsernameManager, UserInterfaceManager, WindowManager, MusicManager
from PIL import Image, ImageTk
from variables import HomeAreaUI, AppState, User, UserInteraction, every_username_session
from main import session


class HomeAreaFrontend:
    def __init__(self, master, home_frame):
        self.master = master
        self.home_frame = home_frame
        self.active_button = None
        self.home_area_ui = HomeAreaUI()
        self.app_state = AppState()  # AppState Instanz erstellen
        self.user = User()
        self.music_manager = MusicManager(self.app_state)
        self.setup_ui()
        self.username_manger = UsernameManager(every_username_session)
        self.user_interaction = UserInteraction()
        self.ui_manager = UserInterfaceManager(dropdown_list=home_area_backend,
                                               session=home_area_backend,
                                               home_frame=self.home_frame,
                                               app_state=self.app_state,
                                               username_manager=self.username_manger,
                                               user_interaction=self.user_interaction)

        #self.current_username = self.ui_manager.get_or_create_username()



    def setup_ui(self):
        # Erstellen des Top-Frames für Begrüßung und Aktionen-Button
        self.top_frame = tk.Frame(self.home_frame, bg='#343a40')
        self.top_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        self.welcome_label = tk.Label(self.top_frame, text="Hallo", font=("Harry P", 30),
                                      relief=tk.RAISED)
        self.welcome_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

        # Aktionen-Menübutton
        self.actions_button = tk.Menubutton(self.top_frame, text="Aktionen", font=("Harry P", 30), relief=tk.RAISED,
                                            width=20)
        self.actions_menu = tk.Menu(self.actions_button, tearoff=0)
        self.actions_button["menu"] = self.actions_menu
        self.actions_button.grid(row=0, column=1, sticky='w', padx=10, pady=10)

        # Unterbuttons zum Menubutton hinzufügen
        self.actions_menu.add_command(label="Neuen User anlegen",
                                      command=lambda: self.ui_manager.create_new_user_window(self.home_frame),
                                      font=("Arial", 16), background='white', foreground='black')

        self.actions_menu.add_separator()
        self.actions_menu.add_command(label="User auswählen", command=self.show_dropdown,
                                      font=("Arial", 16),
                                      background='white', foreground='black')

        self.actions_menu.add_separator()
        self.actions_menu.add_command(label="Musik Ein / Aus", command=self.music_manager.toggle_music,
                                      font=("Arial", 16),
                                      background='white', foreground='black')

        # Button-Frame für die Auswahl der Häuser
        self.button_frame = tk.Frame(self.home_frame, bg='#343a40')
        self.button_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
        self.button_frame.grid_columnconfigure([0, 1, 2, 3], weight=1)
        self.button_frame.grid_rowconfigure(0, weight=1)

        # Funktionen zum Laden und Skalieren der Bilder
        def load_and_resize_image(image_path, size=(400, 500)):
            original_image = Image.open(image_path)
            resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(resized_image)

        # Hausauswahl-Buttons erstellen und im button_frame positionieren
        image_gryffindor = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\gryffindor.png")
        btn_gryffindor = tk.Button(self.button_frame, image=image_gryffindor,
                                   command=lambda: self.on_house_select('Gryffindor', self.current_username))
        btn_gryffindor.grid(row=0, column=0, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

        image_slytherin = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\slytherin.png")
        btn_slytherin = tk.Button(self.button_frame, image=image_slytherin,
                                  command=lambda: self.on_house_select('Slytherin', self.current_username))
        btn_slytherin.grid(row=0, column=1, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

        image_hufflepuff = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\hufflepuff.png")
        btn_hufflepuff = tk.Button(self.button_frame, image=image_hufflepuff,
                                   command=lambda: self.on_house_select('Hufflepuff', self.current_username))
        btn_hufflepuff.grid(row=0, column=2, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

        image_ravenclaw = load_and_resize_image(r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\ravenclaw.png")
        btn_ravenclaw = tk.Button(self.button_frame, image=image_ravenclaw,
                                  command=lambda: self.on_house_select('Ravenclaw', self.current_username))
        btn_ravenclaw.grid(row=0, column=3, sticky='nsew', padx=250, pady=150)  # Abstand zwischen den Buttons

        # Halten Sie die Bildreferenzen, um die automatische Bereinigung durch Garbage Collector zu verhindern
        self.button_frame.image_gryffindor = image_gryffindor
        self.button_frame.image_slytherin = image_slytherin
        self.button_frame.image_hufflepuff = image_hufflepuff
        self.button_frame.image_ravenclaw = image_ravenclaw

    def on_house_select(self, house_name):
        if not self.current_username:
            messagebox.showinfo("Fehler", "Bitte erst einen Benutzer auswählen.")
            return
        if not house_name:
            messagebox.showinfo("Fehler", "Bitte erst ein Haus auswählen.")
            return
        self.house = house_name  # Verwende self.house statt global
        print(f"{house_name} ausgewählt, Benutzer: {self.current_username}")
        # switch_frame und start_quiz müssen entsprechend angepasst werden
        """
               switch_frame(quiz_frame)
               update_active_button(quiz_button)
               start_quiz(house_name, username)
       """

    def switch_to_quiz(self):
        if self.is_quiz_active:
            messagebox.showinfo("Info", "Das Quiz läuft bereits.")
            return
        # Die Methode switch_frame muss angepasst werden, um innerhalb der Klasse zu funktionieren
        self.switch_frame("quiz")
        self.update_active_button(self.quiz_button)
        # Überprüfe, ob ein Benutzername und ein Haus ausgewählt wurden
        if self.current_username and self.house:
            # Die Methode start_quiz muss angepasst werden, um innerhalb der Klasse zu funktionieren
            self.start_quiz(self.house, self.current_username)
        else:
            messagebox.showinfo("Info", "Bitte wählen Sie einen Benutzer und ein Haus, bevor Sie das Quiz starten.")
            self.switch_to_home()  # Stellt sicher, dass auch diese Methode entsprechend angepasst ist

    def show_dropdown(self):
        self.dropdown_window = tk.Toplevel(self.master)
        self.dropdown_window.title("User auswählen")
        # Fenster zentrieren
        WindowManager.center_window(self.dropdown_window, 300, 200)

        # Suchleiste hinzufügen
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self.dropdown_window, textvariable=self.search_var)
        search_entry.pack(fill='x')
        search_entry.bind('<KeyRelease>', UserInterfaceManager.update_dropdown)

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
        self.dropdown_list.bind('<Double-1>', self.ui_manager.on_double_click)
        self.dropdown_list.bind('<Button-3>', self.ui_manager.on_right_click)
        self.dropdown_list.bind('<Return>', self.ui_manager.on_enter_pressed)

"""
# Initialisiere die Listbox mit allen Benutzernamen
#update_dropdown()



    def update_active_button(new_active_button):
        global active_button
        # Setzen Sie alle Buttons auf normale Farbe zurück
        for button in [home_button, quiz_button, erfolge_button, statistik_button]:
            button.config(bg='SystemButtonFace')  # Setzen Sie die Standardfarbe zurück
        # Setzen Sie die Farbe des aktiven Buttons
        new_active_button.config(bg='lightgrey')  # Hervorheben des aktiven Buttons
        active_button = new_active_button
"""




