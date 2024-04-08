import random
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
    username = Column(String, unique=True)
    leaderboard_entries = relationship("Leaderboard", back_populates="user")
    progress = relationship("UserProgress", back_populates="user", uselist=False)

# Leaderboard-Modell
class Leaderboard(Base):
    __tablename__ = 'leaderboard'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # hier handelt es sich um die PLayer_ID nicht User_ID
    user = relationship("User", back_populates="leaderboard_entries")
    house = Column(String)
    score = Column(Float)
    played_on = Column(DateTime, default=datetime.datetime.utcnow)


class UserProgress(Base):
    __tablename__ = 'user_progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    unlocked_images = Column(Integer, default=0)
    user = relationship("User", back_populates="progress")


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


def choose_quiz(asked_question_ids=None):
    if asked_question_ids is None:
        asked_question_ids = set()
    # Stelle sicher, dass bereits gestellte Fragen ausgeschlossen werden
    available_questions = set(df.index) - asked_question_ids
    question_id = random.choice(list(available_questions))

    # Frage und mögliche Antworten aus der Datenbank abrufen
    query = text(f"SELECT `Zauberspruch / Fluch`, `Wirkung` FROM zaubersprueche WHERE id = {question_id}")
    result = session.execute(query).fetchone()

    # Frage und Antworten zurückgeben
    options = [result[1]] + get_random_options(question_id)
    random.shuffle(options)

    # Gibt zusätzlich die Frage-ID zurück
    return f"Welche Wirkung hat der Zauberspruch / Fluch \"{result[0]}\"?", options, result[1], question_id


def get_random_options(question_id):
    # Umwandlung des 'set' in eine Liste für 'random.sample'
    random_option_ids = random.sample(list(set(df.index) - {question_id}), 3)

    # Erstellen einer parameterisierten Abfrage
    query = text("SELECT `Wirkung` FROM zaubersprueche WHERE id IN (:option1, :option2, :option3)")
    results = session.execute(query, {'option1': random_option_ids[0], 'option2': random_option_ids[1],
                                      'option3': random_option_ids[2]}).fetchall()

    # Antworten zurückgeben
    return [result[0] for result in results]


def save_user_progress(username, unlocked_images):
    db_session = get_db_session()  # Umbenannt, um Namenskonflikte zu vermeiden
    user = db_session.query(User).filter_by(username=username).first()

    if user:
        if user.progress:
            user.progress.unlocked_images = unlocked_images
        else:
            db_session.add(UserProgress(user_id=user.id, unlocked_images=unlocked_images))
        db_session.commit()
    else:
        print(f"Benutzer {username} nicht gefunden.")
    db_session.close()  # Schließe die Session nach Gebrauch

def load_user_progress(username):
    db_session = get_db_session()  # Umbenannt, um Namenskonflikte zu vermeiden
    user = db_session.query(User).filter_by(username=username).first()

    if user and user.progress:
        unlocked_images = user.progress.unlocked_images
    else:
        unlocked_images = 0
    db_session.close()  # Schließe die Session nach Gebrauch
    return unlocked_images


