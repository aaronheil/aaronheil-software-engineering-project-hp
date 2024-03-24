import random
import sqlalchemy as db
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
import pandas as pd
import datetime

# Basisdeklaration für das ORM
Base = declarative_base()

# Benutzermodell
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    leaderboard_entries = relationship("Leaderboard", order_by="Leaderboard.id", back_populates="user")

# Leaderboard-Modell
class Leaderboard(Base):
    __tablename__ = 'leaderboard'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="leaderboard_entries")
    house = Column(String)
    score = Column(Float)
    played_on = Column(DateTime, default=datetime.datetime.utcnow)

# Datenbankverbindung initialisieren
engine = create_engine('sqlite:///data.db', echo=False)
Base.metadata.create_all(engine)  # Erstellt die Tabellen, wenn sie noch nicht existieren

# Session erstellen
Session = sessionmaker(bind=engine)
session = Session()

def get_db_session():
    return Session()

# Daten aus CSV-Datei laden
df = pd.read_csv(r"C:\Users\aaron\Desktop\HPQ_IU_Material\hp_db_prod.csv", sep=";")
df.index.name = 'id'

# Datenbanktabelle erstellen und Daten einfügen
df.to_sql('zaubersprueche', con=engine, if_exists='replace', index=True)

def choose_quiz():
    # Pseudozufallszahl für Frageauswahl generieren
    question_id = random.choice(df.index)

    # Frage und mögliche Antworten aus der Datenbank abrufen
    query = text(f"SELECT `Zauberspruch / Fluch`, `Wirkung` FROM zaubersprueche WHERE id = {question_id}")
    result = session.execute(query).fetchone()

    # Frage und Antworten zurückgeben
    options = [result[1]] + get_random_options(question_id)
    random.shuffle(options)
    return f"Welche Wirkung hat der Zauberspruch / Fluch \"{result[0]}\"?", options, result[1]


def get_random_options(question_id):
    # Umwandlung des 'set' in eine Liste für 'random.sample'
    random_option_ids = random.sample(list(set(df.index) - {question_id}), 3)

    # Erstellen einer parameterisierten Abfrage
    query = text("SELECT `Wirkung` FROM zaubersprueche WHERE id IN (:option1, :option2, :option3)")
    results = session.execute(query, {'option1': random_option_ids[0], 'option2': random_option_ids[1],
                                      'option3': random_option_ids[2]}).fetchall()

    # Antworten zurückgeben
    return [result[0] for result in results]
