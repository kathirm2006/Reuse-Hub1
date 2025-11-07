import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import mysql.connector
import pathlib

# -------------------------
# CONFIG
# -------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "reusehub_db"
}
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

# -------------------------
# DATABASE SETUP
# -------------------------
def get_mysql_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    conn.commit()
    cur.close()
    conn.close()

    conn = get_mysql_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            description TEXT,
            grade CHAR(1),
            price VARCHAR(50),
            certified BOOLEAN DEFAULT TRUE,
            warranty VARCHAR(50),
            image_path VARCHAR(1024),
            donor_name VARCHAR(255),
            donor_email VARCHAR(255)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kyc(
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(255),
            email VARCHAR(255),
            address TEXT,
            id_proof_path VARCHAR(1024),
            address_proof_path VARCHAR(1024),
            photo_path VARCHAR(1024),
            signature_path VARCHAR(1024)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# -------------------------
# MAIN APP
# -------------------------
class ReuseHubApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("♻️ Reuse Hub Marketplace")
        self.geometry("1280x780")
        self.minsize(1100, 720)

        self.dark_mode = False
        self.set_theme_colors()

        self.create_navbar()
        self.create_main_area()
        self.show_products()

    # -------------------------
    # Theme Colors
    # -------------------------
    def set_theme_colors(self):
        if self.dark_mode:
            self.bg = "#121212"
            self.card_bg = "#1e1e1e"
            self.fg = "#ffffff"
            self.accent = "#00b894"
        else:
            self.bg = "#f5f5f5"
            self.card_bg = "#ffffff"
            self.fg = "#000000"
            self.accent = "#00b894"

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.set_theme_colors()
        self.configure(bg=self.bg)
        self.show_products()

    # -------------------------
    # Navbar
    # -------------------------
    def create_navbar(self):
        nav = tk.Frame(self, bg=self.card_bg, relief=tk.RAISED, bd=1)
        nav.pack(fill=tk.X)

        title = tk.Label(nav, text="♻️ Reuse Hub", font=("Segoe UI", 18, "bold"), bg=self.card_bg, fg=self.accent)
        title.pack(side=tk.LEFT, padx=20, pady=8)

        buttons = [
            ("Products", self.show_products),
            ("Donate", self.show_donate_form),
            ("KYC", self.show_kyc),
            ("Contact", self.show_contact)
        ]
        for (text, cmd) in buttons:
            btn = tk.Button(nav, text=text, command=cmd, font=("Segoe UI", 11),
                            bg=self.card_bg, fg=self.fg, relief=tk.FLAT,
                            activebackground=self.accent, activeforeground="white")
            btn.pack(side=tk.LEFT, padx=10, pady=5)

        theme_btn = tk.Button(nav, text="🌙", command=self.toggle_theme,
                              bg=self.card_bg, fg=self.fg, font=("Segoe UI", 12), relief=tk.FLAT)
        theme_btn.pack(side=tk.RIGHT, padx=15)

    # -------------------------
    # Scrollable Main Area
    # -------------------------
    def create_main_area(self):
        self.container = tk.Frame(self, bg=self.bg)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.container, bg=self.bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=self.bg)
        self.canvas.create_window((0, 0), window=self.inner, anchor="n")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def clear_main_area(self):
        for w in self.inner.winfo_children():
            w.destroy()

    # -------------------------
    # PRODUCT DISPLAY
    # -------------------------
    def show_products(self):
        self.clear_main_area()
        self.inner.configure(bg=self.bg)

        conn = get_mysql_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        cur.close()
        conn.close()

        wrapper = tk.Frame(self.inner, bg=self.bg)
        wrapper.pack(expand=True, pady=30)
        title = tk.Label(wrapper, text="Available Products", font=("Segoe UI", 20, "bold"), bg=self.bg, fg=self.accent)
        title.pack(pady=15)

        grid = tk.Frame(wrapper, bg=self.bg)
        grid.pack(anchor="center")

        columns = 3
        r = c = 0
        for p in products:
            frame = tk.Frame(grid, bg=self.card_bg, bd=2, relief=tk.SOLID)
            frame.grid(row=r, column=c, padx=30, pady=30)

            img = self.get_image(p["image_path"], (340, 200))
            lbl_img = tk.Label(frame, image=img, bg=self.card_bg)
            lbl_img.image = img
            lbl_img.pack(pady=8)

            tk.Label(frame, text=p["name"], font=("Segoe UI", 13, "bold"), bg=self.card_bg, fg=self.fg).pack(pady=2)
            tk.Label(frame, text=p["description"], wraplength=320, justify="center", bg=self.card_bg, fg=self.fg).pack()
            tk.Label(frame, text=f"Grade: {p['grade']} | Warranty: {p['warranty']}", bg=self.card_bg, fg="gray").pack()
            tk.Label(frame, text=f"Price: {p['price']}", font=("Segoe UI", 13, "bold"), bg=self.card_bg, fg=self.accent).pack(pady=5)
            if p.get("donor_name"):
                tk.Label(frame, text=f"Donated by {p['donor_name']}", bg=self.card_bg, fg="gray").pack()
            else:
                tk.Label(frame, text="✅ Reuse Hub Certified", fg=self.accent, bg=self.card_bg).pack()
            tk.Label(frame, text="🔄 1 Week Free Return", fg="gray", bg=self.card_bg).pack(pady=3)

            c += 1
            if c >= columns:
                c = 0
                r += 1

    def get_image(self, path, size):
        try:
            im = Image.open(path)
            im.thumbnail(size)
        except:
            im = Image.new("RGB", size, (210, 210, 210))
        return ImageTk.PhotoImage(im)

    # -------------------------
    # DONATION FORM
    # -------------------------
    def show_donate_form(self):
        self.clear_main_area()
        wrapper = tk.Frame(self.inner, bg=self.bg)
        wrapper.pack(expand=True)

        tk.Label(wrapper, text="👐 Donate Your Product", font=("Segoe UI", 20, "bold"),
                 bg=self.bg, fg=self.accent).pack(pady=20)

        form = tk.Frame(wrapper, bg=self.bg)
        form.pack(pady=10)

        fields = ["Product Name", "Description", "Grade (A/B)", "Price", "Warranty", "Donor Name", "Donor Email"]
        entries = {}
        for field in fields:
            tk.Label(form, text=field, font=("Segoe UI", 11), bg=self.bg, fg=self.fg).pack(anchor="center", pady=2)
            e = tk.Entry(form, width=60)
            e.pack(pady=4)
            entries[field.lower()] = e

        image_path = {"path": ""}
        def choose_image():
            file = filedialog.askopenfilename(title="Select Product Image", filetypes=[("Images", "*.jpg *.png")])
            if file:
                image_path["path"] = file
                messagebox.showinfo("Image Selected", "Product image selected successfully!")

        tk.Button(form, text="Upload Product Image", command=choose_image, bg=self.accent, fg="white").pack(pady=8)

        def submit_donation():
            data = {k: v.get() for k, v in entries.items()}
            if not all(data.values()):
                messagebox.showerror("Error", "Please fill all fields.")
                return
            conn = get_mysql_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO products (name, description, grade, price, certified, warranty, image_path, donor_name, donor_email)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                data["product name"], data["description"], data["grade (a/b)"], data["price"],
                False, data["warranty"], image_path["path"], data["donor name"], data["donor email"]
            ))
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("Success", "Thank you! Your donated product has been added.")
            self.show_products()

        tk.Button(form, text="Submit Donation", bg=self.accent, fg="white", command=submit_donation).pack(pady=20)

    # -------------------------
    # KYC FORM
    # -------------------------
    def show_kyc(self):
        self.clear_main_area()
        wrapper = tk.Frame(self.inner, bg=self.bg)
        wrapper.pack(expand=True)

        tk.Label(wrapper, text="KYC Verification Form", font=("Segoe UI", 20, "bold"),
                 bg=self.bg, fg=self.accent).pack(pady=20)
        form = tk.Frame(wrapper, bg=self.bg)
        form.pack(pady=10)

        entries = {}
        for field in ["Full Name", "Email", "Address"]:
            tk.Label(form, text=field, font=("Segoe UI", 11), bg=self.bg, fg=self.fg).pack(anchor="center")
            e = tk.Entry(form, width=60)
            e.pack(pady=5)
            entries[field.lower()] = e

        upload_paths = {}
        for label in ["ID Proof", "Address Proof", "Photo", "Signature"]:
            def choose_file(lbl=label):
                file = filedialog.askopenfilename(title=f"Select {lbl}")
                upload_paths[lbl.lower().replace(" ", "_")] = file
                messagebox.showinfo("Selected", f"{lbl} selected!")

            tk.Button(form, text=f"Upload {label}", command=choose_file, bg=self.accent, fg="white").pack(pady=4)

        def submit_kyc():
            data = {k: v.get() for k, v in entries.items()}
            if not all(data.values()):
                messagebox.showerror("Error", "Please fill all fields.")
                return
            conn = get_mysql_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO kyc (full_name, email, address, id_proof_path, address_proof_path, photo_path, signature_path)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                data["full name"], data["email"], data["address"],
                upload_paths.get("id_proof", ""), upload_paths.get("address_proof", ""),
                upload_paths.get("photo", ""), upload_paths.get("signature", "")
            ))
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("Success", "KYC submitted successfully!")

        tk.Button(form, text="Submit KYC", bg=self.accent, fg="white", command=submit_kyc).pack(pady=20)

    # -------------------------
    # CONTACT INFO
    # -------------------------
    def show_contact(self):
        self.clear_main_area()
        wrapper = tk.Frame(self.inner, bg=self.bg)
        wrapper.pack(expand=True, pady=40)

        tk.Label(wrapper, text="Contact Information", font=("Segoe UI", 20, "bold"),
                 bg=self.bg, fg=self.accent).pack(pady=10)
        info = (
            "📞 7305614354 | ☎️ 044 79603993\n"
            "📧 rh1999@gmail.com\n"
            "🏠 No.01 Cross Street, Straight Road, Pallavaram, Chennai, TN 600117\n\n"
            "♻️ All products are Reuse Hub Certified\n"
            "✅ Warranty: 1–3 Years | 🔄 1 Week Free Return Policy"
        )
        tk.Label(wrapper, text=info, font=("Segoe UI", 13), bg=self.bg, fg=self.fg, justify="center").pack(pady=10)

# -------------------------
# RUN
# -------------------------
def main():
    pathlib.Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    init_db()
    app = ReuseHubApp()
    app.mainloop()

if __name__ == "__main__":
    main()