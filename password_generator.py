import tkinter as tk
from tkinter import messagebox
import sqlite3
import string
import secrets
import qrcode
from qrcode import QRCode
from PIL.ImageTk import PhotoImage
from PIL import ImageTk
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator & Manager")
        self.root.geometry("500x600")
        self.root.config(bg="#2b2b2b")
        self.init_db()
        self.setup_ui()

    def init_db(self):
        self.conn = sqlite3.connect("password_manager.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY,
                service TEXT UNIQUE,
                password TEXT,
                created_at TIMESTAMP
            )
        """)
        self.conn.commit()

    def setup_ui(self):
        dark_bg = "#2b2b2b"
        dark_fg = "#ffffff"
        btn_bg = "#404040"
        entry_bg = "#3c3c3c"

        title = tk.Label(self.root, text="Password Generator & Manager", font=("Arial", 16, "bold"), bg=dark_bg, fg=dark_fg)
        title.pack(pady=10)

        tk.Label(self.root, text="Password Length:", bg=dark_bg, fg=dark_fg).pack()
        self.length_var = tk.IntVar(value=12)
        tk.Spinbox(self.root, from_=8, to=128, textvariable=self.length_var, width=10, bg=entry_bg, fg=dark_fg).pack()

        self.uppercase_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, text="Include Uppercase", variable=self.uppercase_var, bg=dark_bg, fg=dark_fg, selectcolor=entry_bg).pack()

        self.lowercase_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, text="Include Lowercase", variable=self.lowercase_var, bg=dark_bg, fg=dark_fg, selectcolor=entry_bg).pack()

        self.digits_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, text="Include Digits", variable=self.digits_var, bg=dark_bg, fg=dark_fg, selectcolor=entry_bg).pack()

        self.symbols_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.root, text="Include Symbols", variable=self.symbols_var, bg=dark_bg, fg=dark_fg, selectcolor=entry_bg).pack()

        tk.Button(self.root, text="Generate Password", command=self.generate_password, bg="#4CAF50", fg="white").pack(pady=10)

        tk.Label(self.root, text="Generated Password:", bg=dark_bg, fg=dark_fg).pack()
        self.password_entry = tk.Entry(self.root, width=40, show="*", bg=entry_bg, fg=dark_fg, insertbackground=dark_fg)
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Show/Hide", command=self.toggle_show, bg=btn_bg, fg=dark_fg).pack()

        tk.Label(self.root, text="Service Name:", bg=dark_bg, fg=dark_fg).pack()
        self.service_entry = tk.Entry(self.root, width=40, bg=entry_bg, fg=dark_fg, insertbackground=dark_fg)
        self.service_entry.pack(pady=5)

        tk.Button(self.root, text="Save Password", command=self.save_password, bg="#2196F3", fg="white").pack(pady=10)

        tk.Button(self.root, text="View Stored Passwords", command=self.view_passwords, bg="#9C27B0", fg="white").pack()

        tk.Button(self.root, text="Generate QR Code", command=self.show_qr, bg="#FF9800", fg="white").pack(pady=10)

        self.password_visible = False

    def generate_password(self):
        length = self.length_var.get()
        chars = ""

        if self.uppercase_var.get():
            chars += string.ascii_uppercase
        if self.lowercase_var.get():
            chars += string.ascii_lowercase
        if self.digits_var.get():
            chars += string.digits
        if self.symbols_var.get():
            chars += string.punctuation

        if not chars:
            messagebox.showerror("Error", "Select at least one character type")
            return

        password = "".join(secrets.choice(chars) for _ in range(length))
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def toggle_show(self):
        self.password_visible = not self.password_visible
        show_char = "" if self.password_visible else "*"
        self.password_entry.config(show=show_char)

    def save_password(self):
        service = self.service_entry.get()
        password = self.password_entry.get()

        if not service or not password:
            messagebox.showerror("Error", "Enter both service name and password")
            return

        try:
            self.cursor.execute("INSERT INTO passwords (service, password, created_at) VALUES (?, ?, ?)",
                              (service, password, datetime.now()))
            self.conn.commit()
            messagebox.showinfo("Success", "Password saved!")
            self.service_entry.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Service already exists")

    def view_passwords(self):
        self.cursor.execute("SELECT service, password, created_at FROM passwords")
        passwords = self.cursor.fetchall()

        if not passwords:
            messagebox.showinfo("Info", "No passwords stored")
            return

        view_window = tk.Toplevel(self.root)
        view_window.title("Stored Passwords")
        view_window.geometry("400x300")
        view_window.config(bg="#2b2b2b")

        text = tk.Text(view_window, width=50, height=15, bg="#3c3c3c", fg="#ffffff")
        text.pack(pady=10)

        for service, password, created_at in passwords:
            text.insert(tk.END, f"Service: {service}\nPassword: {password}\nCreated: {created_at}\n\n")

        text.config(state="disabled")

    def show_qr(self):
        password = self.password_entry.get()

        if not password:
            messagebox.showerror("Error", "Generate or enter a password first")
            return

        qr = qrcode.QRCode()
        qr.add_data(password)
        qr.make()

        img = qr.make_image(fill_color="black", back_color="white")
        photo = ImageTk.PhotoImage(img)

        qr_window = tk.Toplevel(self.root)
        qr_window.title("QR Code")
        qr_window.config(bg="#2b2b2b")
        label = tk.Label(qr_window, image=photo, bg="#2b2b2b")
        label.image = photo
        label.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()