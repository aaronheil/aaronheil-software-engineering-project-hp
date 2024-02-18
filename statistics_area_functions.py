import variables

def show_leaderboard(tab):
    style = ttk.Style()
    style.configure('Treeview', background='#343a40', fieldbackground='#343a40',
                    foreground='white')  # Dunkelgraue Hintergrund- und weiße Textfarbe für das Leaderboard
    style.configure('Treeview.Heading', background='#343a40',
                    foreground='black')  # Dunkelgraue Hintergrundfarbe und schwarze Textfarbe für die Überschriften

    session = get_db_session()
    leaderboard_data = session.query(Leaderboard).order_by(Leaderboard.score.desc()).all()

    # Tabelle für das Leaderboard erstellen
    columns = ('user', 'house', 'score', 'played_on')
    leaderboard_table = ttk.Treeview(tab, columns=columns, show='headings')

    # Spaltenüberschriften definieren
    leaderboard_table.heading('user', text='User')
    leaderboard_table.heading('house', text='Haus')
    leaderboard_table.heading('score', text='Punktzahl')
    leaderboard_table.heading('played_on', text='Gespielt am')

    # Daten in die Tabelle einfügen
    for entry in leaderboard_data:
        user = session.query(User).filter_by(id=entry.user_id).first()
        leaderboard_table.insert('', 'end', values=(user.username, entry.house, entry.score, entry.played_on))

    # Tabelle im Tab platzieren
    leaderboard_table.pack(expand=True, fill='both')