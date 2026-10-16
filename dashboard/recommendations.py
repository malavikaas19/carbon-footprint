
def generate_recommendations(
    electricity_kwh,
    vehicles,
    distance_km,
    solar_kwh,
    ac_hours,
    waste_kg,
):
    recommendations = []

    if electricity_kwh > 100:
        recommendations.append({
            "title": "Reduce Electricity Consumption",
            "message": (
                "Switch off unused equipment, use LED lighting, "
                "and choose energy-efficient appliances."
            ),
        })

    if electricity_kwh > 0 and solar_kwh == 0:
        recommendations.append({
            "title": "Explore Renewable Energy",
            "message": (
                "Consider rooftop solar or renewable electricity "
                "if practical for your location."
            ),
        })

    if ac_hours >= 4:
        recommendations.append({
            "title": "Optimise Air Conditioning",
            "message": (
                "Use a moderate thermostat setting, clean AC filters, "
                "and switch cooling off when rooms are unoccupied."
            ),
        })

    if vehicles > 0 and distance_km > 0:
        recommendations.append({
            "title": "Reduce Transport Emissions",
            "message": (
                "Consider public transport, carpooling, walking, "
                "cycling, or combining journeys."
            ),
        })

    if waste_kg > 0:
        recommendations.append({
            "title": "Reduce Waste",
            "message": (
                "Reuse suitable items and separate recyclable "
                "or compostable waste where possible."
            ),
        })

    if solar_kwh > 0:
        recommendations.append({
            "title": "Keep Using Solar Energy",
            "message": (
                "Continue using solar electricity to reduce "
                "reliance on grid electricity."
            ),
        })

    if not recommendations:
        recommendations.append({
            "title": "Keep Tracking Your Carbon Footprint",
            "message": (
                "Record your electricity, transport, and waste "
                "regularly to identify ways to reduce emissions."
            ),
        })

    return recommendations
