# ============================================================
# Praktikum 3.2 - Dashboard Interaktif dengan Real-time Updates
# (Versi PERBAIKAN)
#
# Perbedaan dari versi modul:
#   1. Loop monitoring memakai root.after(), bukan threading. Tkinter tidak
#      thread-safe, dan di versi modul klik Stop lalu Start dengan cepat
#      membuat DUA loop berjalan bersamaan (data masuk 2x lebih cepat).
#   2. Scrollbar chart dipasang SEBELUM Text, supaya muncul di samping
#      kanan chart (di versi modul scrollbar terjepit kecil di bawahnya).
#   3. Status awal "Stopped" langsung berwarna merah.
# ============================================================

# ------------------------------------------------------------
# SECTION 1: Import library
# ------------------------------------------------------------
import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime


class InteractiveDashboard:

    # ------------------------------------------------------------
    # SECTION 2: Inisialisasi jendela, data, dan metrik
    # ------------------------------------------------------------
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interactive Dashboard - Real-time Updates")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0f1419')

        # Data variables
        self.is_running = False
        self.cpu_data = []
        self.memory_data = []
        self.network_data = []
        self.max_data_points = 50
        self.monitor_job = None  # PERBAIKAN: ID jadwal after() yang sedang aktif

        # Metrics
        self.current_cpu = 0
        self.current_memory = 0
        self.current_network = 0
        self.total_requests = 0
        self.active_users = 0

        self._setup_styles()
        self._buat_interface()

    # ------------------------------------------------------------
    # SECTION 3: Style tema dashboard
    # ------------------------------------------------------------
    def _setup_styles(self):
        self.style = ttk.Style()

        # (Opsional, bukan dari modul) Di Windows, tema bawaan 'vista' mengabaikan
        # warna background tombol. Hapus tanda # di baris bawah ini
        # kalau tombol tidak berwarna biru muda.
        # self.style.theme_use('clam')

        # --- 3a. Frame dan card -----------------------------------
        self.style.configure('Dashboard.TFrame',
                           background='#1e2328',
                           relief='flat')

        self.style.configure('Card.TFrame',
                           background='#252a31',
                           relief='raised',
                           borderwidth=1)

        # --- 3b. Label teks, judul, dan angka metrik --------------
        self.style.configure('Dashboard.TLabel',
                           background='#1e2328',
                           foreground='#ffffff',
                           font=('Arial', 10))

        self.style.configure('Title.TLabel',
                           background='#1e2328',
                           foreground='#00d4ff',
                           font=('Arial', 14, 'bold'))

        self.style.configure('Metric.TLabel',
                           background='#252a31',
                           foreground='#00ff88',
                           font=('Arial', 20, 'bold'))

        self.style.configure('MetricLabel.TLabel',
                           background='#252a31',
                           foreground='#ffffff',
                           font=('Arial', 9))

        # --- 3c. Tombol kontrol -----------------------------------
        self.style.configure('Control.TButton',
                           background='#00d4ff',
                           foreground='#0f1419',
                           borderwidth=0,
                           padding=(15, 8),
                           font=('Arial', 10, 'bold'))

    # ------------------------------------------------------------
    # SECTION 4: Membuat tampilan (interface)
    # ------------------------------------------------------------
    def _buat_interface(self):

        # --- 4a. Container utama dan header -----------------------
        self.main_frame = ttk.Frame(self.root, style='Dashboard.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        header_frame = ttk.Frame(self.main_frame, style='Dashboard.TFrame')
        header_frame.pack(fill='x', pady=(0,20))

        ttk.Label(header_frame, text="📊 System Dashboard",
                 style='Title.TLabel').pack(side='left')

        self.status_label = ttk.Label(header_frame, text="● Stopped",
                                     style='Dashboard.TLabel', foreground='#ff4444')  # PERBAIKAN
        self.status_label.pack(side='right')

        self.time_label = ttk.Label(header_frame, text="",
                                   style='Dashboard.TLabel')
        self.time_label.pack(side='right', padx=(0,20))

        # --- 4b. Baris card metrik: CPU, Memory, Network ----------
        metrics_frame = ttk.Frame(self.main_frame, style='Dashboard.TFrame')
        metrics_frame.pack(fill='x', pady=(0,20))

        # CPU Card
        self.cpu_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding="15")
        self.cpu_card.pack(side='left', fill='both', expand=True, padx=(0,10))

        ttk.Label(self.cpu_card, text="CPU Usage", style='MetricLabel.TLabel').pack()
        self.cpu_metric = ttk.Label(self.cpu_card, text="0%", style='Metric.TLabel')
        self.cpu_metric.pack(pady=(5,0))

        self.cpu_progress = ttk.Progressbar(self.cpu_card, mode='determinate', length=200)
        self.cpu_progress.pack(pady=(10,0), fill='x')

        # Memory Card
        self.memory_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding="15")
        self.memory_card.pack(side='left', fill='both', expand=True, padx=(5,5))

        ttk.Label(self.memory_card, text="Memory Usage", style='MetricLabel.TLabel').pack()
        self.memory_metric = ttk.Label(self.memory_card, text="0%", style='Metric.TLabel')
        self.memory_metric.pack(pady=(5,0))

        self.memory_progress = ttk.Progressbar(self.memory_card, mode='determinate', length=200)
        self.memory_progress.pack(pady=(10,0), fill='x')

        # Network Card
        self.network_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding="15")
        self.network_card.pack(side='left', fill='both', expand=True, padx=(10,0))

        ttk.Label(self.network_card, text="Network I/O", style='MetricLabel.TLabel').pack()
        self.network_metric = ttk.Label(self.network_card, text="0 MB/s", style='Metric.TLabel')
        self.network_metric.pack(pady=(5,0))

        self.network_progress = ttk.Progressbar(self.network_card, mode='determinate', length=200)
        self.network_progress.pack(pady=(10,0), fill='x')

        # --- 4c. Baris statistik: Requests dan Users --------------
        stats_frame = ttk.Frame(self.main_frame, style='Dashboard.TFrame')
        stats_frame.pack(fill='x', pady=(0,20))

        # Requests Card
        requests_card = ttk.Frame(stats_frame, style='Card.TFrame', padding="15")
        requests_card.pack(side='left', fill='both', expand=True, padx=(0,10))

        ttk.Label(requests_card, text="Total Requests", style='MetricLabel.TLabel').pack()
        self.requests_metric = ttk.Label(requests_card, text="0", style='Metric.TLabel')
        self.requests_metric.pack(pady=(5,0))

        # Users Card
        users_card = ttk.Frame(stats_frame, style='Card.TFrame', padding="15")
        users_card.pack(side='left', fill='both', expand=True, padx=(10,0))

        ttk.Label(users_card, text="Active Users", style='MetricLabel.TLabel').pack()
        self.users_metric = ttk.Label(users_card, text="0", style='Metric.TLabel')
        self.users_metric.pack(pady=(5,0))

        # --- 4d. Area chart (disimulasikan dengan Text) -----------
        chart_frame = ttk.LabelFrame(self.main_frame, text="Real-time Monitoring", padding="15")
        chart_frame.pack(fill='both', expand=True, pady=(0,20))

        self.chart_text = tk.Text(chart_frame, height=15, bg='#0f1419', fg='#00ff88',
                                 font=('Consolas', 9), state='disabled')

        # PERBAIKAN: scrollbar di-pack lebih dulu supaya mendapat kolom kanan penuh
        chart_scroll = ttk.Scrollbar(chart_frame, orient="vertical", command=self.chart_text.yview)
        chart_scroll.pack(side="right", fill="y")
        self.chart_text.pack(side="left", fill='both', expand=True)
        self.chart_text.configure(yscrollcommand=chart_scroll.set)

        # --- 4e. Tombol kontrol -----------------------------------
        control_frame = ttk.Frame(self.main_frame, style='Dashboard.TFrame')
        control_frame.pack(fill='x')

        ttk.Button(control_frame, text="▶ Start Monitoring",
                  style='Control.TButton', command=self.start_monitoring).pack(side='left', padx=(0,10))
        ttk.Button(control_frame, text="⏸ Stop Monitoring",
                  style='Control.TButton', command=self.stop_monitoring).pack(side='left', padx=(0,10))
        ttk.Button(control_frame, text="🗑 Clear Data",
                  style='Control.TButton', command=self.clear_data).pack(side='left', padx=(0,10))
        ttk.Button(control_frame, text="📊 Generate Report",
                  style='Control.TButton', command=self.generate_report).pack(side='right')

        # Start time updates
        self._update_time()

    # ------------------------------------------------------------
    # SECTION 5: Jam real-time di header
    # ------------------------------------------------------------
    def _update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)

    # ------------------------------------------------------------
    # SECTION 6: Start/Stop monitoring dan loop data (pakai after)
    # ------------------------------------------------------------
    def start_monitoring(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="● Running", foreground='#00ff88')
            self._monitoring_loop()

    def stop_monitoring(self):
        self.is_running = False
        # PERBAIKAN: batalkan jadwal berikutnya, supaya Start lagi tidak membuat loop ganda
        if self.monitor_job:
            self.root.after_cancel(self.monitor_job)
            self.monitor_job = None
        self.status_label.config(text="● Stopped", foreground='#ff4444')

    def _monitoring_loop(self):
        # Satu putaran update, lalu jadwalkan putaran berikutnya 1 detik lagi
        if self.is_running:
            # Generate random data
            self.current_cpu = random.randint(10, 90)
            self.current_memory = random.randint(20, 80)
            self.current_network = random.uniform(0.1, 10.0)

            # Update requests and users
            self.total_requests += random.randint(1, 5)
            self.active_users = random.randint(50, 200)

            # Store data for chart
            self.cpu_data.append(self.current_cpu)
            self.memory_data.append(self.current_memory)
            self.network_data.append(self.current_network)

            # Limit data points
            if len(self.cpu_data) > self.max_data_points:
                self.cpu_data.pop(0)
                self.memory_data.pop(0)
                self.network_data.pop(0)

            # Update UI
            self._update_metrics()
            self._update_chart()

            self.monitor_job = self.root.after(1000, self._monitoring_loop)  # Update every second

    # ------------------------------------------------------------
    # SECTION 7: Memperbarui angka dan progress bar metrik
    # ------------------------------------------------------------
    def _update_metrics(self):
        self.cpu_metric.config(text=f"{self.current_cpu}%")
        self.cpu_progress['value'] = self.current_cpu

        self.memory_metric.config(text=f"{self.current_memory}%")
        self.memory_progress['value'] = self.current_memory

        self.network_metric.config(text=f"{self.current_network:.1f} MB/s")
        self.network_progress['value'] = min(self.current_network * 10, 100)

        self.requests_metric.config(text=str(self.total_requests))
        self.users_metric.config(text=str(self.active_users))

    # ------------------------------------------------------------
    # SECTION 8: Chart ASCII di area monitoring
    # ------------------------------------------------------------
    def _update_chart(self):
        if not self.cpu_data:
            return

        self.chart_text.config(state='normal')

        # Create simple ASCII chart
        timestamp = datetime.now().strftime("%H:%M:%S")
        cpu_bar = "█" * (self.current_cpu // 5)
        memory_bar = "█" * (self.current_memory // 5)
        network_bar = "█" * min(int(self.current_network), 20)

        chart_line = f"[{timestamp}] CPU: {cpu_bar:<20} {self.current_cpu}% | "
        chart_line += f"MEM: {memory_bar:<20} {self.current_memory}% | "
        chart_line += f"NET: {network_bar:<20} {self.current_network:.1f}MB/s\n"

        self.chart_text.insert('end', chart_line)
        self.chart_text.see('end')
        self.chart_text.config(state='disabled')

    # ------------------------------------------------------------
    # SECTION 9: Clear Data (reset semua)
    # ------------------------------------------------------------
    def clear_data(self):
        self.cpu_data.clear()
        self.memory_data.clear()
        self.network_data.clear()
        self.total_requests = 0

        self.chart_text.config(state='normal')
        self.chart_text.delete('1.0', 'end')
        self.chart_text.config(state='disabled')

        # Reset metrics
        self.cpu_metric.config(text="0%")
        self.memory_metric.config(text="0%")
        self.network_metric.config(text="0 MB/s")
        self.requests_metric.config(text="0")
        self.users_metric.config(text="0")

        self.cpu_progress['value'] = 0
        self.memory_progress['value'] = 0
        self.network_progress['value'] = 0

    # ------------------------------------------------------------
    # SECTION 10: Generate Report (ringkasan rata-rata)
    # ------------------------------------------------------------
    def generate_report(self):
        if not self.cpu_data:
            return

        # Generate summary report
        avg_cpu = sum(self.cpu_data) / len(self.cpu_data)
        avg_memory = sum(self.memory_data) / len(self.memory_data)
        avg_network = sum(self.network_data) / len(self.network_data)

        report = f"\n{'='*60}\n"
        report += f"SYSTEM PERFORMANCE REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*60}\n"
        report += f"Average CPU Usage: {avg_cpu:.1f}%\n"
        report += f"Average Memory Usage: {avg_memory:.1f}%\n"
        report += f"Average Network I/O: {avg_network:.1f} MB/s\n"
        report += f"Total Requests: {self.total_requests}\n"
        report += f"Current Active Users: {self.active_users}\n"
        report += f"Data Points Collected: {len(self.cpu_data)}\n"
        report += f"{'='*60}\n\n"

        self.chart_text.config(state='normal')
        self.chart_text.insert('end', report)
        self.chart_text.see('end')
        self.chart_text.config(state='disabled')

    # ------------------------------------------------------------
    # SECTION 11: Menjalankan event loop aplikasi
    # ------------------------------------------------------------
    def run(self):
        self.root.mainloop()


# ------------------------------------------------------------
# SECTION 12: Titik masuk program
# ------------------------------------------------------------
if __name__ == "__main__":
    app = InteractiveDashboard()
    app.run()