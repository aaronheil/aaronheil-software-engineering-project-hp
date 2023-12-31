import random
import random as ran
import sqlalchemy as db
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd


# Datenbankverbindung initialisieren
engine = create_engine('sqlite:///data.db', echo=False)

# Session erstellen
Session = sessionmaker(bind=engine)
session = Session()

# Daten aus CSV-Datei laden
df = pd.read_csv('/Users/heilscan/Desktop/Software Engineering Project/hp_db_prod.csv', sep=";")
df.index.name = 'id'

# Datenbanktabelle erstellen und Daten einfügen
df.to_sql('zaubersprueche', con=engine, if_exists='replace', index=True)

def choose_quiz():
    # Pseudozufallszahl für Frageauswahl generieren
    question_id = ran.choice(df.index)

    # Frage und mögliche Antworten aus der Datenbank abrufen
    query = text(f"SELECT `Zauberspruch / Fluch`, `Wirkung` FROM zaubersprueche WHERE id = {question_id}")
    result = session.execute(query).fetchone()

    # Frage und Antworten zurückgeben
    options = [result[1]] + get_random_options(question_id)
    random.shuffle(options)
    return f"Welche Wirkung hat der Zauberspruch / Fluch \"{result[0]}\"?", options, result[1]


def get_random_options(question_id):
    # Pseudozufallszahlen für Auswahl generieren
    random_options = ran.sample(set(df.index) - {question_id}, 3)

    # Mögliche Antworten aus der Datenbank abrufen
    query = text(f"SELECT `Wirkung` FROM zaubersprueche WHERE id IN ({', '.join(map(str, random_options))})")
    results = session.execute(query).fetchall()

    # Antworten zurückgeben
    return [result[0] for result in results]


def play_quiz():
    user_score = 0
    while user_score < 4:
        question, options, correct_answer = choose_quiz()

        print(f"Frage: {question}")
        print("Antwortmöglichkeiten:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        user_answer = input("Bitte geben Sie die Nummer Ihrer Antwort ein: ")
        if options[int(user_answer) - 1] == correct_answer:
            user_score += 1
            print("Richtige Antwort!")
        else:
            print("Falsche Antwort.")

    return user_score
