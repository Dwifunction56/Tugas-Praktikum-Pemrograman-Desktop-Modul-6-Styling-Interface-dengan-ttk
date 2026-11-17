# ============================================================
# Praktikum 1.2 - Implementasi Theme Switching
# ============================================================

# ------------------------------------------------------------
# SECTION 1: Import library
# ------------------------------------------------------------
import tkinter as tk
from tkinter import ttk


class ThemeSwitcher:

    # ------------------------------------------------------------
    # SECTION 2: Inisialisasi jendela utama dan style
    # ------------------------------------------------------------
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Theme Switcher Demo")
        self.root.geometry("600x400")

        # Inisialisasi style
        # (ttk.Style mengatur tampilan semua widget ttk sekaligus)
        self.style = ttk.Style()
        self.current_theme = tk.StringVar(value=self.style.theme_use())

        self._buat_interface()
        self._setup_themes()

    # ------------------------------------------------------------
    # SECTION 3: Membuat tampilan (interface)
    # ------------------------------------------------------------
    def _buat_interface(self):

        # --- 3a. Frame utama dan header ---------------------------
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Theme Switcher Demo",
                 font=('Arial', 16, 'bold')).pack(pady=(0,20))

        # --- 3b. Pemilihan theme ----------------------------------
        theme_frame = ttk.LabelFrame(main_frame, text="Pilih Theme", padding="10")
        theme_frame.pack(fill='x', pady=(0,20))

        # Combobox untuk memilih theme
        # (event <<ComboboxSelected>> memanggil change_theme saat pilihan berubah)
        ttk.Label(theme_frame, text="Theme:").pack(anchor='w')
        self.theme_combo = ttk.Combobox(theme_frame, textvariable=self.current_theme,
                                       values=self.style.theme_names(), state="readonly")
        self.theme_combo.pack(fill='x', pady=(5,10))
        self.theme_combo.bind('<<ComboboxSelected>>', self.change_theme)

        # --- 3c. Widget demo --------------------------------------
        demo_frame = ttk.LabelFrame(main_frame, text="Demo Widgets", padding="10")
        demo_frame.pack(fill='both', expand=True)

        # Entry widget
        ttk.Label(demo_frame, text="Entry Widget:").pack(anchor='w')
        self.demo_entry = ttk.Entry(demo_frame)
        self.demo_entry.pack(fill='x', pady=(5,10))
        self.demo_entry.insert(0, "Contoh text...")

        # Button widgets (normal dan disabled)
        button_frame = ttk.Frame(demo_frame)
        button_frame.pack(fill='x', pady=(0,10))

        ttk.Button(button_frame, text="Normal Button").pack(side='left', padx=(0,5))
        ttk.Button(button_frame, text="Disabled Button", state='disabled').pack(side='left')

        # Progressbar
        ttk.Label(demo_frame, text="Progress Bar:").pack(anchor='w')
        self.progress = ttk.Progressbar(demo_frame, mode='determinate', value=70)
        self.progress.pack(fill='x', pady=(5,10))

        # Scale
        ttk.Label(demo_frame, text="Scale Widget:").pack(anchor='w')
        self.scale = ttk.Scale(demo_frame, from_=0, to=100, orient='horizontal')
        self.scale.pack(fill='x', pady=(5,10))
        self.scale.set(50)

    # ------------------------------------------------------------
    # SECTION 4: Daftar theme yang tersedia (tampil di Terminal)
    # ------------------------------------------------------------
    def _setup_themes(self):
        # Konfigurasi tambahan untuk beberapa theme
        available_themes = self.style.theme_names()
        print(f"Available themes: {available_themes}")

    # ------------------------------------------------------------
    # SECTION 5: Mengganti theme saat dipilih di combobox
    # ------------------------------------------------------------
    def change_theme(self, event=None):
        selected_theme = self.current_theme.get()
        try:
            self.style.theme_use(selected_theme)
            print(f"Theme changed to: {selected_theme}")
        except tk.TclError as e:
            print(f"Error changing theme: {e}")

    # ------------------------------------------------------------
    # SECTION 6: Menjalankan event loop aplikasi
    # ------------------------------------------------------------
    def run(self):
        self.root.mainloop()


# ------------------------------------------------------------
# SECTION 7: Titik masuk program
# ------------------------------------------------------------
if __name__ == "__main__":
    app = ThemeSwitcher()
    app.run()