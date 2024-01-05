import tkinter as tk
from tkinter import ttk
import pygame
from tkinter import PhotoImage
from utils import set_background
from quiz_screen import open_house_window


def open_home_screen():
    home_window = tk.Tk()
    home_window.title("Home")
    home_window.attributes("-fullscreen", True)

    style = ttk.Style()
    style.configure('Blue.TFrame', background='light blue')
    style.configure('Green.TFrame', background='light green')
    style.configure('Yellow.TFrame', background='light yellow')

    style = ttk.Style()
    style.configure('TNotebook.Tab', font=('Harry P', '100'))  # Schriftart und Größe

    tabControl = ttk.Notebook(home_window)

    # Erstellen von Tabs mit spezifischer Hintergrundfarbe
    tab1 = ttk.Frame(tabControl, style='Blue.TFrame')
    tabControl.add(tab1, text='⌂ Home')

    tab2 = ttk.Frame(tabControl, style='Green.TFrame')
    tabControl.add(tab2, text='\U0001F3C6 Erfolge')

    tab3 = ttk.Frame(tabControl, style='Yellow.TFrame')
    tabControl.add(tab3, text='\U0001F4C8 Statistik ')

    tabControl.pack(expand=1, fill="both")

    # Inhalte zu den Tabs hinzufügen
    tk.Label(tab1, text="Willkommen auf Tab 1").pack(padx=10, pady=10)
    tk.Label(tab2, text="Willkommen auf Tab 2").pack(padx=10, pady=10)
    tk.Label(tab3, text="Willkommen auf Tab 3").pack(padx=10, pady=10)

    home_window.mainloop()

