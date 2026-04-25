import os
import sys
import time
import threading
import ctypes
from datetime import datetime as dt, time as dtime
import tkinter as tk
from tkinter import messagebox, ttk

# হোস্ট ফাইল পাথ
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT = "127.0.0.1"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ProfessionalBlocker:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro Time Blocker (AM/PM)")
        self.root.geometry("500x550")
        self.root.resizable(False, False)
        self.is_running = False

        # মূল ফ্রেম
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ওয়েবসাইট ইনপুট
        ttk.Label(main_frame, text="ব্লক করার ওয়েবসাইটগুলো (কমা দিয়ে লিখুন):", font=("Arial", 10, "bold")).pack(anchor="w")
        self.site_entry = ttk.Entry(main_frame, width=55)
        self.site_entry.insert(0, "facebook.com, youtube.com, instagram.com")
        self.site_entry.pack(pady=(5, 20))

        # সময় সিলেকশন ফ্রেম
        time_container = ttk.LabelFrame(main_frame, text="সময় নির্ধারণ করুন", padding="15")
        time_container.pack(fill="x", pady=10)

        # ড্রপডাউন অপশনগুলো
        hours = [str(i).zfill(2) for i in range(1, 13)]
        minutes = [str(i).zfill(2) for i in range(0, 60, 5)] # ৫ মিনিট গ্যাপে
        periods = ["AM", "PM"]

        # শুরুর সময় (Start Time)
        ttk.Label(time_container, text="কখন থেকে শুরু:").grid(row=0, column=0, sticky="w", pady=5)
        self.start_h = ttk.Combobox(time_container, values=hours, width=5, state="readonly")
        self.start_h.set("09")
        self.start_h.grid(row=0, column=1, padx=5)

        self.start_m = ttk.Combobox(time_container, values=minutes, width=5, state="readonly")
        self.start_m.set("00")
        self.start_m.grid(row=0, column=2, padx=5)

        self.start_p = ttk.Combobox(time_container, values=periods, width=5, state="readonly")
        self.start_p.set("AM")
        self.start_p.grid(row=0, column=3, padx=5)

        # শেষ সময় (End Time)
        ttk.Label(time_container, text="কখন শেষ হবে:").grid(row=1, column=0, sticky="w", pady=15)
        self.end_h = ttk.Combobox(time_container, values=hours, width=5, state="readonly")
        self.end_h.set("05")
        self.end_h.grid(row=1, column=1, padx=5)

        self.end_m = ttk.Combobox(time_container, values=minutes, width=5, state="readonly")
        self.end_m.set("00")
        self.end_m.grid(row=1, column=2, padx=5)

        self.end_p = ttk.Combobox(time_container, values=periods, width=5, state="readonly")
        self.end_p.set("PM")
        self.end_p.grid(row=1, column=3, padx=5)

        # কন্ট্রোল বাটন
        self.btn_start = tk.Button(main_frame, text="ব্লকার এক্টিভেট করুন", command=self.toggle_blocking, 
                                   bg="#16a085", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_start.pack(fill="x", pady=20)

        self.status_label = ttk.Label(main_frame, text="Status: Idle", foreground="gray", font=("Arial", 9, "italic"))
        self.status_label.pack()

    def get_time_object(self, h, m, p):
        """ড্রপডাউন থেকে প্রাপ্ত সময়কে Python-এর time অবজেক্টে রূপান্তর করে"""
        hour = int(h)
        if p == "PM" and hour != 12:
            hour += 12
        elif p == "AM" and hour == 12:
            hour = 0
        return dtime(hour, int(m))

    def toggle_blocking(self):
        if not self.is_running:
            if not is_admin():
                messagebox.showwarning("Admin Rights", "দয়া করে Administrator হিসেবে এটি রান করুন!")
                return
            
            self.sites = [s.strip() for s in self.site_entry.get().split(",") if s.strip()]
            if not self.sites:
                messagebox.showerror("Error", "ওয়েবসাইটের নাম দিন!")
                return

            self.start_time_obj = self.get_time_object(self.start_h.get(), self.start_m.get(), self.start_p.get())
            self.end_time_obj = self.get_time_object(self.end_h.get(), self.end_m.get(), self.end_p.get())

            self.is_running = True
            self.btn_start.config(text="বন্ধ করুন (Deactivate)", bg="#c0392b")
            self.status_label.config(text="Status: ব্লকার চলছে...", foreground="green")
            
            threading.Thread(target=self.run_engine, daemon=True).start()
        else:
            self.stop_engine()

    def stop_engine(self):
        self.is_running = False
        self.btn_start.config(text="ব্লকার এক্টিভেট করুন", bg="#16a085")
        self.status_label.config(text="Status: বন্ধ (সব ওয়েবসাইট খুলে দেওয়া হয়েছে)", foreground="gray")
        self.unblock_sites()

    def run_engine(self):
        while self.is_running:
            now = dt.now().time()
            
            # সময় চেক করা (যদি এন্ড টাইম স্টার্ট টাইম থেকে কম হয় অর্থাৎ মাঝরাত পার হয়)
            is_blocking_time = False
            if self.start_time_obj <= self.end_time_obj:
                is_blocking_time = self.start_time_obj <= now <= self.end_time_obj
            else: # রাত ১২টার পরের সময় হ্যান্ডেল করার জন্য
                is_blocking_time = now >= self.start_time_obj or now <= self.end_time_obj

            if is_blocking_time:
                self.block_sites()
            else:
                self.unblock_sites()
            time.sleep(10)

    def block_sites(self):
        try:
            with open(HOSTS_PATH, 'r+') as file:
                content = file.read()
                for site in self.sites:
                    if site not in content:
                        file.write(f"{REDIRECT} {site}\n")
        except: pass

    def unblock_sites(self):
        try:
            with open(HOSTS_PATH, 'r+') as file:
                lines = file.readlines()
                file.seek(0)
                for line in lines:
                    if not any(site in line for site in self.sites):
                        file.write(line)
                file.truncate()
        except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalBlocker(root)
    root.mainloop()