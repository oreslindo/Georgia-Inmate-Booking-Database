import sys
import mysql.connector
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt

class MugshotSearchApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("Georgia Jail Booking & Inmate Arrest Records")
        self.setGeometry(50, 50, 1200, 700)  # Larger window size
        self.setWindowOpacity(0.97)  # Slightly less transparent

        # Layout setup
        layout = QtWidgets.QVBoxLayout(self)

        # Search inputs (professional dark theme)
        self.name_input = QtWidgets.QLineEdit(self)
        self.name_input.setPlaceholderText('Search by Name')
        self.name_input.setStyleSheet("""
            background-color: #23272e;
            color: #e0e6ed;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #39424e;
            font-size: 16px;
        """)
        layout.addWidget(self.name_input)

        self.reason_input = QtWidgets.QLineEdit(self)
        self.reason_input.setPlaceholderText('Search by Reason')
        self.reason_input.setStyleSheet("""
            background-color: #23272e;
            color: #e0e6ed;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #39424e;
            font-size: 16px;
        """)
        layout.addWidget(self.reason_input)

        self.profile_url_input = QtWidgets.QLineEdit(self)
        self.profile_url_input.setPlaceholderText('Search by County')
        self.profile_url_input.setStyleSheet("""
            background-color: #23272e;
            color: #e0e6ed;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #39424e;
            font-size: 16px;
        """)
        layout.addWidget(self.profile_url_input)

        # Search button (professional dark theme)
        self.search_button = QtWidgets.QPushButton('Search', self)
        self.search_button.setStyleSheet("""
            background-color: #1a1d23;
            color: #4fd18b;
            padding: 10px 0;
            border-radius: 6px;
            border: 1px solid #39424e;
            font-size: 16px;
            font-weight: bold;
        """)
        self.search_button.clicked.connect(self.search_profiles)
        layout.addWidget(self.search_button)

        # Results table setup (professional dark theme)
        self.results_table = QtWidgets.QTableWidget(self)
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(['ID', 'Name', 'Reason', 'County', 'Image URL'])
        self.results_table.setStyleSheet("""
            QHeaderView::section {
                background-color: #23272e;
                color: #4fd18b;
                font-size: 15px;
                font-weight: bold;
                border: 1px solid #39424e;
                padding: 6px;
            }
            QTableWidget {
                background-color: #181a20;
                color: #e0e6ed;
                border: 1px solid #39424e;
                font-size: 15px;
                selection-background-color: #263445;
                selection-color: #4fd18b;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #23272e;
                border: 1px solid #39424e;
            }
        """)
        self.results_table.horizontalHeader().setDefaultSectionSize(220)  # Wider columns
        self.results_table.verticalHeader().setDefaultSectionSize(36)
        layout.addWidget(self.results_table)

        # Label to display total results
        self.results_count_label = QtWidgets.QLabel(self)
        self.results_count_label.setStyleSheet("""
            color: #181a20;
            font-size: 16px;
            padding: 8px 0 0 0;
            font-weight: bold;
        """)
        layout.addWidget(self.results_count_label)

        self.setLayout(layout)

    def connect_to_db(self):
        try:
            conn = mysql.connector.connect(
                host="vavps.duckdns.org",
                user="guest",  # Replace with your DB username
                password="guest",  # Replace with your DB password
                database="GA_Jail_Booking"  # Replace with your database name
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
            self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))  # ID
            self.results_table.setItem(row_idx, 1, QTableWidgetItem(str(name)))  # Name
            self.results_table.setItem(row_idx, 2, QTableWidgetItem(str(county)))  # County
            self.results_table.setItem(row_idx, 3, QTableWidgetItem(str(reason)))  # Reason
            self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(img_url)))  # Image URL
        
        cursor.close()
        conn.close()

# To run the application
app = QtWidgets.QApplication(sys.argv)
window = MugshotSearchApp()
window.show()
sys.exit(app.exec_())
