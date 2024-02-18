import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main import choose_quiz
from main import get_db_session, Leaderboard, User
from bots import HogwartsBot
from bots import bots, update_bot_scores
import datetime
from PIL import Image, ImageTk
import pygame
import home_area_backend
import variables












def setup_quiz():
    global quiz_frame, quiz_widget_frame, is_quiz_active, score, question_count

    # Markiere das Quiz als nicht aktiv
    is_quiz_active = False

    # Setze den Score und den Fragezähler zurück
    score = 0
    question_count = 0

    # Entferne alle Widgets im quiz_frame
    for widget in quiz_frame.winfo_children():
        widget.destroy()

    # Erstelle den quiz_widget_frame neu
    quiz_widget_frame = tk.Frame(quiz_frame, bg='#343a40')
    quiz_widget_frame.pack(fill='both', expand=True)

    # Hier kannst du weitere Widgets oder Anweisungen für das Quiz hinzufügen
    print("Quiz-Setup ist bereit.")











