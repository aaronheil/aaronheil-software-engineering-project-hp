from bots_logic import HogwartsBot
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Basisklasse für das Datenbankmodell mittels SQLAlchemy's ORM
Base = declarative_base()

#  Benutzer-Datenbankmodell mit einer Tabelle 'users'.
# Jeder Benutzer hat eine eindeutige ID und einen Benutzernamen.

""" Enthält alle jemals angelegten User(namen) """


class User(Base):
    __tablename__ = 'users'  # Name der Tabelle in der Datenbank
    id = Column(Integer, primary_key=True)  # Eindeutige ID als Primärschlüssel
    username = Column(String)  # Benutzername als String


# Etabliert die Datenbankverbindung zur SQLite-Datenbank 'users.db'.
engine = create_engine('sqlite:///users.db')
# Erstellt alle Tabellen, die im Base-Modell definiert sind, in der Datenbank.
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
# Erstellt eine Session, um Operationen in der Datenbank durchzuführen.
every_username_session = Session()


# Definiert eine Klasse für den Anwendungszustand.
class AppState:
    def __init__(self):
        # Initialisiert Zustandsvariablen für die Anwendung.
        self.is_music_playing = True  # Steuert, ob Musik spielt.
        self.is_quiz_active = False  # Zeigt an, ob ein Quiz aktiv ist.
        self.house = ""  # Speichert das ausgewählte Haus.
        self.current_username = ""  # Hält den aktuellen Benutzernamen.


# Definiert eine Klasse für die Quiz-Konfiguration.
class QuizConfig:
    # Klassenvariablen für die Quiz-Konfiguration.
    NUM_QUESTIONS = 10  # Anzahl der Fragen im Quiz.
    NUM_OPTIONS = 4  # Anzahl der Antwortmöglichkeiten pro Frage.
    POINTS_PER_ANSWER = 10  # Punkte pro richtiger Antwort.

    def __init__(self):
        # Initialisiert Zustandsvariablen für ein spezifisches Quiz.
        self.score = 0  # Aktueller Punktestand im Quiz.
        self.question_count = 0  # Anzahl der bisher gestellten Fragen.
        self.in_tiebreaker_round = False  # Zeigt an, ob sich das Quiz in einer Entscheidungsrunde befindet.
        # UI-Elemente für das Quiz.
        self.user_score_label = None  # Label für die Anzeige des Punktestandes.
        self.result_label = None  # Label für die Anzeige, ob Antwort richtig oder falsch.
        self.bot_scores_frame = None  # Frame für die Anzeige der Bot-Punktestände.
        self.quiz_frame = None  # Haupt-Frame für das Quiz.
        self.quiz_widget_frame = None  # Frame für Quiz-Widgets.


# Definiert eine Klasse für die Bot-Konfiguration.
class BotConfig:
    def __init__(self):
        # Liste der Häuser.
        self.houses = ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw"]
        # Dictionary von Bots, eines für jedes Haus.
        self.bots = {house: HogwartsBot(house_name=house) for house in self.houses}
        # Dictionary zur Speicherung der Punktestände der Bots.
        self.bot_score_labels = {}


class HomeAreaUI:
    def __init__(self):
        self.top_frame = None
        self.button_frame = None
        self.welcome_label = None
        self.actions_button = None
        self.dropdown_list = None
        self.active_button = None
        self.home_window = None


class UserInteraction:
    def __init__(self):
        self.name_entry = None
        self.dropdown_var = None
