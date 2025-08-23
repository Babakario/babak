import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import sympy as sp
import numpy as np

# --- analytic area calculation (exact) ---
x = sp.symbols('x', real=True)

# Ideal right triangle (base 13, height 5)
y_true = 5 - sp.Rational(5,13)*x
area_ideal = sp.Rational(13*5, 2)  # 32.5

# Two pieces' hypotenuse segments
y1 = 5 - sp.Rational(2,5)*x                # on [0,5]
y2 = sp.Rational(39,8) - sp.Rational(3,8)*x  # on (5,13]

A1 = sp.integrate(y_true - y1, (x, 0, 5))
A2 = sp.integrate(y_true - y2, (x, 5, 13))
A_total = sp.simplify(A1 + A2)

# Convert to floats
area_ideal_f = float(area_ideal)
A1_f, A2_f, A_total_f = map(float, (A1, A2, A_total))

# --- Polygons for Plotting ---

# Configuration A (gap): concave boundary from the analytic section
# Piece 1: Trapezoid with vertices (0,0), (5,0), (5,3), (0,5)
poly_A_gap = np.array([[0,0], [5,0], [5,3], [0,5]])
# Piece 2: Right triangle with vertices (5,0), (13,0), (5,3)
poly_B_gap = np.array([[5,0], [13,0], [5,3]])

# Configuration B (overlap): convex boundary
# For this case, we define new pieces that create a convex boundary.
# The hypotenuse is split at x=8, with the joining point at (8,2),
# which is above the ideal hypotenuse, creating an overlap.
# Piece 1: Trapezoid (0,0)-(8,0)-(8,2)-(0,5)
poly_A_overlap = np.array([[0,0], [8,0], [8,2], [0,5]])
# Piece 2: Right triangle (8,0)-(13,0)-(8,2)
poly_B_overlap = np.array([[8,0], [13,0], [8,2]])


# --- Plotting ---
x_line = np.linspace(0, 13, 200)
y_line = 5 - (5/13) * x_line

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot for Configuration A (gap)
axes[0].plot(x_line, y_line, 'k--', label='Ideal hypotenuse', zorder=2)
axes[0].add_patch(Polygon(poly_A_gap, closed=True, alpha=0.6, hatch='//', facecolor='C0', label='Piece 1'))
axes[0].add_patch(Polygon(poly_B_gap, closed=True, alpha=0.6, hatch='\\\\', facecolor='C1', label='Piece 2'))
# Plot the actual hypotenuses of the two pieces
axes[0].plot([0, 5], [5, 3], 'r-', linewidth=2, label='Actual boundary', zorder=3)
axes[0].plot([5, 13], [3, 0], 'r-', linewidth=2, zorder=3)
axes[0].set_title('Configuration A: Concave Boundary (Gap)')
axes[0].set_xlim(-0.5, 13.5)
axes[0].set_ylim(-0.5, 5.5)
axes[0].legend()
axes[0].set_aspect('equal', adjustable='box')
axes[0].axis('off')

# Plot for Configuration B (overlap)
axes[1].plot(x_line, y_line, 'k--', label='Ideal hypotenuse', zorder=2)
axes[1].add_patch(Polygon(poly_A_overlap, closed=True, alpha=0.6, hatch='//', facecolor='C0', label='Piece 1'))
axes[1].add_patch(Polygon(poly_B_overlap, closed=True, alpha=0.6, hatch='\\\\', facecolor='C1', label='Piece 2'))
# Plot the actual hypotenuses of the two pieces
axes[1].plot([0, 8], [5, 2], 'g-', linewidth=2, label='Actual boundary', zorder=3)
axes[1].plot([8, 13], [2, 0], 'g-', linewidth=2, zorder=3)
axes[1].set_title('Configuration B: Convex Boundary (Overlap)')
axes[1].set_xlim(-0.5, 13.5)
axes[1].set_ylim(-0.5, 5.5)
axes[1].legend()
axes[1].set_aspect('equal', adjustable='box')
axes[1].axis('off')

plt.tight_layout()
plt.show()

# --- Analytic area calculation for overlap case ---
y1_o = 5 - sp.Rational(3, 8) * x
y2_o = 2 - sp.Rational(2, 5) * (x - 8)
A1_o = sp.integrate(y1_o - y_true, (x, 0, 8))
A2_o = sp.integrate(y2_o - y_true, (x, 8, 13))
A_total_overlap = sp.simplify(A1_o + A2_o)

# --- Print Results ---
print(f"Ideal Area: {area_ideal_f}")
print("-" * 20)
print(f"Gap Area (Symbolic): {A_total}")
print(f"Gap Area (Float): {A_total_f}")
print("-" * 20)
print(f"Overlap Area (Symbolic): {A_total_overlap}")
print(f"Overlap Area (Float): {float(A_total_overlap)}")
