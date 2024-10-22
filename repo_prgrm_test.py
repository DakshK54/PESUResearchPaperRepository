import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error
class ResearchPaperApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Research Paper Repository")
        self.master.geometry("400x300")
        
        # MySQL connection
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="hello@1234",
                database="research_paper_repository"
            )
            self.cursor = self.db.cursor()
            messagebox.showinfo("Connection Status", "Database connected successfully!")
        except Error as e:
            messagebox.showerror("Connection Error", f"Error connecting to the database: {e}")
            self.master.destroy()

        self.create_widgets()

    def create_widgets(self):
        # Table selection
        ttk.Label(self.master, text="Select Table:").pack(pady=10)
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(self.master, textvariable=self.table_var)
        self.table_combo['values'] = self.get_tables()
        self.table_combo.pack(pady=5)
        self.table_combo.bind('<<ComboboxSelected>>', self.on_table_select)

        # Operation selection
        ttk.Label(self.master, text="Select Operation:").pack(pady=10)
        self.operation_var = tk.StringVar()
        ttk.Radiobutton(self.master, text="Add", variable=self.operation_var, value="add").pack()
        ttk.Radiobutton(self.master, text="Delete", variable=self.operation_var, value="delete").pack()

        # Execute button
        ttk.Button(self.master, text="Execute", command=self.execute_operation).pack(pady=20)

    def get_tables(self):
        self.cursor.execute("SHOW TABLES")
        return [table[0] for table in self.cursor.fetchall()]

    def on_table_select(self, event):
        # Placeholder for future table-specific field management
        pass

    def execute_operation(self):
        table = self.table_var.get()
        operation = self.operation_var.get()

        if not table or not operation:
            messagebox.showerror("Error", "Please select both a table and an operation.")
            return

        if operation == "add":
            self.add_data(table)
        elif operation == "delete":
            self.delete_data(table)

    def add_data(self, table):
        add_window = tk.Toplevel(self.master)
        add_window.title(f"Add data to {table}")

        self.cursor.execute(f"DESCRIBE {table}")
        columns = [column[0] for column in self.cursor.fetchall()]  # Fetch only column names

        entries = {}
        for column in columns:
            ttk.Label(add_window, text=column).pack()
            entries[column] = ttk.Entry(add_window)
            entries[column].pack()

        def submit():
            data = {column: entry.get() for column, entry in entries.items()}
            try:
                # Insert into main table
                columns_str = ", ".join(data.keys())
                values_str = ", ".join(["%s"] * len(data))
                query = f"INSERT INTO {table} ({columns_str}) VALUES ({values_str})"
                self.cursor.execute(query, tuple(data.values()))

                last_id = self.cursor.lastrowid
                # Handle foreign keys
                if table == 'Research_papers':
                    self.handle_paper_relations(last_id, data)
                elif table == 'Users':
                    self.handle_user_relations(last_id, data)

                self.db.commit()
                messagebox.showinfo("Success", "Data added successfully!")
                add_window.destroy()
            except mysql.connector.Error as err:
                self.db.rollback()
                messagebox.showerror("Error", f"An error occurred: {err}")

        ttk.Button(add_window, text="Submit", command=submit).pack(pady=10)

    def handle_paper_relations(self, paper_id, data):
        # Handle Paper_authors
        self.handle_relation('Users', 'user_id', paper_id, data.get('authors'), 'Paper_authors', 'author_id')

        # Handle Paper_keywords
        self.handle_keywords_or_areas('Paper_keywords', 'keyword', paper_id, data.get('keywords'))

        # Handle Paper_research_areas
        self.handle_relation('Research_areas', 'area_id', paper_id, data.get('research_areas'), 'Paper_research_areas', 'area_id')

    def handle_relation(self, related_table, related_key, main_id, ids, link_table, link_key):
        if ids:
            for item_id in ids.split(','):
                self.cursor.execute(f"SELECT * FROM {related_table} WHERE {related_key} = %s", (item_id.strip(),))
                if self.cursor.fetchone():
                    self.cursor.execute(f"INSERT INTO {link_table} (paper_id, {link_key}) VALUES (%s, %s)", (main_id, item_id))
                else:
                    messagebox.showwarning("Warning", f"ID {item_id} does not exist in {related_table}. Skipping.")

    def handle_keywords_or_areas(self, table, column, main_id, data_str):
        if data_str:
            for item in data_str.split(','):
                self.cursor.execute(f"INSERT INTO {table} (paper_id, {column}) VALUES (%s, %s)", (main_id, item.strip()))

    def handle_user_relations(self, user_id, data):
        access_rights = data.get('access_rights')
        if access_rights:
            for right in access_rights.split(','):
                resource_type, access_level = right.split(':')
                if resource_type in ['Paper', 'User', 'Review'] and access_level in ['Read', 'Write', 'Admin']:
                    self.cursor.execute(
                        "INSERT INTO User_access_rights (user_id, resource_type, access_level) VALUES (%s, %s, %s)",
                        (user_id, resource_type.strip(), access_level.strip()))
                else:
                    messagebox.showwarning("Warning", f"Invalid access right format: {right}. Skipping.")

    def delete_data(self, table):
        delete_window = tk.Toplevel(self.master)
        delete_window.title(f"Delete data from {table}")

        self.cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'")
        primary_key = self.cursor.fetchone()[4]  # Primary key column name

        ttk.Label(delete_window, text=f"Enter {primary_key} to delete:").pack()
        id_entry = ttk.Entry(delete_window)
        id_entry.pack()

        def confirm_delete():
            id_value = id_entry.get()
            if not id_value:
                messagebox.showerror("Error", "Please enter a value.")
                return
            try:
                self.cursor.execute(f"SELECT * FROM {table} WHERE {primary_key} = %s", (id_value,))
                if not self.cursor.fetchone():
                    messagebox.showinfo("Info", "No matching record found.")
                    return

                if table == 'Research_papers':
                    self.delete_paper_relations(id_value)
                elif table == 'Users':
                    self.delete_user_relations(id_value)

                self.cursor.execute(f"DELETE FROM {table} WHERE {primary_key} = %s", (id_value,))
                self.db.commit()
                messagebox.showinfo("Success", "Data deleted successfully!")
                delete_window.destroy()
            except mysql.connector.Error as err:
                self.db.rollback()
                messagebox.showerror("Error", f"An error occurred: {err}")

        ttk.Button(delete_window, text="Delete", command=confirm_delete).pack(pady=10)

    def delete_paper_relations(self, paper_id):
        self.cursor.execute("UPDATE Paper_reviews SET reviewer_id = NULL WHERE paper_id = %s", (paper_id,))
        self.cursor.execute("DELETE FROM Paper_authors WHERE paper_id = %s", (paper_id,))
        self.cursor.execute("DELETE FROM Paper_keywords WHERE paper_id = %s", (paper_id,))
        self.cursor.execute("DELETE FROM Paper_research_areas WHERE paper_id = %s", (paper_id,))

    def delete_user_relations(self, user_id):
        self.cursor.execute("UPDATE Paper_reviews SET paper_id = NULL WHERE reviewer_id = %s", (user_id,))
        self.cursor.execute("DELETE FROM Paper_authors WHERE author_id = %s", (user_id,))
        self.cursor.execute("DELETE FROM User_access_rights WHERE user_id = %s", (user_id,))

if __name__ == "__main__":
    root = tk.Tk()
    app = ResearchPaperApp(root)
    root.mainloop()
