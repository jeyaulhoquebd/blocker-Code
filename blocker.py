import sys
import os
import time
from datetime import datetime as dt
import tkinter as tk
from tkinter import messagebox
import threading

# উইন্ডোজের হোস্ট ফাইল পাথ
hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
redirect = "127.0.0.1"

class WebsiteBlocker:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Website Blocker")
        self.root.geometry("400x350")

        # UI Elements
        tk.Label(root, text="ওয়েবসাইটের নাম (কমা দিয়ে লিখুন):").pack(pady=5)
        self.site_entry = tk.Entry(root, width=40)
        self.site_entry.insert(0, "facebook.com, youtube.com")
        self.site_entry.pack(pady=5)

        tk.Label(root, text="কয়টা থেকে ব্লক হবে (24h format - যেমন: 9):").pack(pady=5)
        self.start_entry = tk.Entry(root, width=10)
        self.start_entry.insert(0, "9")
        self.start_entry.pack(pady=5)

        tk.Label(root, text="কয়টা পর্যন্ত ব্লক থাকবে (24h format - যেমন: 17):").pack(pady=5)
        self.end_entry = tk.Entry(root, width=10)
        self.end_entry.insert(0, "17")
        self.end_entry.pack(pady=5)

        self.btn_start = tk.Button(root, text="ব্লকার চালু করুন", command=self.start_blocking_thread, bg="red", fg="white")
        self.btn_start.pack(pady=20)

        self.status_label = tk.Label(root, text="অবস্থা: বন্ধ", fg="blue")
        self.status_label.pack(pady=5)

    def start_blocking_thread(self):
        # ব্যাকগ্রাউন্ডে কাজ করার জন্য থ্রেড ব্যবহার
        block_thread = threading.Thread(target=self.block_engine, daemon=True)
        block_thread.start()
        self.btn_start.config(state="disabled")
        self.status_label.config(text="অবস্থা: ব্লকার চলছে...")

    def block_engine(self):
        sites = [s.strip() for s in self.site_entry.get().split(",")]
        start_h = int(self.start_entry.get())
        end_h = int(self.end_entry.get())

        while True:
            current_time = dt.now()
            if start_h <= current_time.hour < end_h:
                try:
                    with open(hosts_path, 'r+') as file:
                        content = file.read()
                        for site in sites:
                            if site not in content:
                                file.write(redirect + " " + site + "\n")
                except PermissionError:
                    messagebox.showerror("Error", "দয়া করে এটি Administrator হিসেবে চালান!")
                    break
            else:
                with open(hosts_path, 'r+') as file:
                    lines = file.readlines()
                    file.seek(0)
                    for line in lines:
                        if not any(site in line for site in sites):
                            file.write(line)
                    file.truncate()
            
            time.sleep(10) # প্রতি ১০ সেকেন্ড পর পর চেক করবে

# মেইন ফাংশন
if __name__ == "__main__":
    root = tk.Tk()
    app = WebsiteBlocker(root)
    root.mainloop()