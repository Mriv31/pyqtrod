from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QApplication
import sys

class InputDialog(QDialog):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.message = message
        self.inputs = []

        # Créer une boîte de dialogue pour contenir les composants
        layout = QVBoxLayout(self)
        next_char_type = 0
        # Parcourir le message et ajouter des champs de texte pour chaque placeholder
        current_text = ""
        for char in message:
            if char == "%":
                if current_text:
                    label = QLabel(current_text, self)
                    layout.addWidget(label)
                current_text = ""
                next_char_type =1
                continue

            if next_char_type and (char == "s" or char == "d"):
                line_edit = QLineEdit(self)
                layout.addWidget(line_edit)
                self.inputs.append(line_edit)
                current_text = ""
                next_char_type = 1

                continue

            current_text += char
        if current_text:
            label = QLabel(current_text, self)
            layout.addWidget(label)

        # Ajouter les boutons OK et Annuler
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def getInputs(self):
        # Récupérer les valeurs des champs de texte
        values = []
        for line_edit in self.inputs:
            values.append(line_edit.text())
        return tuple(values)


def InputF(message, *args, **kwargs):
    dialog = InputDialog(message, *args, **kwargs)
    if dialog.exec():
        return dialog.getInputs()
    return None



