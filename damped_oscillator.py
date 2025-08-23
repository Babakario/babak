import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- پارامترهای مدل ---
# پارامترها در یک دیکشنری برای سازماندهی بهتر و انتقال آسان به توابع گروه بندی شده‌اند
MODEL_PARAMS = {
    "m1": 1.0,      # جرم ۱
    "m2": 1.0,      # جرم ۲
    "k": 5.0,       # ضریب سختی خطی فنر
    "alpha": 1.0,   # ضریب سختی غیرخطی فنر (عامل غیرخطی)
    "c": 0.5,       # ضریب دمپینگ
    "A": 1.0,       # دامنه نیروی خارجی
    "omega": 2.0,   # فرکانس نیروی خارجی
}

def system_equations(t, y, params):
    """
    سیستم معادلات دیفرانسیل مرتبه اول برای دو جرم متصل.
    y: [x1, v1, x2, v2]
    t: زمان
    params: دیکشنری پارامترهای مدل
    """
    x1, v1, x2, v2 = y
    # استخراج پارامترها از دیکشنری
    m1, m2, k, alpha, c, A, omega = params.values()

    # جابجایی نسبی بین دو جرم
    dx = x2 - x1

    # محاسبه نیروها
    F_spring = k * dx + alpha * dx**3  # نیروی فنر غیرخطی (مدل دافینگ)
    F_damping1 = -c * v1               # نیروی دمپینگ روی جرم ۱
    F_damping2 = -c * v2               # نیروی دمپینگ روی جرم ۲
    F_ext1 = A * np.sin(omega * t)     # نیروی خارجی سینوسی روی جرم ۱
    F_ext2 = 0                         # فرض شده نیروی خارجی فقط به جرم ۱ وارد می‌شود

    # محاسبه شتاب‌ها بر اساس قانون دوم نیوتن (a = F/m)
    a1 = (F_spring + F_damping1 + F_ext1) / m1
    a2 = (-F_spring + F_damping2 + F_ext2) / m2

    return [v1, a1, v2, a2]

def calculate_energies(sol, params):
    """انرژی‌های جنبشی، پتانسیل و کل سیستم را محاسبه می‌کند."""
    m1, m2, k, alpha, *_ = params.values()
    x1, v1, x2, v2 = sol.y
    dx = x2 - x1

    KE1 = 0.5 * m1 * v1**2  # انرژی جنبشی جرم ۱
    KE2 = 0.5 * m2 * v2**2  # انرژی جنبشی جرم ۲
    PE = 0.5 * k * dx**2 + 0.25 * alpha * dx**4  # انرژی پتانسیل فنر
    total_energy = KE1 + KE2 + PE
    return total_energy

def plot_results(sol, total_energy):
    """نتایج شبیه‌سازی شامل مکان، انرژی و نمودار فاز را رسم می‌کند."""
    t = sol.t
    x1, v1, x2, v2 = sol.y

    # --- رسم نمودارهای مکان و انرژی ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('تحلیل دینامیکی سیستم دو جرمی', fontsize=16)

    # نمودار مکان جرم‌ها
    ax1.plot(t, x1, label='مکان جرم ۱ ($x_1$)')
    ax1.plot(t, x2, label='مکان جرم ۲ ($x_2$)')
    ax1.set_xlabel('زمان (t)')
    ax1.set_ylabel('مکان (x)')
    ax1.set_title('مکان جرم‌ها در طول زمان')
    ax1.legend()
    ax1.grid(True)

    # نمودار انرژی کل
    ax2.plot(t, total_energy, label='انرژی کل', color='r')
    ax2.set_xlabel('زمان (t)')
    ax2.set_ylabel('انرژی (E)')
    ax2.set_title('انرژی کل سیستم در طول زمان')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    # --- رسم نمودار فاز ---
    plt.figure(figsize=(7, 6))
    plt.plot(x1, v1, label='جرم ۱')
    plt.plot(x2, v2, label='جرم ۲', alpha=0.8)
    plt.xlabel('مکان (x)')
    plt.ylabel('سرعت (v)')
    plt.title('نمودار فضای فاز سیستم')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    """
    تابع اصلی برای اجرای شبیه‌سازی و نمایش نتایج.
    """
    # شرایط اولیه: [x1_0, v1_0, x2_0, v2_0]
    y0 = [0.0, 0.0, 1.0, 0.0]

    # بازه زمانی برای حل عددی
    t_span = (0, 50)
    t_eval = np.linspace(t_span[0], t_span[1], 4000)

    # حل معادلات دیفرانسیل با استفاده از solve_ivp
    # از یک تابع لامبدا برای ارسال پارامترهای اضافی به تابع معادلات استفاده می‌شود
    sol = solve_ivp(
        lambda t, y: system_equations(t, y, MODEL_PARAMS),
        t_span,
        y0,
        t_eval=t_eval,
        dense_output=True  # برای داشتن یک حل پیوسته و نرم
    )

    # محاسبه انرژی سیستم
    total_energy = calculate_energies(sol, MODEL_PARAMS)

    # رسم نتایج
    plot_results(sol, total_energy)

if __name__ == "__main__":
    main()
