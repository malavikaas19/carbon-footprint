
ELECTRICITY_FACTOR = 0.70
TRANSPORT_FACTOR = 0.12
WASTE_FACTOR = 0.50
AC_POWER_KW = 2.0


def calculate_emissions(
    electricity_kwh,
    vehicles,
    distance_km,
    solar_kwh,
    ac_hours,
    waste_kg,
):
    ac_electricity = ac_hours * AC_POWER_KW

    grid_electricity = max(
        0.0,
        electricity_kwh + ac_electricity - solar_kwh,
    )

    electricity_emissions = grid_electricity * ELECTRICITY_FACTOR
    transport_emissions = vehicles * distance_km * TRANSPORT_FACTOR
    waste_emissions = waste_kg * WASTE_FACTOR

    return {
        "Electricity": electricity_emissions,
        "Transportation": transport_emissions,
        "Waste": waste_emissions,
        "Total": (
            electricity_emissions
            + transport_emissions
            + waste_emissions
        ),
        "Grid electricity": grid_electricity,
        "AC electricity": ac_electricity,
    }
