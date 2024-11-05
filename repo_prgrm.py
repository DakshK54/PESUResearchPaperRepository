import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage, filedialog
import json

class ResearchPaperApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Research Paper Repository")
        self.master.geometry("1200x600")

        try:
            icon = PhotoImage(file="D:\Daksh\Visual Studio Code\Sem-5\MiniProject_DBMS\pesu.jpg")
            self.master.iconphoto(False, icon)
        except Exception as e:
            print(f"Error loading icon: {e}")

        # Database connection
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="Research_Paper_Repository"
        )
        self.cursor = self.db.cursor()

        self.create_widgets()

    def create_widgets(self):
        # Table selection (only 'Research_papers' as an option)
        ttk.Label(self.master, text="Select Table:").pack(pady=10)
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(self.master, textvariable=self.table_var, state="readonly")
        self.table_combo['values'] = ["Research_papers"]
        self.table_combo.current(0)  # Default to 'Research_papers'
        self.table_combo.pack(pady=5)

        # Operation selection
        ttk.Label(self.master, text="Select Operation for Research Papers:").pack(pady=10)
        self.operation_var = tk.StringVar()
        ttk.Radiobutton(self.master, text="Add", variable=self.operation_var, value="add").pack()
        ttk.Radiobutton(self.master, text="Delete", variable=self.operation_var, value="delete").pack()

        # Execute button
        ttk.Button(self.master, text="Execute", command=self.execute_operation).pack(pady=20)

    def execute_operation(self):
        operation = self.operation_var.get()

        if not operation:
            messagebox.showerror("Error", "Please select an operation.")
            return

        if operation == "add":
            self.add_data()
        elif operation == "delete":
            self.delete_data()

    def add_data(self):
        add_window = tk.Toplevel(self.master)
        add_window.title("Add Research Paper")

        # Fetch columns for Research_papers table
        self.cursor.execute("DESCRIBE Research_papers")
        columns = [column[0] for column in self.cursor.fetchall()]

        entries = {}
        for column in columns:
            if column not in ['pdf_data', 'paper_id']:  # Skip pdf_data and paper_id field for entry (handled separately)
                ttk.Label(add_window, text=column).pack()
                entries[column] = ttk.Entry(add_window)
                entries[column].pack()

        # PDF upload section
        ttk.Label(add_window, text="Upload PDF:").pack()

        def select_pdf():
            file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
            if file_path:
                with open(file_path, 'rb') as file:
                    self.pdf_data = file.read()

        ttk.Button(add_window, text="Select PDF", command=select_pdf).pack()

        # Input fields for keywords, authors, and research areas
        ttk.Label(add_window, text="Enter Keywords (comma-separated):").pack()
        self.keyword_entry = ttk.Entry(add_window)
        self.keyword_entry.pack()

        ttk.Label(add_window, text="Enter Author IDs (comma-separated):").pack()
        self.author_entry = ttk.Entry(add_window)
        self.author_entry.pack()

        ttk.Label(add_window, text="Enter Research Area IDs (comma-separated):").pack()
        self.area_entry = ttk.Entry(add_window)
        self.area_entry.pack()

        ttk.Button(add_window, text="Submit", command=self.submit).pack(pady=10)

    def submit(self):
        data = {column: entry.get() for column, entry in entries.items()}

        # Prepare JSON inputs for keywords, authors, and research areas
        keywords_json = json.dumps([k.strip() for k in self.keyword_entry.get().split(",") if k.strip()])
        authors_json = json.dumps([int(a.strip()) for a in self.author_entry.get().split(",") if a.strip().isdigit()])
        areas_json = json.dumps([int(a.strip()) for a in self.area_entry.get().split(",") if a.strip().isdigit()])

        try:
            # Call stored procedure to add research paper
            query = """CALL AddResearchPaper(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (data['title'], data['abstract'], data['doi'],
                                        data['journal_name'], data['publication_year'],
                                        self.pdf_data, keywords_json, authors_json, areas_json))

            # Commit the transaction
            self.db.commit()

            # Check if any author IDs were not found in the users table
            missing_authors = [int(a) for a in authors_json.strip('[]').split(',') if a.strip().isdigit() and int(a) not in self.get_existing_author_ids()]
            if missing_authors:
                self.add_missing_authors(missing_authors)
                messagebox.showinfo("Success", "Data added successfully! Please add the missing authors.")
            else:
                messagebox.showinfo("Success", "Data added successfully!")

            add_window.destroy()
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error", f"An error occurred: {err}")

    def get_existing_author_ids(self):
        self.cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in self.cursor.fetchall()]

    def add_missing_authors(self, missing_author_ids):
        add_author_window = tk.Toplevel(self.master)
        add_author_window.title("Add Missing Authors")

        author_entries = {}
        for author_id in missing_author_ids:
            ttk.Label(add_author_window, text=f"Author ID: {author_id}").pack()

            author_data = {}
            for column in ['first_name', 'last_name', 'email', 'affiliation']:
                ttk.Label(add_author_window, text=column.replace('_', ' ').capitalize()).pack()
                author_data[column] = ttk.Entry(add_author_window)
                author_data[column].pack()

            author_entries[author_id] = author_data

        def save_authors():
            for author_id, entry_data in author_entries.items():
                first_name = entry_data['first_name'].get()
                last_name = entry_data['last_name'].get()
                email = entry_data['email'].get()
                affiliation = entry_data['affiliation'].get()
                
                try:
                    query = "INSERT INTO users (user_id, first_name, last_name, email, affiliation) VALUES (%s, %s, %s, %s, %s)"
                    self.cursor.execute(query, (author_id, first_name, last_name, email, affiliation))
                    self.db.commit()
                except mysql.connector.Error as err:
                    self.db.rollback()
                    messagebox.showerror("Error", f"An error occurred while adding author {author_id}: {err}")

            messagebox.showinfo("Success", "Missing authors added successfully!")
            add_author_window.destroy()

        ttk.Button(add_author_window, text="Save Authors", command=save_authors).pack(pady=10)

    def delete_data(self):
        delete_window = tk.Toplevel(self.master)
        delete_window.title("Delete data from Research Papers")

        # Get the primary key for Research_papers (assuming it's paper_id)
        primary_key = 'paper_id'

        ttk.Label(delete_window, text=f"Enter {primary_key} to delete:").pack()
        id_entry = ttk.Entry(delete_window)
        id_entry.pack()

        def confirm_delete():
            id_value = id_entry.get()
            if not id_value:
                messagebox.showerror("Error", "Please enter a value.")
                return

            try:
                # Check if the record exists
                self.cursor.execute(f"SELECT * FROM Research_papers WHERE {primary_key} = %s", (id_value,))
                if not self.cursor.fetchone():
                    messagebox.showinfo("Info", "No matching record found.")
                    return

                # Delete from Research_papers table
                query = f"DELETE FROM Research_papers WHERE {primary_key} = %s"
                self.cursor.execute(query, (id_value,))

                # Commit the transaction
                self.db.commit()

                messagebox.showinfo("Success", "Data deleted successfully!")
                delete_window.destroy()
            except mysql.connector.Error as err:
                self.db.rollback()
                messagebox.showerror("Error", f"An error occurred: {err}")

        ttk.Button(delete_window, text="Confirm Delete", command=confirm_delete).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ResearchPaperApp(root)
    root.mainloop()