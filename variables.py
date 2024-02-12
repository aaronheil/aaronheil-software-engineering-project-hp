from bots import HogwartsBot

#Initialisierungen

houses = ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw"]
bots = {house: HogwartsBot(house_name=house) for house in houses}

# Deklaration der Bot-Variablen mit primären Bezug zu Bots

bot_vars = {
    'houses': houses,
    'bots': {house: HogwartsBot(house_name=house) for house in houses},
    'bot_score_labels': {},



}