from flask import Blueprint, render_template, request

# Create a Blueprint for the calculator
calculator_bp = Blueprint('calculator', __name__, template_folder='../templates')

def calculate_power(wind_speed, laser_power):
    """Calculates the output power based on wind speed and laser power."""
    try:
        # The formula from the original Tkinter app
        output_power = (0.5 * float(wind_speed)**3) + (0.8 * float(laser_power))
        return output_power
    except (ValueError, TypeError):
        return None

@calculator_bp.route('/calculator', methods=['GET', 'POST'])
def calculator():
    if request.method == 'POST':
        wind_speed_str = request.form.get('wind_speed')
        laser_power_str = request.form.get('laser_power')

        # Basic validation to ensure inputs are not empty
        if not wind_speed_str or not laser_power_str:
            error = "لطفا هر دو مقدار را وارد کنید."
            return render_template('calculator.html', error=error)

        output_power = calculate_power(wind_speed_str, laser_power_str)

        if output_power is not None:
            result = f"{output_power:.2f} kW"
            return render_template('calculator.html', result=result, wind_speed=wind_speed_str, laser_power=laser_power_str)
        else:
            error = "لطفا مقادیر عددی معتبر وارد کنید."
            return render_template('calculator.html', error=error, wind_speed=wind_speed_str, laser_power=laser_power_str)

    # For GET requests, just display the form
    return render_template('calculator.html')
