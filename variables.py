from bots import HogwartsBot


houses = ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw"]

# Deklaration der globalen Bot-Variablen mit primären Bezug zu Bots
global global_bot_vars
global_bot_vars = {
    'houses': houses,
    'bots': {house: HogwartsBot(house_name=house) for house in houses},
    'bot_score_labels': {},



}