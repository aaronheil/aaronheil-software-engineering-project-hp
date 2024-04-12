import tkinter as tk
from PIL import Image, ImageTk
from main import load_user_progress, save_user_progress


class SuccessArea:

    def __init__(self, parent_frame, username):
        self.labels_container = None
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

        # Anpassung, um sicherzustellen, dass nur zwei Zeilen erstellt werden
        for i in range(len(self.image_paths)):  # Nutze die Länge von image_paths, um die Labels zu limitieren
            row = i // 5  # Berechne die Zeile (0 oder 1)
            column = i % 5  # Berechne die Spalte (0 bis 4)
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

    def create_image_label(self, index, image):
        """Erstellt ein neues Label mit einem Bild und platziert es entsprechend seinem Index."""
        # Berechne die Position basierend auf dem Index
        row = index // 5
        column = index % 5

        label = tk.Label(self.labels_container, image=image, borderwidth=5, relief='solid')
        label.grid(row=row, column=column, padx=5, pady=5)
        label.image = image  # Speichere eine Referenz auf das Bild

        # Ersetze das alte Label in der Liste oder füge das neue hinzu
        if index < len(self.image_labels):
            self.image_labels[index] = label
        else:
            self.image_labels.append(label)

        return label

    def update_unlocked_images(self):
        self.unlocked_images = load_user_progress(self.username)
        while len(self.images) < len(self.image_labels):
            self.images.append(self.placeholder_image)

        for i in range(max(len(self.image_labels), self.unlocked_images)):
            if i < len(self.image_labels) and not self.image_labels[i].winfo_exists():
                # Das Label existiert nicht mehr; erstelle es neu
                image = self.images[i] if i < len(self.images) else self.placeholder_image
                self.create_image_label(i, image)
            elif i < len(self.image_labels):
                # Das Label existiert; aktualisiere einfach das Bild
                self.image_labels[i].config(image=self.images[i])
                self.image_labels[i].image = self.images[i]
            else:
                # Es gibt noch kein Label für diesen Index; erstelle es neu
                image = self.images[i] if i < len(self.images) else self.placeholder_image
                self.create_image_label(i, image)

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
            # Benutzernamen und Fortschritt aktualisieren
            self.username = new_username
            self.unlocked_images = load_user_progress(self.username)

            # Vorhandene Widgets im parent_frame entfernen
            for widget in self.labels_container.winfo_children():
                widget.destroy()

            # Den Container selbst neu erstellen, um sicherzustellen, dass alles zurückgesetzt wird
            self.labels_container.destroy()
            self.labels_container = tk.Frame(self.parent_frame)
            self.labels_container.pack(expand=True)

            # Bilder basierend auf dem neuen Benutzer neu laden
            self.load_and_display_images()
            print(f"Erwartete Label-Anzahl: {len(self.image_paths)}")
            print(f"Tatsächliche Label-Anzahl nach Erstellung: {len(self.labels_container.winfo_children())}")
