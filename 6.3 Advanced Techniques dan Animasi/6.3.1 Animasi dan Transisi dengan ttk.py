# ============================================================
# Praktikum 3.1 - Animasi dan Transisi dengan ttk
# (Versi PERBAIKAN)
#
# Perbedaan dari versi modul:
#   1. Tinggi jendela dinaikkan ke 850 supaya bagian Fade Animation
#      tidak terpotong di bawah layar.
#   2. Animasi memakai root.after(), bukan threading. Tkinter tidak
#      thread-safe: widget sebaiknya hanya diubah dari thread utama.
#      after() menjadwalkan langkah animasi berikutnya tanpa membekukan
#      UI, jadi tujuan "UI tidak freeze" tetap tercapai.
#   3. Fade sungguhan: warna teks berubah bertahap dari terang ke warna
#      latar (dan sebaliknya), bukan sekadar mengubah state jadi disabled.
#   4. Setelah Fade In, konten kembali ke posisinya di atas tombol
#      (versi modul menaruhnya di bawah tombol).
#   5. Animasi yang sedang berjalan dibatalkan dulu kalau tombol diklik
#      lagi, supaya dua animasi tidak saling bertabrakan.
# ============================================================

# ------------------------------------------------------------
# SECTION 1: Import library
# ------------------------------------------------------------
import tkinter as tk
from tkinter import ttk


class AnimatedApp:

    # ------------------------------------------------------------
    # SECTION 2: Inisialisasi jendela utama dan variabel animasi
    # ------------------------------------------------------------
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Animasi dan Transisi dengan ttk")
        self.root.geometry("800x850")  # PERBAIKAN: dari 600 ke 850
        self.root.configure(bg='#1a1a1a')

        # Animation variables
        self.animation_running = False
        self.progress_value = 0
        self.fade_alpha = 1.0

        # PERBAIKAN: menyimpan ID animasi yang sedang berjalan (untuk dibatalkan)
        self.slide_job = None
        self.fade_job = None

        self._setup_styles()
        self._buat_interface()

    # ------------------------------------------------------------
    # SECTION 3: Style tema gelap
    # ------------------------------------------------------------
    def _setup_styles(self):
        self.style = ttk.Style()

        # (Opsional) Di Windows, tema bawaan 'vista' mengabaikan warna
        # background tombol. Hapus tanda # di baris bawah ini kalau
        # tombol tidak berwarna hijau.
        # self.style.theme_use('clam')

        # --- 3a. Frame dan label gelap ----------------------------
        self.style.configure('Dark.TFrame',
                           background='#2d2d2d',
                           relief='flat')

        self.style.configure('Dark.TLabel',
                           background='#2d2d2d',
                           foreground='#ffffff',
                           font=('Arial', 11))

        self.style.configure('Title.TLabel',
                           background='#2d2d2d',
                           foreground='#00ff88',
                           font=('Arial', 16, 'bold'))

        # PERBAIKAN: style khusus label yang di-fade, supaya label lain tidak ikut berubah
        self.style.configure('FadeTitle.TLabel',
                           background='#2d2d2d',
                           foreground='#00ff88',
                           font=('Arial', 16, 'bold'))

        self.style.configure('FadeText.TLabel',
                           background='#2d2d2d',
                           foreground='#ffffff',
                           font=('Arial', 11))

        # --- 3b. Tombol hijau dengan efek hover/klik --------------
        self.style.configure('Animated.TButton',
                           background='#00ff88',
                           foreground='#1a1a1a',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(20, 10),
                           font=('Arial', 10, 'bold'))

        self.style.map('Animated.TButton',
                      background=[('active', '#00cc6a'),
                                ('pressed', '#009954')])

    # ------------------------------------------------------------
    # SECTION 4: Membuat tampilan (interface)
    # ------------------------------------------------------------
    def _buat_interface(self):

        # --- 4a. Container utama dan header -----------------------
        self.main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        self.header_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        self.header_frame.pack(fill='x', pady=(0,30))

        self.title_label = ttk.Label(self.header_frame, text="🎬 Animation Demo",
                                    style='Title.TLabel')
        self.title_label.pack()

        # --- 4b. Bagian animasi progress bar ----------------------
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Progress Animation", padding="20")
        self.progress_frame.pack(fill='x', pady=(0,20))

        ttk.Label(self.progress_frame, text="Animated Progress Bar:",
                 style='Dark.TLabel').pack(anchor='w', pady=(0,10))

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate',
                                          length=400, style='TProgressbar')
        self.progress_bar.pack(fill='x', pady=(0,15))

        progress_controls = ttk.Frame(self.progress_frame, style='Dark.TFrame')
        progress_controls.pack(fill='x')

        ttk.Button(progress_controls, text="Start Animation",
                  style='Animated.TButton', command=self.start_progress_animation).pack(side='left', padx=(0,10))
        ttk.Button(progress_controls, text="Stop Animation",
                  style='Animated.TButton', command=self.stop_animation).pack(side='left', padx=(0,10))
        ttk.Button(progress_controls, text="Reset",
                  style='Animated.TButton', command=self.reset_progress).pack(side='left')

        # --- 4c. Bagian sliding panel -----------------------------
        self.slide_frame = ttk.LabelFrame(self.main_frame, text="Sliding Panel", padding="20")
        self.slide_frame.pack(fill='x', pady=(0,20))

        self.slide_container = ttk.Frame(self.slide_frame, style='Dark.TFrame', height=200)
        self.slide_container.pack(fill='x', pady=(0,15))
        self.slide_container.pack_propagate(False)

        # Panel yang akan slide (awalnya di luar layar: x=-300)
        self.slide_x = -300
        self.sliding_panel = ttk.Frame(self.slide_container, style='Dark.TFrame')
        self.sliding_panel.place(x=self.slide_x, y=0, width=300, height=200)

        panel_content = ttk.Frame(self.sliding_panel, style='Dark.TFrame')
        panel_content.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(panel_content, text="🎯 Sliding Panel Content",
                 style='Title.TLabel').pack()
        ttk.Label(panel_content, text="Panel ini dapat slide masuk dan keluar",
                 style='Dark.TLabel').pack(pady=(10,0))

        slide_controls = ttk.Frame(self.slide_frame, style='Dark.TFrame')
        slide_controls.pack(fill='x')

        ttk.Button(slide_controls, text="Slide In",
                  style='Animated.TButton', command=self.slide_in).pack(side='left', padx=(0,10))
        ttk.Button(slide_controls, text="Slide Out",
                  style='Animated.TButton', command=self.slide_out).pack(side='left')

        # --- 4d. Bagian fade --------------------------------------
        self.fade_frame = ttk.LabelFrame(self.main_frame, text="Fade Animation", padding="20")
        self.fade_frame.pack(fill='both', expand=True)

        self.fade_content = ttk.Frame(self.fade_frame, style='Dark.TFrame')
        self.fade_content.pack(fill='both', expand=True, pady=(0,15))

        ttk.Label(self.fade_content, text="✨ Fade Content",
                 style='FadeTitle.TLabel').pack(pady=20)
        ttk.Label(self.fade_content, text="Content ini dapat fade in/out dengan smooth transition",
                 style='FadeText.TLabel').pack()

        # PERBAIKAN: disimpan di self supaya Fade In bisa menaruh konten di atasnya
        self.fade_controls = ttk.Frame(self.fade_frame, style='Dark.TFrame')
        self.fade_controls.pack(fill='x')

        ttk.Button(self.fade_controls, text="Fade Out",
                  style='Animated.TButton', command=self.fade_out).pack(side='left', padx=(0,10))
        ttk.Button(self.fade_controls, text="Fade In",
                  style='Animated.TButton', command=self.fade_in).pack(side='left')

    # ------------------------------------------------------------
    # SECTION 5: Animasi progress bar (pakai after)
    # ------------------------------------------------------------
    def start_progress_animation(self):
        if not self.animation_running:
            self.animation_running = True
            self._animate_progress()

    def _animate_progress(self):
        # Satu langkah animasi, lalu jadwalkan langkah berikutnya 50 ms lagi
        if self.animation_running and self.progress_value < 100:
            self.progress_value += 1
            self.progress_bar['value'] = self.progress_value
            self.root.after(50, self._animate_progress)
        else:
            self.animation_running = False

    def stop_animation(self):
        self.animation_running = False

    def reset_progress(self):
        self.animation_running = False
        self.progress_value = 0
        self.progress_bar['value'] = 0

    # ------------------------------------------------------------
    # SECTION 6: Animasi sliding panel (masuk dan keluar)
    # ------------------------------------------------------------
    def slide_in(self):
        self._mulai_slide(end_x=0)

    def slide_out(self):
        self._mulai_slide(end_x=-300)

    def _mulai_slide(self, end_x):
        # Batalkan animasi slide sebelumnya, lalu mulai dari posisi panel saat ini
        if self.slide_job:
            self.root.after_cancel(self.slide_job)
        self._animate_slide(self.slide_x, end_x, step=0, steps=30)

    def _animate_slide(self, start_x, end_x, step, steps):
        self.slide_x = start_x + (end_x - start_x) * (step / steps)
        self.sliding_panel.place(x=self.slide_x, y=0, width=300, height=200)
        if step < steps:
            self.slide_job = self.root.after(20, self._animate_slide,
                                             start_x, end_x, step + 1, steps)
        else:
            self.slide_job = None

    # ------------------------------------------------------------
    # SECTION 7: Animasi fade (perubahan warna teks bertahap)
    # ------------------------------------------------------------
    def _campur_warna(self, warna_awal, warna_akhir, t):
        # t = 0 -> warna_awal, t = 1 -> warna_akhir
        r1, g1, b1 = (int(warna_awal[i:i+2], 16) for i in (1, 3, 5))
        r2, g2, b2 = (int(warna_akhir[i:i+2], 16) for i in (1, 3, 5))
        r = round(r1 + (r2 - r1) * t)
        g = round(g1 + (g2 - g1) * t)
        b = round(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _set_fade(self, alpha):
        # alpha = 1 -> teks terlihat penuh, alpha = 0 -> teks menyatu dengan latar
        self.fade_alpha = alpha
        latar = '#2d2d2d'
        self.style.configure('FadeTitle.TLabel',
                             foreground=self._campur_warna(latar, '#00ff88', alpha))
        self.style.configure('FadeText.TLabel',
                             foreground=self._campur_warna(latar, '#ffffff', alpha))

    def fade_out(self):
        self._mulai_fade(target=0.0, selesai=self.fade_content.pack_forget)

    def fade_in(self):
        if not self.fade_content.winfo_ismapped():
            self._set_fade(0.0)
            # PERBAIKAN: kembalikan konten DI ATAS tombol, bukan di bawahnya
            self.fade_content.pack(fill='both', expand=True, pady=(0,15),
                                   before=self.fade_controls)
        self._mulai_fade(target=1.0)

    def _mulai_fade(self, target, selesai=None):
        if self.fade_job:
            self.root.after_cancel(self.fade_job)
        self._animate_fade(self.fade_alpha, target, step=0, steps=20, selesai=selesai)

    def _animate_fade(self, awal, akhir, step, steps, selesai):
        self._set_fade(awal + (akhir - awal) * (step / steps))
        if step < steps:
            self.fade_job = self.root.after(50, self._animate_fade,
                                            awal, akhir, step + 1, steps, selesai)
        else:
            self.fade_job = None
            if selesai:
                selesai()

    # ------------------------------------------------------------
    # SECTION 8: Menjalankan event loop aplikasi
    # ------------------------------------------------------------
    def run(self):
        self.root.mainloop()


# ------------------------------------------------------------
# SECTION 9: Titik masuk program
# ------------------------------------------------------------
if __name__ == "__main__":
    app = AnimatedApp()
    app.run()