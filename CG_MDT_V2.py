import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

INFRACTIONS = {
    "ALPHA 0.1": ("Clone Trooper E3 and below refuses to post after 3 warnings.", 3, 120),
    "ALPHA 0.2": ("Clone Trooper random killing.", 2, 300),
    "ALPHA 0.3": ("Clone Trooper team killing.", 1, 150),
    "ALPHA 0.4": ("Clone Trooper disrupting divisional events.", 3, 100),
    "ALPHA 0.5": ("Clone Trooper disrupting official TGR events.", 3, 150),
    "ALPHA 0.6": ("Clone Trooper enters a restricted area.", 3, 200),
    "ALPHA 0.7": ("Arrest on Sight (No Jail if at TGR Event).", 0, 300),
    "ALPHA 0.8": ("Hosting a fake event. Report to R&A.", 1, 300),
    "ALPHA 0.9": ("Sexual comments/actions. Report after 5 jails.", 0, 300),
    "ALPHA 1.0": ("Toxicity toward others.", 3, 200),
    "ALPHA 1.1": ("Freeing a cuffed individual.", 0, 300),
    "ALPHA 1.2": ("Misusing authority.", 1, 250),
    "ALPHA 1.3": ("Discrimination.", 1, 300),
    "ALPHA 1.4": ("Disobeying orders near VIPs.", 3, 120),
    "ALPHA 1.5": ("Visible exploiting. Report to R&A.", 0, 200),
    "ALPHA 1.6": ("Slacking off.", 3, 200),
    "ALPHA 1.7": ("Disturbing the peace.", 3, 100),
    "ALPHA 1.8": ("In restricted/public area with no reason.", 3, 200),
    "ALPHA 1.9": ("Loitering in no-loitering zone.", 2, 150),
    "ALPHA 2.0": ("Harassment.", 2, 300),
}

# New dictionary for short clean descriptions in the warnings view
SHORT_DESCRIPTIONS = {
    "ALPHA 0.1": "Refusal to post",
    "ALPHA 0.2": "Random killing",
    "ALPHA 0.3": "Team killing",
    "ALPHA 0.4": "Disrupting divisional events",
    "ALPHA 0.5": "Disrupting official events",
    "ALPHA 0.6": "Restricted area entry",
    "ALPHA 0.7": "Arrest on Sight",
    "ALPHA 0.8": "Fake event hosting",
    "ALPHA 0.9": "Sexual comments/actions",
    "ALPHA 1.0": "Toxicity",
    "ALPHA 1.1": "Freeing cuffed individual",
    "ALPHA 1.2": "Misusing authority",
    "ALPHA 1.3": "Discrimination",
    "ALPHA 1.4": "Disobeying VIP orders",
    "ALPHA 1.5": "Visible exploiting",
    "ALPHA 1.6": "Slacking off",
    "ALPHA 1.7": "Disturbing peace",
    "ALPHA 1.8": "Loitering without reason",
    "ALPHA 1.9": "Loitering no-loiter zone",
    "ALPHA 2.0": "Harassment",
}

DB_FILE = "warnings.db"

def short_desc(full_desc):
    words = full_desc.split()
    return " ".join(words[:3]) if len(words) >= 3 else full_desc

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            warning TEXT,
            count INTEGER DEFAULT 1,
            last_updated TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

class MDTApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Coruscant Guard MDT")
        self.geometry("1080x620")
        self.configure(bg="#0f111a")
        self.create_widgets()
        init_db()
        self.refresh_warnings()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#1c1f2b", foreground="#f1f1f1", fieldbackground="#1c1f2b", rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background="#11131b", foreground="#D92525", font=('Orbitron', 10, 'bold'))
        style.configure("TButton", background="#222633", foreground="#f1f1f1")
        style.map("TButton", background=[("active", "#2c2f3a")])
        style.configure("TCombobox", fieldbackground="#1a1f2b", background="#1a1f2b", foreground="#f1f1f1")

        infractions_frame = tk.Frame(self, bg="#1a1d26", bd=1, relief="solid")
        infractions_frame.place(x=20, y=20, width=360, height=580)

        tk.Label(infractions_frame, text="Infractions", font=("Orbitron", 14, "bold"), fg="#D92525", bg="#1a1d26").pack(pady=10)

        self.infractions_text = tk.Text(infractions_frame, bg="#1a1d26", fg="#f1f1f1", font=("Consolas", 10), bd=0, wrap=tk.WORD)
        self.infractions_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        self.infractions_text.insert(tk.END, self.format_infractions())
        self.infractions_text.config(state=tk.DISABLED)

        controls_frame = tk.Frame(self, bg="#0f111a")
        controls_frame.place(x=400, y=20, width=660, height=580)

        tk.Label(controls_frame, text="Add Warning", font=("Orbitron", 14, "bold"), fg="#D92525", bg="#0f111a").pack(anchor="w")

        form_frame = tk.Frame(controls_frame, bg="#0f111a")
        form_frame.pack(fill=tk.X, pady=10)

        tk.Label(form_frame, text="Username:", fg="#f1f1f1", bg="#0f111a").grid(row=0, column=0, sticky="w")
        self.entry_username = tk.Entry(form_frame, bg="#1a1f2b", fg="#f1f1f1", insertbackground="#f1f1f1", relief="flat")
        self.entry_username.grid(row=0, column=1, sticky="ew", padx=5)

        tk.Label(form_frame, text="Infraction Code:", fg="#f1f1f1", bg="#0f1111").grid(row=1, column=0, sticky="w")

        # Use full description in dropdown
        full_warning_list = [f"{code} - {INFRACTIONS[code][0]}" for code in INFRACTIONS.keys()]
        self.combo_warning = ttk.Combobox(form_frame, values=full_warning_list, state="readonly")
        self.combo_warning.grid(row=1, column=1, sticky="ew", padx=5)
        form_frame.columnconfigure(1, weight=1)

        ttk.Button(controls_frame, text="Add Warning", command=self.add_warning).pack(fill=tk.X, pady=5)

        tk.Label(controls_frame, text="Warnings (All Users)", font=("Orbitron", 14, "bold"), fg="#D92525", bg="#0f111a").pack(anchor="w", pady=(10, 5))

        columns = ("Username", "Infraction Code", "Description", "Count", "Last Updated")
        self.tree = ttk.Treeview(controls_frame, columns=columns, show="headings", selectmode="browse")
        col_widths = {
            "Username": 120,
            "Infraction Code": 180,
            "Description": 140,
            "Count": 60,
            "Last Updated": 600,
        }
        for col in columns:
            anchor = "center"
            if col == "Last Updated":
                anchor = "w"
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=anchor, width=col_widths[col])

        self.tree.pack(expand=True, fill=tk.BOTH)

        clear_frame = tk.Frame(controls_frame, bg="#0f111a")
        clear_frame.pack(fill=tk.X, pady=10)

        tk.Label(clear_frame, text="Clear Warnings for:", fg="#f1f1f1", bg="#0f111a").pack(side=tk.LEFT)
        self.entry_clear_username = tk.Entry(clear_frame, bg="#1a1f2b", fg="#f1f1f1", insertbackground="#f1f1f1", relief="flat")
        self.entry_clear_username.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        ttk.Button(clear_frame, text="Clear", command=self.clear_warnings).pack(side=tk.LEFT)

    def format_infractions(self):
        lines = []
        for code, (desc, warns, jail) in INFRACTIONS.items():
            lines.append(f"{code} - {desc}\n  Required: {warns} warnings | Jail: {jail} secs\n")
        return "\n".join(lines)

    def add_warning(self):
        username = self.entry_username.get().strip()
        full_selection = self.combo_warning.get().strip()
        warning = full_selection.split(" - ")[0] if " - " in full_selection else full_selection
        if not username or not warning:
            messagebox.showerror("Error", "Username and infraction are required.")
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = c.fetchone()[0]

        c.execute("SELECT id, count FROM warnings WHERE user_id = ? AND warning = ?", (user_id, warning))
        existing = c.fetchone()
        if existing:
            c.execute("UPDATE warnings SET count = ?, last_updated = ? WHERE id = ?", (existing[1] + 1, timestamp, existing[0]))
        else:
            c.execute("INSERT INTO warnings (user_id, warning, count, last_updated) VALUES (?, ?, ?, ?)", (user_id, warning, 1, timestamp))
        conn.commit()
        conn.close()

        self.entry_username.delete(0, tk.END)
        self.combo_warning.set('')
        self.refresh_warnings()

    def refresh_warnings(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT u.username, w.warning, w.count, w.last_updated
            FROM warnings w
            JOIN users u ON w.user_id = u.id
            ORDER BY u.username ASC
        """)
        rows = c.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for username, code, count, updated in rows:
            desc_short = SHORT_DESCRIPTIONS.get(code, "Unknown")
            self.tree.insert("", "end", values=(username, code, desc_short, count, updated if updated else "N/A"))

    def clear_warnings(self):
        username = self.entry_clear_username.get().strip()
        if not username:
            messagebox.showerror("Error", "Enter a username.")
            return
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        if not result:
            messagebox.showinfo("Not Found", f"No warnings found for {username}.")
            conn.close()
            return
        c.execute("DELETE FROM warnings WHERE user_id = ?", (result[0],))
        conn.commit()
        conn.close()
        self.entry_clear_username.delete(0, tk.END)
        self.refresh_warnings()
        messagebox.showinfo("Cleared", f"Warnings for {username} cleared.")

if __name__ == "__main__":
    init_db()
    app = MDTApp()
    app.mainloop()
