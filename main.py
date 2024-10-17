import sqlite3
import random
import pyperclip
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

# Function to initialize the database and create table if it doesn't exist
def initialize_db():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS passwords
                 (id INTEGER PRIMARY KEY, username TEXT, website TEXT, password TEXT)''')
    conn.commit()
    conn.close()

# Function to generate password
def generate_password(length, strength):
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    digits = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()"
    if strength == "low":
        chars = lower
    elif strength == "medium":
        chars = upper
    elif strength == "strong":
        chars = digits
    else:
        return None
    return ''.join(random.choice(chars) for _ in range(length))

# Function to generate and display password
def generate(entry_password):
    length = var1.get()
    strength = "low" if var.get() == 1 else "medium" if var.get() == 2 else "strong"
    password = generate_password(length, strength)
    if password:
        entry_password.delete(0, END)
        entry_password.insert(0, password)

# Function to copy password to clipboard
def copy_password(entry_id):
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("SELECT password FROM passwords WHERE id=?", (entry_id,))
    password = c.fetchone()[0]
    conn.close()
    pyperclip.copy(password)

# Function to save password to database
def save_password(username, website, password):
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("INSERT INTO passwords (username, website, password) VALUES (?, ?, ?)", (username, website, password))
    conn.commit()
    conn.close()
    load_passwords()

# Function to read all passwords from database
def load_passwords():
    for i in tree.get_children():
        tree.delete(i)
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("SELECT * FROM passwords")
    rows = c.fetchall()
    for row in rows:
        tree.insert("", END, values=(row[0], row[1], row[2], '******', 'Copy', 'Edit', 'Delete'))
    conn.close()

# Function to toggle password visibility
def toggle_password_visibility(event):
    selected_item = tree.selection()[0]
    password_visible = tree.item(selected_item, 'values')[3]
    if password_visible == '******':
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        c.execute("SELECT password FROM passwords WHERE id=?", (tree.item(selected_item, 'values')[0],))
        real_password = c.fetchone()[0]
        conn.close()
        tree.item(selected_item, values=(tree.item(selected_item, 'values')[0], tree.item(selected_item, 'values')[1], tree.item(selected_item, 'values')[2], real_password, 'Copy', 'Edit', 'Delete'))
    else:
        tree.item(selected_item, values=(tree.item(selected_item, 'values')[0], tree.item(selected_item, 'values')[1], tree.item(selected_item, 'values')[2], '******', 'Copy', 'Edit', 'Delete'))

# Function to add new login details
def add_login_details():
    dialog = Toplevel(root)
    dialog.title("Add New Login Details")

    Label(dialog, text="Username").grid(row=0, column=0)
    entry_username = Entry(dialog)
    entry_username.grid(row=0, column=1)

    Label(dialog, text="Website").grid(row=1, column=0)
    entry_website = Entry(dialog)
    entry_website.grid(row=1, column=1)

    Label(dialog, text="Password").grid(row=2, column=0)
    entry_password = Entry(dialog)
    entry_password.grid(row=2, column=1)

    Label(dialog, text="Password Length").grid(row=3, column=0)
    length_spinbox = Spinbox(dialog, from_=8, to=32, textvariable=var1)
    length_spinbox.grid(row=3, column=1)

    Label(dialog, text="Password Strength").grid(row=4, column=0)
    strength_frame = Frame(dialog)
    strength_frame.grid(row=4, column=1)
    Radiobutton(strength_frame, text="Low", variable=var, value=1).pack(side=LEFT)
    Radiobutton(strength_frame, text="Medium", variable=var, value=2).pack(side=LEFT)
    Radiobutton(strength_frame, text="Strong", variable=var, value=3).pack(side=LEFT)

    Button(dialog, text="Generate", command=lambda: generate(entry_password)).grid(row=5, column=0, columnspan=2)
    Button(dialog, text="Save", command=lambda: save_password(entry_username.get(), entry_website.get(), entry_password.get()) or dialog.destroy()).grid(row=6, column=0, columnspan=2)

# Function to edit existing entry
def edit_entry(entry_id):
    dialog = Toplevel(root)
    dialog.title("Edit Login Details")

    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("SELECT * FROM passwords WHERE id=?", (entry_id,))
    row = c.fetchone()
    conn.close()

    Label(dialog, text="Username").grid(row=0, column=0)
    entry_username = Entry(dialog)
    entry_username.insert(0, row[1])
    entry_username.grid(row=0, column=1)

    Label(dialog, text="Website").grid(row=1, column=0)
    entry_website = Entry(dialog)
    entry_website.insert(0, row[2])
    entry_website.grid(row=1, column=1)

    Label(dialog, text="Password").grid(row=2, column=0)
    entry_password = Entry(dialog)
    entry_password.insert(0, row[3])
    entry_password.grid(row=2, column=1)

    Label(dialog, text="Password Length").grid(row=3, column=0)
    length_spinbox = Spinbox(dialog, from_=8, to=32, textvariable=var1)
    length_spinbox.grid(row=3, column=1)

    Label(dialog, text="Password Strength").grid(row=4, column=0)
    strength_frame = Frame(dialog)
    strength_frame.grid(row=4, column=1)
    Radiobutton(strength_frame, text="Low", variable=var, value=1).pack(side=LEFT)
    Radiobutton(strength_frame, text="Medium", variable=var, value=2).pack(side=LEFT)
    Radiobutton(strength_frame, text="Strong", variable=var, value=3).pack(side=LEFT)

    Button(dialog, text="Generate", command=lambda: generate(entry_password)).grid(row=5, column=0, columnspan=2)
    Button(dialog, text="Save", command=lambda: update_password(entry_id, entry_username.get(), entry_website.get(), entry_password.get()) or dialog.destroy()).grid(row=6, column=0, columnspan=2)

# Function to update password in database
def update_password(entry_id, username, website, password):
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute("UPDATE passwords SET username=?, website=?, password=? WHERE id=?", (username, website, password, entry_id))
    conn.commit()
    conn.close()
    load_passwords()

# Function to delete entry with confirmation
def delete_entry(entry_id):
    confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this entry?")
    if confirm:
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        c.execute("DELETE FROM passwords WHERE id=?", (entry_id,))
        conn.commit()
        conn.close()
        load_passwords()

# Initialize the database
initialize_db()

# Create the GUI
root = Tk()
var = IntVar()
var1 = IntVar(value=8)  # Set default value to 8
root.title("Python Password Manager")

# Treeview to display passwords
tree = Treeview(root, columns=("ID", "Username", "Website", "Password", "Copy", "Edit", "Delete"), show='headings')
tree.heading("ID", text="ID")
tree.heading("Username", text="Username")
tree.heading("Website", text="Website")
tree.heading("Password", text="Password")
tree.heading("Copy", text="Copy")
tree.heading("Edit", text="Edit")
tree.heading("Delete", text="Delete")
tree.column("ID", width=50)
tree.column("Username", width=150)
tree.column("Website", width=200)
tree.column("Password", width=150)
tree.column("Copy", width=50)
tree.column("Edit", width=50)
tree.column("Delete", width=50)
tree.bind("<Button-1>", toggle_password_visibility)
tree.pack(fill=BOTH, expand=1)

# Add button to add new login details
add_button = Button(root, text="Add", command=add_login_details)
add_button.pack(side=TOP, anchor=NW)

# Load passwords initially
load_passwords()

# Function to handle button clicks in the treeview
def treeview_button_click(event):
    item = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    entry_id = tree.item(item, 'values')[0]

    if column == '#5':  # Copy button
        copy_password(entry_id)
    elif column == '#6':  # Edit button
        edit_entry(entry_id)
    elif column == '#7':  # Delete button
        delete_entry(entry_id)

tree.bind("<Button-1>", treeview_button_click)

root.mainloop()