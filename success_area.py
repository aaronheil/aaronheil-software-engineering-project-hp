import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk


class SuccessArea:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        # Definiere hier die Liste der Bildpfade
        self.image_paths = [
            r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\success_area\1_gleis_neundreiviertel.png",
            r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\success_area\2_believe.png",
            r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\success_area\3_hogwarts_express.png",
            r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\success_area\4_the_wands.png",
            r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\success_area\5_hedwig.png",
            r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\success_area\6_dobby.png",
            r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\success_area\7_hogwarts_castle.png",
            r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\success_area\8_hogwarts_houses.png",
            r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\success_area\9_peitschende_Weide.png",
            r"C:\Users\aaron\Desktop\HPQ_IU_Material\pictures\success_area\10_hp_team.png",
        ]
        self.images = []  # Zum Speichern der PhotoImage-Objekte
        self.target_size = (300, 400)  # Zielgröße für die Bilder (Breite, Höhe)
        self.load_and_display_images()

    def load_and_display_images(self):
        if len(self.image_paths) != 10:
            print("Warnung: Es wurden nicht genau 10 Bildpfade übergeben.")
            return

        # Container-Frame erstellen
        container = tk.Frame(self.parent_frame)
        container.pack(expand=True)  # Zentriere den Container im parent_frame

        # Das Grid im Container konfigurieren
        # Hinzufügen von Gewicht zu den Platzhalter-Spalten und -Reihen
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(6, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(3, weight=1)

        for i, image_path in enumerate(self.image_paths):
            row = (i // 5) + 1  # +1 verschiebt die Bilder von der obersten Randreihe weg
            column = (i % 5) + 1

            # Lade das Originalbild mit PIL und skaliere es
            original_image = Image.open(image_path)
            resized_image = original_image.resize(self.target_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)
            self.images.append(photo)

            # Bild im Container platzieren
            label = tk.Label(container, image=photo)
            label.grid(row=row, column=column, padx=5, pady=5)
