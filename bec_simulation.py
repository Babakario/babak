import numpy as np
import matplotlib.pyplot as plt

# --- Physical Parameters ---
# --- پارامترهای فیزیکی ---

# Spatial grid (x-axis)
# x: Defines the spatial domain of the simulation. It's a 1D array representing positions.
# np.linspace(-10, 10, 1000): Creates 1000 points from -10 to 10.
# x (موقعیت): آرایه‌ای از نقاط در فضا برای شبیه‌سازی
x = np.linspace(-10, 10, 1000)  # Spatial domain from -10 to 10 with 1000 points

# Spatial step size (dx)
# dx: The distance between two consecutive points in the spatial grid.
# dx (گام فضایی): فاصله بین نقاط متوالی در شبکه فضایی
dx = x[1] - x[0]  # Grid spacing

# External Potential (V)
# V: Represents the external potential energy landscape. Here, a harmonic potential (V(x) = 0.5 * x^2).
# V (پتانسیل خارجی): پتانسیل هارمونیکی که BEC در آن قرار دارد
V = 0.5 * x**2  # Harmonic potential V(x) = 0.5 * x^2

# Initial wavefunction (psi)
# psi: The initial state of the Bose-Einstein Condensate (BEC) wavefunction.
# Here, a Gaussian wavepacket is used as the initial state.
# psi (تابع موج اولیه): حالت اولیه BEC، معمولاً یک بسته موج گاوسی
psi = np.exp(-x**2)  # Initial Gaussian wavepacket

# --- Normalization of the Wavefunction ---
# --- نرمال‌سازی تابع موج ---
# The wavefunction must be normalized so that the total probability of finding the particle is 1.
# Integral |psi(x)|^2 dx = 1
# نرمال‌سازی: تابع موج باید نرمال شود تا انتگرال مربع قدر مطلق آن برابر با یک باشد (احتمال کل یافتن ذره یک است)
psi = psi / np.sqrt(np.sum(np.abs(psi)**2) * dx) # Normalize psi so that integral |psi|^2 dx = 1

# --- Simulation Parameters ---
# --- پارامترهای شبیه‌سازی ---

# Time step (dt)
# dt: The small increment of time for each step in the simulation.
# dt (گام زمانی): مقدار کوچک افزایش زمان در هر گام شبیه‌سازی
dt = 0.005  # Time step for the evolution

# Final time (t_final)
# t_final: The total duration for which the simulation will run.
# t_final (زمان نهایی): مدت زمان کل شبیه‌سازی
t_final = 2.0  # Total simulation time

# Number of time steps (N_steps)
# N_steps: Total number of discrete time steps to perform.
# N_steps (تعداد گام‌های زمانی): تعداد کل گام‌های زمانی برای اجرای شبیه‌سازی
N_steps = int(t_final / dt)  # Total number of simulation steps

# Interaction strength (g)
# g: Represents the strength of the non-linear interaction term in the Gross-Pitaevskii equation.
#    g > 0 for repulsive interactions, g < 0 for attractive interactions.
#    g = 0 corresponds to a non-interacting BEC (linear Schrödinger equation).
# g (قدرت برهمکنش): پارامتر برهمکنش در معادله گروس-پیتایوسکی، مثبت برای دافعه، منفی برای جاذبه، صفر برای بدون برهمکنش
g = 1.0  # Interaction parameter (g > 0 repulsive, g < 0 attractive, g = 0 non-interacting)

# --- k-space Array (Frequency/Momentum axis) ---
# --- آرایه فضای k (محور فرکانس/تکانه) ---
# k: Represents the wave numbers (momentum multiplied by hbar) corresponding to the spatial grid.
#    It's essential for Fourier transforms, as the kinetic energy operator is simpler in k-space.
# np.fft.fftfreq generates the frequency bins for the FFT.
# k (فضای فرکانس): محور فرکانس یا اعداد موج برای تبدیل فوریه، لازم برای محاسبه انرژی جنبشی
k = 2 * np.pi * np.fft.fftfreq(len(x), d=dx) # Wave numbers for Fourier transform

# --- Optional: Plot Initial State ---
# --- اختیاری: رسم حالت اولیه ---
# This section can be uncommented to visualize the initial probability density.
# plt.plot(x, np.abs(psi)**2)
# plt.title("تراکم احتمال اولیه BEC (Initial BEC probability density)")
# plt.xlabel("x")
# plt.ylabel("|ψ(x)|²")
# plt.grid()
# plt.show() # Ensure this is commented out if you add plotting at the end.

print("BEC simulation script initialized with parameters.")
print(f"Time step (dt): {dt}")
print(f"Final time (t_final): {t_final}")
print(f"Number of steps (N_steps): {N_steps}")
print(f"Interaction strength (g): {g}")

# --- Operators for Split-Step Fourier Method ---
# --- اپراتورها برای روش اسپلیت-استپ فوریه ---
# The Gross-Pitaevskii equation (or Schrödinger eq. if g=0) is split into kinetic and potential parts.
# U(dt) = exp(-i H dt) approx exp(-i K dt/2) exp(-i P dt) exp(-i K dt/2)
# K is kinetic energy operator (diagonal in k-space), P is potential energy operator (diagonal in x-space).

def kinetic_operator_step(psi_k_in, dt_half):
    """
    Applies the kinetic energy operator for half a time step in Fourier space.
    Evolves the wavefunction under the kinetic energy term H_kin = p^2 / (2m) = (hbar k)^2 / (2m).
    In k-space, this is multiplication by exp(-i * (hbar k)^2 / (2m) * dt_half).
    محاسبه نیم گام اپراتور انرژی جنبشی در فضای فوریه.

    Args:
        psi_k_in (np.ndarray): Wavefunction in k-space (Fourier transformed).
        dt_half (float): Half of the time step (dt/2).

    Returns:
        np.ndarray: Wavefunction in k-space after applying the kinetic operator.
    """
    # Assumes hbar=1 and m=1 for simplicity. These can be added as parameters if needed.
    # The kinetic energy operator in k-space (after Fourier transform) is multiplication by -0.5 * k^2.
    # psi_k_out = exp(-0.5j * k^2 * dt_half) * psi_k_in
    return np.exp(-0.5j * (k**2) * dt_half) * psi_k_in

def potential_operator_step(psi_x_in, V_potential, g_interaction, dt_full):
    """
    Applies the potential energy and interaction operator for a full time step in real space.
    Evolves the wavefunction under the potential energy term H_pot = V(x) + g * |psi(x)|^2.
    In real space (x-space), this is multiplication by exp(-i * (V(x) + g*|psi(x)|^2) * dt_full).
    محاسبه گام کامل اپراتور انرژی پتانسیل و برهمکنش در فضای حقیقی.

    Args:
        psi_x_in (np.ndarray): Wavefunction in real space (x-space).
        V_potential (np.ndarray): External potential V(x).
        g_interaction (float): Interaction strength g.
        dt_full (float): Full time step (dt).

    Returns:
        np.ndarray: Wavefunction in real space after applying the potential and interaction operator.
    """
    # The potential operator (including interaction) in x-space is multiplication by (V(x) + g*|psi(x)|^2).
    # psi_x_out = exp(-1j * (V_potential + g_interaction * np.abs(psi_x_in)**2) * dt_full) * psi_x_in
    return np.exp(-1j * (V_potential + g_interaction * np.abs(psi_x_in)**2) * dt_full) * psi_x_in

print("Split-step Fourier method operators defined.")

# --- Time Evolution Loop (Split-Step Fourier Method) ---
# --- حلقه تکامل زمانی (روش اسپلیت-استپ فوریه) ---
print("Starting time evolution...")

# Initial wavefunction in k-space (momentum space)
# Transform psi from real space (x) to k-space using Fast Fourier Transform (FFT).
# تابع موج اولیه در فضای k (فضای تکانه)
psi_k = np.fft.fft(psi)

# Loop over the total number of time steps
# حلقه بر روی تعداد کل گام‌های زمانی
for i in range(N_steps):
    # The Split-Step Fourier Method alternates between real and k-space.
    # Step 1: Apply half of the kinetic energy operator in k-space.
    # مرحله ۱: اعمال نیم‌گام اپراتور انرژی جنبشی در فضای k
    psi_k = kinetic_operator_step(psi_k, dt / 2.0)

    # Step 2: Transform the wavefunction from k-space back to real space (x-space) using Inverse FFT.
    # مرحله ۲: تبدیل تابع موج از فضای k به فضای حقیقی (فضای x) با استفاده از تبدیل فوریه معکوس
    psi_x = np.fft.ifft(psi_k)

    # Step 3: Apply the full potential energy and interaction operator in real space.
    # مرحله ۳: اعمال گام کامل اپراتور انرژی پتانسیل و برهمکنش در فضای حقیقی
    psi_x = potential_operator_step(psi_x, V, g, dt)

    # Step 4: Transform the wavefunction from real space back to k-space using FFT.
    # مرحله ۴: تبدیل تابع موج از فضای حقیقی به فضای k با استفاده از تبدیل فوریه
    psi_k = np.fft.fft(psi_x)

    # Step 5: Apply the second half of the kinetic energy operator in k-space.
    # This completes one full time step dt using the symmetric split-step formula.
    # مرحله ۵: اعمال نیم‌گام دیگر اپراتور انرژی جنبشی در فضای k
    psi_k = kinetic_operator_step(psi_k, dt / 2.0)

    # (Optional) Renormalization at each step:
    # (اختیاری) نرمال‌سازی مجدد در هر گام:
    # For numerical stability or to strictly enforce probability conservation,
    # the wavefunction can be renormalized at each time step.
    # However, the split-step method is unitary and should conserve norm well for small dt.
    # اگرچه روش اسپلیت-استپ یونیتی است و باید نرم را به خوبی حفظ کند، می‌توان برای اطمینان آن را در هر گام نرمال کرد.
    # current_psi_x = np.fft.ifft(psi_k)
    # norm_factor = np.sqrt(np.sum(np.abs(current_psi_x)**2) * dx)
    # psi_k = np.fft.fft(current_psi_x / norm_factor)


# Transform the final wavefunction from k-space back to real space for plotting or analysis.
# تبدیل تابع موج نهایی از فضای k به فضای حقیقی برای رسم یا تحلیل نتایج
psi_final_x = np.fft.ifft(psi_k)

# Normalize the final wavefunction.
# This is important for consistency, especially if renormalization was not done in the loop.
# It ensures that the final probability density integrates to 1.
# نرمال‌سازی تابع موج نهایی: تضمین می‌کند که انتگرال چگالی احتمال نهایی برابر با یک است.
psi_final_x = psi_final_x / np.sqrt(np.sum(np.abs(psi_final_x)**2) * dx)


print("Time evolution finished.")
# Verify the norm of the final wavefunction. It should be very close to 1.0.
# بررسی نرم تابع موج نهایی، باید بسیار نزدیک به ۱.۰ باشد
print(f"Final psi norm: {np.sum(np.abs(psi_final_x)**2)*dx}") # Should be close to 1.0

# --- Plotting Results ---
# --- رسم نتایج ---

plt.figure(figsize=(10, 6)) # Create a figure for the plot

# Plot initial probability density |psi(x, t=0)|^2
# رسم تراکم احتمال اولیه |ψ(x, t=0)|²
plt.plot(x, np.abs(psi)**2, label="تراکم احتمال اولیه |ψ(x, t=0)|² (Initial)")

# Plot final probability density |psi(x, t=t_final)|^2
# رسم تراکم احتمال نهایی |ψ(x, t=t_final)|²
plt.plot(x, np.abs(psi_final_x)**2, label=f"تراکم احتمال نهایی |ψ(x, t={t_final})|² (Final)", linestyle='--')

plt.title("تکامل زمانی چگالی احتمال BEC در پتانسیل هارمونیکی (Time Evolution of BEC Probability Density)")
plt.xlabel("x (موقعیت - Position)")
plt.ylabel("|ψ(x,t)|² (چگالی احتمال - Probability Density)")
plt.legend() # Show legend
plt.grid(True) # Show grid
plt.savefig("bec_evolution.png") # Save the plot as an image file
# plt.show() # Comment out plt.show() for non-interactive environments (e.g., servers, scripts)
# plt.show() را کامنت کنید اگر در محیط غیرتعاملی اجرا می‌کنید

print("Plotting complete. Image saved to bec_evolution.png")
