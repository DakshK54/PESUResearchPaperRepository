import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox

class ResearchPaperApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Research Paper Repository")
        self.master.geometry("400x300")
        self.db = mysql.connector.connect(
            host="localhost",
            user="root", # set according to own server username
            password="1234", # set according to own server password
            database="research_paper_repository"
        )
        self.cursor = self.db.cursor()

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
        # This method can be expanded to show table-specific fields
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
        columns = [column[0] for column in self.cursor.fetchall()]  # Updated to access the first element of the tuple

        entries = {}
        for column in columns:
            ttk.Label(add_window, text=column).pack()
            entries[column] = ttk.Entry(add_window)
            entries[column].pack()

        def submit():
            data = {column: entry.get() for column, entry in entries.items()}
            
            try:
                # Start a transaction
                #self.db.start_transaction()

                # Insert into main table
                columns_str = ", ".join(data.keys())
                values_str = ", ".join(["%s"] * len(data))
                query = f"INSERT INTO {table} ({columns_str}) VALUES ({values_str})"
                self.cursor.execute(query, tuple(data.values()))

                # Get the last inserted ID
                last_id = self.cursor.lastrowid

                # Handle linked tables
                if table == 'Research_papers':
                    self.handle_paper_relations(last_id, data)
                elif table == 'Users':
                    self.handle_user_relations(last_id, data)

                # Commit the transaction
                self.db.commit()
                messagebox.showinfo("Success", "Data added successfully!")
                add_window.destroy()
            except mysql.connector.Error as err:
                self.db.rollback()
                messagebox.showerror("Error", f"An error occurred: {err}")

        ttk.Button(add_window, text="Submit", command=submit).pack(pady=10)
        
        
    def handle_paper_relations(self, paper_id, data):
        
        self.cursor.execute("SELECT * FROM Research_papers WHERE paper_id = %s", (paper_id,))
        
        if not self.cursor.fetchone():
            messagebox.showerror("Error", f"Paper with ID {paper_id} does not exist.")
            return
    
        # Handle Paper_authors
        if 'authors' in data and data['authors']:
            author_ids = [int(id.strip()) for id in data['authors'].split(',')]
            for author_id in author_ids:
                # Check if the author exists in Users
                self.cursor.execute("SELECT * FROM Users WHERE user_id = %s", (author_id,))
                if self.cursor.fetchone():
                    self.cursor.execute("INSERT INTO Paper_authors (paper_id, author_id) VALUES (%s, %s)", (paper_id, author_id))
                else:
                    messagebox.showwarning("Warning", f"Author with ID {author_id} does not exist. Skipping.")

        # Handle Paper_keywords
        if 'keywords' in data and data['keywords']:
            keywords = [keyword.strip() for keyword in data['keywords'].split(',')]
            for keyword in keywords:
                self.cursor.execute("INSERT INTO Paper_keywords (paper_id, keyword) VALUES (%s, %s)", (paper_id, keyword))

        # Handle Paper_research_areas
        if 'research_areas' in data and data['research_areas']:
            area_ids = [int(id.strip()) for id in data['research_areas'].split(',')]
            for area_id in area_ids:
                # Check if the research area exists in Research_areas
                self.cursor.execute("SELECT * FROM Research_areas WHERE area_id = %s", (area_id,))
                if self.cursor.fetchone():
                    self.cursor.execute("INSERT INTO Paper_research_areas (paper_id, area_id) VALUES (%s, %s)", (paper_id, area_id))
                else:
                    messagebox.showwarning("Warning", f"Research area with ID {area_id} does not exist. Skipping.")
        
        
    def handle_user_relations(self, user_id, data):
        # Handle User_access_rights
        if 'access_rights' in data and data['access_rights']:
            access_rights = data['access_rights'].split(',')
            for right in access_rights:
                resource_type, access_level = right.strip().split(':')
                if resource_type in ['Paper', 'User', 'Review'] and access_level in ['Read', 'Write', 'Admin']:
                    self.cursor.execute("INSERT INTO User_access_rights (user_id, resource_type, access_level) VALUES (%s, %s, %s)",
                                        (user_id, resource_type, access_level))
                else:
                    messagebox.showwarning("Warning", f"Invalid access right: {right}. Skipping.")
                    
    def delete_data(self, table):
        delete_window = tk.Toplevel(self.master)
        delete_window.title(f"Delete data from {table}")

        self.cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'")
        primary_key = self.cursor.fetchone()[4]  # Updated to access the primary key column name

        ttk.Label(delete_window, text=f"Enter {primary_key} to delete:").pack()
        id_entry = ttk.Entry(delete_window)
        id_entry.pack()

        def confirm_delete():
            id_value = id_entry.get()
            if not id_value:
                messagebox.showerror("Error", "Please enter a value.")
                return

            try:
                # Start a transaction
                #self.db.start_transaction()

                # Check if the record exists
                self.cursor.execute(f"SELECT * FROM {table} WHERE {primary_key} = %s", (id_value,))
                if not self.cursor.fetchone():
                    messagebox.showinfo("Info", "No matching record found.")
                    return

                # Handle linked tables
                if table == 'Research_papers':
                    self.delete_paper_relations(id_value)
                elif table == 'Users':
                    self.delete_user_relations(id_value)

                # Delete from main table
                query = f"DELETE FROM {table} WHERE {primary_key} = %s"
                self.cursor.execute(query, (id_value,))

                # Commit the transaction
                self.db.commit()

                messagebox.showinfo("Success", "Data deleted successfully!")
                delete_window.destroy()
            except mysql.connector.Error as err:
                self.db.rollback()
                messagebox.showerror("Error", f"An error occurred: {err}")

        ttk.Button(delete_window, text="Delete", command=confirm_delete).pack(pady=10)
    
    def delete_paper_relations(self, paper_id):
        # Set reviewer_id to NULL in Paper_reviews
        self.cursor.execute("UPDATE Paper_reviews SET reviewer_id = NULL WHERE paper_id = %s", (paper_id,))
        
        # Delete from other related tables
        self.cursor.execute("DELETE FROM Paper_authors WHERE paper_id = %s", (paper_id,))
        self.cursor.execute("DELETE FROM Paper_keywords WHERE paper_id = %s", (paper_id,))
        self.cursor.execute("DELETE FROM Paper_research_areas WHERE paper_id = %s", (paper_id,))

    def delete_user_relations(self, user_id):
        # Set paper_id to NULL in Paper_reviews
        self.cursor.execute("UPDATE Paper_reviews SET paper_id = NULL WHERE reviewer_id = %s", (user_id,))
        
        # Delete from other related tables
        self.cursor.execute("DELETE FROM Paper_authors WHERE author_id = %s", (user_id,))
        self.cursor.execute("DELETE FROM User_access_rights WHERE user_id = %s", (user_id,))

if __name__ == "__main__":
    root = tk.Tk()
    app = ResearchPaperApp(root)
    root.mainloop()
