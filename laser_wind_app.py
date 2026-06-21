import tkinter as tk
from tkinter import messagebox

class LaserWindApp:
    def __init__(self, root):
        self.root = root
        self.root.title("توربین بادی لیزری")
        self.root.geometry("500x400")
        self.root.configure(bg="#1e1e2e")

        # عنوان
        self.title_label = tk.Label(root, text="مدل توربین بادی لیزری", font=("B Nazanin", 20, "bold"), bg="#1e1e2e", fg="cyan")
        self.title_label.pack(pady=15)

        # ورودی سرعت باد
        self.wind_label = tk.Label(root, text="سرعت باد (m/s):", font=("B Nazanin", 14), bg="#1e1e2e", fg="white")
        self.wind_label.pack()
        self.wind_entry = tk.Entry(root, font=("B Nazanin", 12))
        self.wind_entry.pack(pady=5)

        # ورودی توان لیزر
        self.laser_label = tk.Label(root, text="توان لیزر (kW):", font=("B Nazanin", 14), bg="#1e1e2e", fg="white")
        self.laser_label.pack()
        self.laser_entry = tk.Entry(root, font=("B Nazanin", 12))
        self.laser_entry.pack(pady=5)

        # دکمه محاسبه
        self.calc_button = tk.Button(root, text="محاسبه توان خروجی", font=("B Nazanin", 14, "bold"), bg="cyan", fg="black", command=self.calculate_power)
        self.calc_button.pack(pady=15)

        # خروجی
        self.result_label = tk.Label(root, text="", font=("B Nazanin", 14, "bold"), bg="#1e1e2e", fg="yellow")
        self.result_label.pack(pady=10)

    def calculate_power(self):
        try:
            wind_speed = float(self.wind_entry.get())
            laser_power = float(self.laser_entry.get())

            # فرمول نمونه (ساده شده)
            output_power = (0.5 * wind_speed**3) + (0.8 * laser_power)

            self.result_label.config(text=f"توان خروجی: {output_power:.2f} kW")
        except ValueError:
            messagebox.showerror("خطا", "لطفا مقادیر عددی معتبر وارد کنید.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LaserWindApp(root)
    root.mainloop()
