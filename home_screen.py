import tkinter as tk
from tkinter import ttk
import pygame
from tkinter import PhotoImage
from utils import set_background
from quiz_screen import open_house_window

def open_home_screen():
    home_window = tk.Tk()
    home_window.title("Home")

    home_window.config(bg="#f5deb3")
    home_window.attributes("-fullscreen", True)

    # Erstellen des Notebook (Tab-Container)
    tabControl = ttk.Notebook(home_window)

    # Erstellen von Tabs
    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)

    # Hinzufügen der Tabs zum Notebook
    tabControl.add(tab1, text='Home')
    tabControl.add(tab2, text='Erfolge')

    tabControl.pack(expand=1, fill="both")

    tk.Label(tab1, text="Willkommen auf Tab 1").pack(padx=10, pady=10)
    tk.Label(tab2, text="Willkommen auf Tab 2").pack(padx=10, pady=10)

    home_window.mainloop()