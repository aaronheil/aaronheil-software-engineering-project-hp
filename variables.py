from bots import HogwartsBot

#Initialisierungen

houses = ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw"]
bots = {house: HogwartsBot(house_name=house) for house in houses}

# Deklaration der Bot-Variablen
bot_items = {

    'houses': houses,
    'bots': {house: HogwartsBot(house_name=house) for house in houses},
    'bot_score_labels': {},

}

# Deklaration der Quiz-Variablen
quiz_items = {

    'NUM_QUESTIONS': 10,
    'NUM_OPTIONS': 4,
    'POINTS_PER_ANSWER': 10,

}
