import sys
import mysql.connector
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt

class MugshotSearchApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("Inmate Record Search")
        self.setGeometry(100, 100, 900, 600)  # Set window size to 900x600
        self.setWindowOpacity(0.98)  # Set transparency (0 = fully transparent, 1 = fully opaque)
        
        # Layout setup
        layout = QtWidgets.QVBoxLayout(self)

        # Search inputs (with dark theme)
        self.name_input = QtWidgets.QLineEdit(self)
        self.name_input.setPlaceholderText('Search by Name')
        self.name_input.setStyleSheet("background-color: #17202a; color: #d4efdf; padding: 5px; border-radius: 5px;")
        layout.addWidget(self.name_input)

        self.reason_input = QtWidgets.QLineEdit(self)
        self.reason_input.setPlaceholderText('Search by Reason')
        self.reason_input.setStyleSheet("background-color: #17202a; color: #d4efdf; padding: 5px; border-radius: 5px;")
        layout.addWidget(self.reason_input)

        self.profile_url_input = QtWidgets.QLineEdit(self)
        self.profile_url_input.setPlaceholderText('Search by County')
        self.profile_url_input.setStyleSheet("background-color: #17202a; color: #d4efdf; padding: 5px; border-radius: 5px;")
        layout.addWidget(self.profile_url_input)

        # Search button (with dark theme)
        self.search_button = QtWidgets.QPushButton('Search', self)
        self.search_button.setStyleSheet("background-color: #17202a; color: #0a5e10; padding: 8px; border-radius: 5px;")
        self.search_button.clicked.connect(self.search_profiles)
        layout.addWidget(self.search_button)

        # Results table setup (with dark theme)
        self.results_table = QtWidgets.QTableWidget(self)
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(['ID', 'Name', 'Reason', 'County', 'Image URL'])
        # Set header text color to black and results text to green
        self.results_table.setStyleSheet("""
            QHeaderView::section {
                background-color: #17202a;
                color: #1567eb;
                font-size: 14px;
                border: 1px solid #444444;
            }
            QTableWidget {
                background-color: #17202a;
                color: #FFFFFF;
                border: 1px solid #444444;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.results_table)

        # Label to display total results
        self.results_count_label = QtWidgets.QLabel(self)
        self.results_count_label.setStyleSheet("color: #17202a; font-size: 15px; padding: 5px;")
        layout.addWidget(self.results_count_label)

        self.setLayout(layout)

    def connect_to_db(self):
        try:
            conn = mysql.connector.connect(
                host="vavps.duckdns.org",
                user="guest",
                password="password",
                database="GA_Jail_Booking"
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def search_profiles(self):
        # Get search criteria
        name = self.name_input.text()
        reason = self.reason_input.text()
        profile_url = self.profile_url_input.text()

        # Build query dynamically
        query = "SELECT * FROM mugshots WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE %s"
            params.append(f"%{name}%")
        
        if reason:
            query += " AND reason LIKE %s"
            params.append(f"%{reason}%")
        
        if profile_url:
            query += " AND profile_url LIKE %s"
            params.append(f"%{profile_url}%")

        # Execute the query
        conn = self.connect_to_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        
        # Fetch results and update table
        rows = cursor.fetchall()
        self.results_table.setRowCount(len(rows))
        self.results_count_label.setText(f"Total results: {len(rows)}")

        for row_idx, row in enumerate(rows):
            name = row[1]  # Assuming the name is in the second column (index 1)
            reason = row[3]  # Assuming the reason is in the fourth column (index 3)
            profile_url = row[4]  # Assuming profile_url is in the fifth column (index 4)
            img_url = row[2]  # Assuming image URL is in the third column (index 2)
            
            # Extract county from profile_url
            county = ""
            if isinstance(profile_url, str) and profile_url.startswith("http"):
                parts = profile_url.split("/")
                if len(parts) > 3:
                    county = parts[3]
                else:
                    county = ""
            else:
                county = profile_url

            # Check if the reason is a URL (indicating an image) or empty
            if reason and (reason.startswith('http') and any(ext in reason for ext in ['.jpg', '.png', '.jpeg', '.gif'])):
                reason = "Image URL (not a valid reason)"

            # Update the table with the data
            self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
            self.results_table.setItem(row_idx, 1, QTableWidgetItem(str(name)))
            self.results_table.setItem(row_idx, 2, QTableWidgetItem(str(county)))
            self.results_table.setItem(row_idx, 3, QTableWidgetItem(str(reason)))
            self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(img_url)))
        
        cursor.close()
        conn.close()

# To run the application
app = QtWidgets.QApplication(sys.argv)
window = MugshotSearchApp()
window.show()
sys.exit(app.exec_())
