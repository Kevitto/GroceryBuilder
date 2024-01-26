import sys, re, requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from bs4 import BeautifulSoup

MEASUREMENTS = {"tbsp": ["tbsp", "tablespoon", "tablespoons", "tbsp", "tbsps"],
                "tsp": ["tsp", "teaspoon", "teaspoons", "tsp", "tsps"],
                "cup": ["cup", "cups"],
                "pint": ["pint", "pints"],
                "quart": ["quart", "quarts"],
                "gallon": ["gallon", "gallons"],
                "oz": ["oz", "ounce", "ounces"],
                "lb": ["lb", "pound", "pounds" "lbs"],
                "g": ["g", "gram", "grams"],
                "kg": ["kg", "kgs", "kilogram", "kilograms"],
                "ml": ["milliliter", "milliliters", "ml", "mls"],
                "l": ["l", "liter", "liters", "ls"]}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.setWindowTitle("Grocery Builder")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create title label and center it
        title_label = QLabel()
        title_pixmap = QPixmap("path_to_title_image.png")
        title_label.setPixmap(title_pixmap)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Create buttons layout
        buttons_layout = QHBoxLayout()

        # Create buttons
        add_recipe_button = QPushButton("Add Recipe")
        grocery_list_button = QPushButton("Grocery List")
        close_button = QPushButton("Close")

        # Add buttons to the layout
        buttons_layout.addWidget(add_recipe_button)
        buttons_layout.addWidget(grocery_list_button)
        buttons_layout.addWidget(close_button)

        # Add buttons layout to the main layout
        layout.addLayout(buttons_layout)

        # Create settings button and set it on the top right
        settings_button = QPushButton()
        settings_button.setIcon(QIcon("path_to_gear_icon.png"))
        settings_button.setFixedSize(30, 30)
        settings_button.setStyleSheet("QPushButton { border: none; }")
        settings_button.move(self.width() - settings_button.width() - 10, 10)
        self.layout().addWidget(settings_button)

        # Connect button signals to their respective functions
        add_recipe_button.clicked.connect(self.add_recipe)
        grocery_list_button.clicked.connect(self.grocery_list)
        close_button.clicked.connect(self.close)
        settings_button.clicked.connect(self.open_settings)
        self.recipe_list = {}
        self.last_recipe = None

    def add_recipe(self):
        # Create a dialog window
        self.add_recipe_dialog = QDialog(self)
        self.add_recipe_dialog.setWindowTitle("Add Recipe")
        self.add_recipe_dialog.setFixedSize(300, 100)
        self.add_recipe_dialog.setWindowFlag(Qt.FramelessWindowHint)

        # Create layout for the dialog
        layout = QVBoxLayout(self.add_recipe_dialog)

        # Create text input for URL
        url_input = QLineEdit()
        layout.addWidget(url_input)

        # Create buttons layout
        buttons_layout = QHBoxLayout()

        # Create OK button
        ok_button = QPushButton("OK")
        buttons_layout.addWidget(ok_button)

        # Create Cancel button
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(cancel_button)

        # Add buttons layout to the dialog layout
        layout.addLayout(buttons_layout)

        # Connect button signals to their respective functions
        ok_button.clicked.connect(self.parse_ingredients)
        cancel_button.clicked.connect(self.add_recipe_dialog.reject)

        # Show the dialog
        result = self.add_recipe_dialog.exec_()
        if result == QDialog.Accepted:
            print(f"{self.last_recipe} recipe added successfully.")
        else:
            print("Recipe not added.")

    def manual_recipe_name(self):
        # Create a dialog window
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("Add Recipe - Name")
        self.dialog.setFixedSize(300, 100)
        self.dialog.setWindowFlag(Qt.FramelessWindowHint)

        # Create layout for the dialog
        layout = QVBoxLayout(self.dialog)

        # Create text input for URL
        recipe_name_input = QLineEdit()
        layout.addWidget(recipe_name_input)

        # Create buttons layout
        buttons_layout = QHBoxLayout()

        # Create OK button
        ok_button = QPushButton("OK")
        buttons_layout.addWidget(ok_button)

        # Add buttons layout to the dialog layout
        layout.addLayout(buttons_layout)
        # Connect button to function
        ok_button.clicked.connect(self.dialog.accept)
        
        # Show the dialog
        result = self.dialog.exec_()
        if result == QDialog.Accepted:
            if recipe_name_input != "":
                return recipe_name_input.text()
        
        self.dialog.reject()
        
    def parse_ingredients(self):
        url = self.add_recipe_dialog.findChild(QLineEdit).text()
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find the block that looks like a title
        recipe_name = soup.find("h1").text
        if not recipe_name:
            recipe_name = self.manual_recipe_name()
        self.recipe_list[recipe_name] = []
        # Find the block that looks like an ingredient list
        regex = re.compile(".*ingredient.*")
        ingredient_block = soup.find_all("ul", {"class" : regex})  # Assuming the ingredient list is in an unordered list (ul) tag
        
        if ingredient_block:
            ingredients = ingredient_block[0].find_all("li")
            for ingredient in ingredients:
                parenthetical = re.search(r"\(.*\)", ingredient.text)
                ingredient = re.sub(r"[^a-zA-Z0-9]+", ' ', re.sub(r"\(.*\)",
                            '', ingredient.text)).lower().strip()
                ingredient = ingredient.split(" ", 2)
                unit = ""
                for measurement in MEASUREMENTS:
                    if ingredient[1] in MEASUREMENTS[measurement]:
                        unit = measurement
                        break
                if unit == "":
                    ingredient[2] = ingredient[1] + " " + ingredient[2]
                    ingredient[1] = ""
                else:
                    ingredient[1] = unit
                if not ingredient[0].isdigit():
                    ingredient[2] = ingredient[0] + " " + ingredient[2]
                    ingredient[0] = ""
                if parenthetical:
                    parenthetical = re.sub(r"[\(\)]", '', parenthetical.group(0))
                    ingredient.append(parenthetical)
                self.recipe_list[recipe_name] += [ingredient]
                
            print(self.recipe_list)
            self.last_recipe = recipe_name
            self.add_recipe_dialog.accept()
        else:
            print("Unable to parse ingredients from this URL.")
            self.recipe_list.pop(recipe_name)
            self.add_recipe_dialog.reject()

    def grocery_list(self):
        pass

    def open_settings(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
