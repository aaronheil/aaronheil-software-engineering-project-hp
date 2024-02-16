from bots import HogwartsBot

#Initialisierungen

is_music_playing = True
dropdown_list = None
dropdown_var = None
is_quiz_active = False
house = ""
current_username = ""
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
    'score': 0,
    'question_count': 0,
    'in_tiebreaker_round': False,
    'score_label': None,
    'result_label': None,
    'bot_scores_frame': None,
    'quiz_frame': None,
    'quiz_widget_frame': None,
    'user_score_label': None

}
