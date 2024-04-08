import tkinter as tk
from PIL import Image, ImageTk
from main import load_user_progress, save_user_progress



class SuccessArea:
    def __init__(self, parent_frame, username):
        self.username = username
        self.unlocked_images = load_user_progress(self.username)
        self.parent_frame = parent_frame
        # Bildpfade
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
        self.target_size = (300, 400)  # Zielgröße für die Bilder (Breite, Höhe)
        self.images = []  # Zum Speichern der PhotoImage-Objekte
        self.image_labels = []  # Zum Speichern der Label-Referenzen für spätere Updates
        self.load_and_display_images()
        self.placeholder_image = None

    def create_placeholder_image(self, size):
        """Erstellt ein transparentes Bild als Platzhalter."""
        image = Image.new("RGB", size, "lightgrey")
        return ImageTk.PhotoImage(image)

    def load_and_display_images(self):
        container = tk.Frame(self.parent_frame)
        container.pack(expand=True)
        # Setze das tatsächliche Platzhalterbild
        self.placeholder_image = self.create_placeholder_image(self.target_size)

        for i in range(10):  # Angenommen, es gibt 10 Bilder
            row = i // 5
            column = i % 5
            label = tk.Label(container, image=self.placeholder_image, borderwidth=5, relief='solid')
            label.grid(row=row, column=column, padx=5, pady=5)
            self.image_labels.append(label)

        # Entsperre die entsprechenden Bilder basierend auf dem Fortschritt des Benutzers
        for i in range(self.unlocked_images):
            self.unlock_image(i)

    def unlock_image(self, index):
        """Freischalten eines Bildes basierend auf dem Index."""
        if 0 <= index < len(self.image_paths):
            image_path = self.image_paths[index]
            original_image = Image.open(image_path)
            resized_image = original_image.resize(self.target_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)

            label = self.image_labels[index]
            label.config(image=photo)
            label.image = photo

    def update_unlocked_images(self):
        self.unlocked_images = load_user_progress(self.username)
        for i in range(len(self.image_labels)):
            if i < self.unlocked_images:
                self.unlock_image(i)
            else:
                # Setze zurück zu Platzhalter, falls notwendig
                self.image_labels[i].config(image=self.placeholder_image)

