import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage, filedialog

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
            database="research_paper_repository"
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
            if column != 'pdf_data':  # Skip pdf_data field for entry (handled separately)
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

        def submit():
            data = {column: entry.get() for column, entry in entries.items() if column != 'pdf_data'}

            try:
                # Start a transaction
                self.db.start_transaction()

                # Insert into main table without the pdf_data
                columns_str = ", ".join(data.keys())
                values_str = ", ".join(["%s"] * len(data))
                query = f"INSERT INTO Research_papers ({columns_str}) VALUES ({values_str})"
                self.cursor.execute(query, tuple(data.values()))

                # Get the last inserted ID
                last_id = self.cursor.lastrowid

                # Insert the PDF data
                if hasattr(self, 'pdf_data'):
                    self.cursor.execute("UPDATE Research_papers SET pdf_data = %s WHERE paper_id = %s", (self.pdf_data, last_id))

                # Commit the transaction
                self.db.commit()
                messagebox.showinfo("Success", "Data added successfully!")
                add_window.destroy()
            except mysql.connector.Error as err:
                self.db.rollback()
                messagebox.showerror("Error", f"An error occurred: {err}")

        ttk.Button(add_window, text="Submit", command=submit).pack(pady=10)
        
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
                # Start a transaction
                self.db.start_transaction()

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

        ttk.Button(delete_window, text="Delete", command=confirm_delete).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ResearchPaperApp(root)
    root.mainloop()