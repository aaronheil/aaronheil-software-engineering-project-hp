from tkinter import ttk
import main
import locale

class LeaderboardView:
    def __init__(self, tab):
        self.tab = tab
        self.leaderboard_loaded = False
        self.setup_leaderboard()

    def setup_leaderboard(self):
        if self.tab.winfo_children():
            return

        # Lokalisierung auf Deutsch
        locale.setlocale(locale.LC_TIME, 'de_DE.utf8')

        style = ttk.Style()
        style.configure('Treeview', font=('Harry P', 20), background='#343a40', fieldbackground='#343a40', foreground='white')
        # Erhöhe die Zeilenhöhe, um den vertikalen Abstand zwischen den Einträgen zu erhöhen
        style.configure('Treeview', rowheight=50)
        style.configure('Treeview.Heading', font=('Harry P', 30, 'bold'), background='#343a40', foreground='black')

        session = main.get_db_session()
        leaderboard_data = session.query(main.Leaderboard).order_by(main.Leaderboard.score.desc()).all()

        columns = ('user', 'house', 'score', 'played_on')
        self.leaderboard_table = ttk.Treeview(self.tab, columns=columns, show='headings')

        self.leaderboard_table.heading('user', text='User')
        self.leaderboard_table.heading('house', text='Haus')
        self.leaderboard_table.heading('score', text='Punktzahl')
        self.leaderboard_table.heading('played_on', text='Gespielt am')

        for entry in leaderboard_data:
            user = session.query(main.User).filter_by(id=entry.user_id).first()
            # Formatieren des Datums mit 50 Leerzeichen am Anfang
            played_on_formatted = " " * 45 + entry.played_on.strftime('%d. %B %Y')
            # Formatieren des Scores ohne "Punkte" und mit 50 Leerzeichen am Anfang
            score_formatted = " " * 50 + (f"{int(entry.score)}" if entry.score.is_integer() else f"{entry.score}")
            # Einfügen der formatierten Werte mit zusätzlichen Leerzeichen am Anfang für Username und Haus
            self.leaderboard_table.insert('', 'end',
                                          values=(" " * 50 + user.username, " " * 50 + entry.house, score_formatted,
                                                  played_on_formatted))

        self.leaderboard_table.pack(expand=True, fill='both')
        self.leaderboard_loaded = True

