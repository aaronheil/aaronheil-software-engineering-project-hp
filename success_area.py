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
        # Erstelle einen neuen Frame als Container für die Labels.
        self.labels_container = tk.Frame(self.parent_frame)
        self.labels_container.pack(expand=True)

        self.placeholder_image = self.create_placeholder_image(self.target_size)

        # Verwende grid innerhalb des neuen Containers für die Labels.
        for i in range(10):  # Für jedes Bild
            row = i // 5
            column = i % 5
            label = tk.Label(self.labels_container, image=self.placeholder_image, borderwidth=5, relief='solid')
            label.grid(row=row, column=column, padx=5, pady=5)
            self.image_labels.append(label)

        # Entsperre die entsprechenden Bilder basierend auf dem Benutzerfortschritt
        for i in range(self.unlocked_images):
            self.unlock_image(i)

    def unlock_image(self, index):
        if 0 <= index < len(self.image_paths):
            image_path = self.image_paths[index]
            original_image = Image.open(image_path)
            resized_image = original_image.resize(self.target_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)

            # Aktualisiere oder füge das PhotoImage-Objekt zur images-Liste hinzu
            if index < len(self.images):
                self.images[index] = photo
            else:
                self.images.append(photo)

            if index < len(self.image_labels) and self.image_labels[index].winfo_exists():
                self.image_labels[index].config(image=self.images[index])
                self.image_labels[index].image = self.images[index]
            else:
                # Erstelle ein neues Label im labels_container, falls nötig.
                row = index // 5
                column = index % 5
                new_label = tk.Label(self.labels_container, image=photo, borderwidth=5, relief='solid')
                new_label.grid(row=row, column=column, padx=5, pady=5)
                if index < len(self.image_labels):
                    self.image_labels[index] = new_label
                else:
                    self.image_labels.append(new_label)
                new_label.image = photo

    def update_unlocked_images(self):
        self.unlocked_images = load_user_progress(self.username)
        # Stelle sicher, dass self.images mindestens so viele Elemente enthält wie self.image_labels
        while len(self.images) < len(self.image_labels):
            self.images.append(self.placeholder_image)  # Füge Platzhalterbilder hinzu, falls nötig

        for i, label in enumerate(self.image_labels):
            if label.winfo_exists():
                if i < self.unlocked_images:
                    if i < len(self.images):
                        # Aktualisiere das Bild, wenn das Label existiert, der Benutzer genügend Fortschritte gemacht hat, und der Index gültig ist
                        label.config(image=self.images[i])
                        label.image = self.images[i]
                    else:
                        print(f"Fehler: Kein Bild für Index {i} in der images Liste.")
                else:
                    label.config(image=self.placeholder_image)
                    label.image = self.placeholder_image
            else:
                print(f"Label existiert nicht mehr und kann nicht aktualisiert werden.")

    def refresh_images(self):
        # Aktualisiere self.images basierend auf dem neuen Fortschritt
        self.images.clear()
        for i in range(self.unlocked_images):
            if i < len(self.image_paths):
                image_path = self.image_paths[i]
                image = Image.open(image_path)
                photo = ImageTk.PhotoImage(image.resize(self.target_size, Image.Resampling.LANCZOS))
                self.images.append(photo)
            else:
                self.images.append(self.placeholder_image)

        # Rufe update_unlocked_images erneut auf, um die UI zu aktualisieren
        self.update_unlocked_images()

    def refresh_for_new_user(self, new_username):
        if self.username != new_username:
            self.username = new_username
            self.unlocked_images = load_user_progress(self.username)

            # Leere die images-Liste vor dem Neuladen der Bilder
            self.images.clear()

            # Zerstöre existierende Widgets im parent_frame und lade die Bilder neu
            for widget in self.parent_frame.winfo_children():
                widget.destroy()
            self.load_and_display_images()
        else:
            print(f"Kein Benutzerwechsel: {new_username} ist bereits der aktuelle Benutzer.")

