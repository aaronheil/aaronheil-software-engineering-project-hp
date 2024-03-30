import random


# Definieren Sie eine Konstante für die Punktzahl pro richtiger Antwort
POINTS_PER_ANSWER = 10


class HogwartsBot:
    def __init__(self, house_name):
        self.house_name = house_name
        self.score = 0

    def choose_answer(self, options):
        # Wählt zufällig eine Antwort aus den verfügbaren Optionen.
        return random.choice(options)

    def update_score(self, is_correct):
        """ Aktualisiert den Punktestand des Bots. """
        if is_correct:
            self.score += POINTS_PER_ANSWER

    def reset_bot_scores(self):
        """Setzt den Punktestand der Bots zurück."""
        self.score = 0


# Bots für jedes Haus
bots = {
    'Gryffindor': HogwartsBot('Gryffindor'),
    'Slytherin': HogwartsBot('Slytherin'),
    'Ravenclaw': HogwartsBot('Ravenclaw'),
    'Hufflepuff': HogwartsBot('Hufflepuff')
}



