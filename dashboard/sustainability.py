
# dashboard/sustainability.py

WASTE_LABELS = {
    "bottle": {
        "material": "plastic",
        "category": "Potential plastic recycling",
        "instruction": (
            "Check whether the bottle is plastic and confirm "
            "your local recycling rules."
        ),
    },
    "cup": {
        "material": "unknown",
        "category": "Needs verification",
        "instruction": (
            "Check whether the cup is paper, plastic, foam, "
            "or a mixed material."
        ),
    },
    "wine glass": {
        "material": "glass",
        "category": "Potential glass recycling",
        "instruction": (
            "Check your local facility's rules. Drinking glasses "
            "may not be accepted with bottle glass."
        ),
    },
    "banana": {
        "material": "organic",
        "category": "Potential composting",
        "instruction": (
            "Compost where suitable facilities are available."
        ),
    },
    "apple": {
        "material": "organic",
        "category": "Potential composting",
        "instruction": (
            "Compost where suitable facilities are available."
        ),
    },
    "book": {
        "material": "paper",
        "category": "Potential paper recycling",
        "instruction": (
            "Reuse the book if possible, or check local paper "
            "recycling requirements."
        ),
    },
    "cell phone": {
        "material": "ewaste",
        "category": "Electronic waste",
        "instruction": (
            "Use an authorized e-waste collection service. "
            "Do not put electronics in ordinary recycling bins."
        ),
    },
    "can": {
        "material": "metal",
        "category": "Potential metal recycling",
        "instruction": (
            "Verify the can material and local recycling rules."
        ),
    },
    "cardboard": {
        "material": "paper",
        "category": "Potential cardboard recycling",
        "instruction": (
            "Keep cardboard clean and dry and check local rules."
        ),
    },
    "paper": {
        "material": "paper",
        "category": "Potential paper recycling",
        "instruction": (
            "Check that the paper is clean and accepted locally."
        ),
    },
}


def suggest_waste(label):
    """Suggest a possible waste category from a detected object label."""
    normalized = str(label).strip().lower()
    suggestion = WASTE_LABELS.get(normalized)

    if suggestion:
        return {
            **suggestion,
            "needs_verification": True,
        }

    return {
        "material": "unknown",
        "category": "Needs verification",
        "instruction": (
            "Confirm the object's material manually before "
            "choosing a disposal method."
        ),
        "needs_verification": True,
    }


# Illustrative demonstration factors only.
# Replace with documented, location-appropriate lifecycle factors
# before using these values as real-world carbon estimates.
DEMO_FACTORS = {
    "plastic": 1.0,
    "paper": 0.5,
    "metal": 1.0,
    "glass": 0.2,
    "organic": 0.3,
    "ewaste": 1.0,
    "general": 0.2,
    "unknown": 0.0,
}

SCENARIO_FACTORS = {
    "recycle": 0.4,
    "compost": 0.3,
    "reuse": 0.2,
    "landfill": 1.0,
    "not_recorded": 1.0,
}


def calculate_waste_scenario(material, weight_kg, disposal_method):
    """Calculate illustrative scenario values for the dashboard."""
    if material not in DEMO_FACTORS:
        raise ValueError("Please choose a supported material.")

    if weight_kg <= 0:
        raise ValueError("Weight must be greater than zero.")

    if disposal_method not in SCENARIO_FACTORS:
        raise ValueError("Choose a valid disposal method.")

    baseline = weight_kg * DEMO_FACTORS[material]
    scenario = weight_kg * SCENARIO_FACTORS[disposal_method]
    avoided = max(0.0, baseline - scenario)

    return {
        "baseline_emissions_kg": round(baseline, 3),
        "scenario_emissions_kg": round(scenario, 3),
        "estimated_avoided_emissions_kg": round(avoided, 3),
        "is_demo_estimate": True,
    }
