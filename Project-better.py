import sys, os, json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QDate

DATA_FILE = "tasks.json"


class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List")
        self.resize(600, 400)
        self.tasks = []
        self._load_tasks()

        # --- Widgets ---
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Input row
        row = QHBoxLayout()
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("New task description…")
        self.input_prio = QComboBox()
        self.input_prio.addItems(["Low", "Medium", "High"])
        self.input_date = QDateEdit(QDate.currentDate())
        self.input_date.setCalendarPopup(True)
        btn_add = QPushButton("Add Task")
        btn_add.clicked.connect(self.add_task)
        row.addWidget(self.input_desc)
        row.addWidget(self.input_prio)
        row.addWidget(self.input_date)
        row.addWidget(btn_add)
        layout.addLayout(row)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Description", "Priority", "Due Date", "Status"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_done = QPushButton("Mark Done")
        btn_done.clicked.connect(self.mark_done)
        btn_del = QPushButton("Delete Task")
        btn_del.clicked.connect(self.delete_task)
        btn_row.addWidget(btn_done)
        btn_row.addWidget(btn_del)
        layout.addLayout(btn_row)

        self._refresh_table()

    def _load_tasks(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []

    def _save_tasks(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self):
        desc = self.input_desc.text().strip()
        if not desc:
            QMessageBox.warning(self, "Error", "Description cannot be blank.")
            return
        prio = self.input_prio.currentText()
        due = self.input_date.date().toString("yyyy-MM-dd")
        self.tasks.append({
            "desc": desc,
            "priority": prio,
            "due": due,
            "done": False
        })
        self.input_desc.clear()
        self._refresh_table()
        self._save_tasks()

    def _refresh_table(self):
        self.table.setRowCount(0)
        # sort by done status, then by due date then by priority
        def keyfn(t):
            due_str = t.get("due", "2100-01-01")  # default far future date
            prio = t.get("priority", "Low")
            return ( t.get("done", False),
        datetime.strptime(due_str, "%Y-%m-%d"),
        {"Low": 0, "Medium": 1, "High": 2}.get(prio, 0))
        for task in sorted(self.tasks, key=keyfn):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(task["desc"]))
            self.table.setItem(row, 1, QTableWidgetItem(task["priority"]))
            self.table.setItem(row, 2, QTableWidgetItem(task["due"]))
            status = "✅ Done" if task["done"] else "🔲 Pending"
            item = QTableWidgetItem(status)
            # gray out done tasks
            if task["done"]:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setForeground(Qt.gray)
            self.table.setItem(row, 3, item)

    def mark_done(self):
        sel = self.table.currentRow()
        if sel < 0:
            return
        # Map back to self.tasks index by matching description+due+priority
        desc = self.table.item(sel, 0).text()
        due = self.table.item(sel, 2).text()
        prio = self.table.item(sel, 1).text()
        for t in self.tasks:
            if t["desc"]==desc and t["due"]==due and t["priority"]==prio:
                t["done"] = True
                break
        self._refresh_table()
        self._save_tasks()

    def delete_task(self):
        sel = self.table.currentRow()
        if sel < 0:
            return
        desc = self.table.item(sel, 0).text()
        due = self.table.item(sel, 2).text()
        prio = self.table.item(sel, 1).text()
        self.tasks = [
            t for t in self.tasks
            if not (t["desc"]==desc and t["due"]==due and t["priority"]==prio)
        ]
        self._refresh_table()
        self._save_tasks()

    def closeEvent(self, event):
        self._save_tasks()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())

