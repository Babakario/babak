# generator_power_estimator.py

# Appliance power ratings (in Watts)
# Using starting wattage for devices with motors, running wattage for others.
POWER_RATINGS = {
    "refrigerator_starting": 2000,  # Typical starting wattage
    "ac_12000_btu_starting": 4500,  # Typical starting wattage
    "led_light_running": 10,        # Running wattage
    "light_elevator_starting": 7000, # Typical starting wattage for a light elevator
}

# User's appliance counts
APPLIANCE_COUNTS = {
    "refrigerators": 3,
    "ac_units_12000_btu": 2,
    "led_lights": 20,
    "elevators": 1,
}

# User's generator preferences
GENERATOR_PREFERENCES = {
    "fuel_type": "Gasoline (بنزینی)",
    "noise_level": "Silent (بی‌صدا)",
    "portability": "Fixed (ثابت)",
    "start_system": "Electric (الکتریکی)",
}

def calculate_total_power(ratings, counts):
    """Calculates the total estimated power requirement."""
    total_power = 0
    total_power += counts["refrigerators"] * ratings["refrigerator_starting"]
    total_power += counts["ac_units_12000_btu"] * ratings["ac_12000_btu_starting"]
    total_power += counts["led_lights"] * ratings["led_light_running"]
    total_power += counts["elevators"] * ratings["light_elevator_starting"]
    return total_power

def main():
    """Main function to calculate and display power estimation and preferences."""
    print("Generator Power Estimation")
    print("--------------------------")

    # Calculate total power
    total_watts = calculate_total_power(POWER_RATINGS, APPLIANCE_COUNTS)
    total_kilowatts = total_watts / 1000

    print(f"Appliance Counts:")
    for appliance, count in APPLIANCE_COUNTS.items():
        print(f"  - {appliance.replace('_', ' ').capitalize()}: {count}")
    print("\nEstimated Total Power Requirement:")
    print(f"  - {total_watts} Watts")
    print(f"  - {total_kilowatts} kW")

    # Adding a 20-25% buffer as is generally recommended
    recommended_kilowatts_min = total_kilowatts * 1.20
    recommended_kilowatts_max = total_kilowatts * 1.25
    print(f"\nRecommended Generator Size (including a 20-25% buffer):")
    print(f"  - Approximately {recommended_kilowatts_min:.2f} kW to {recommended_kilowatts_max:.2f} kW")

    print("\nGenerator Preferences:")
    for key, value in GENERATOR_PREFERENCES.items():
        print(f"  - {key.replace('_', ' ').capitalize()}: {value}")

    print("\nNotes:")
    print("  - Power ratings are estimates. Starting wattage for motors can vary significantly.")
    print("  - This calculation assumes worst-case scenario where all motorized appliances start simultaneously.")
    print("  - It's always best to consult with an electrician for precise sizing.")

if __name__ == "__main__":
    main()
