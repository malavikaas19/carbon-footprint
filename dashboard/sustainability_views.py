
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import CameraDetection, WasteImpact, EcoAction
from .sustainability import suggest_waste, calculate_waste_scenario


ACTION_POINTS = {
    "recycling": 10,
    "reusable": 10,
    "energy": 15,
    "transport": 15,
    "composting": 10,
    "water": 5,
}

VALID_DISPOSAL_METHODS = {
    "recycle",
    "compost",
    "reuse",
    "landfill",
    "not_recorded",
}

NON_WASTE_LABELS = {
    "person", "bicycle", "car", "motorcycle", "airplane",
    "bus", "train", "truck", "boat", "bird", "cat", "dog",
    "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe",
}


@require_http_methods(["GET", "POST"])
def sustainability_dashboard(request):
    error = None

    # Handle submitted forms
    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "save_waste":
            try:
                material = request.POST.get("material", "unknown")
                weight_kg = float(request.POST.get("weight_kg", "0"))
                quantity = int(request.POST.get("quantity", "1"))
                disposal_method = request.POST.get(
                    "disposal_method", "not_recorded"
                )

                if quantity < 1:
                    raise ValueError("Quantity must be at least one.")

                if not 0 < weight_kg <= 10000:
                    raise ValueError(
                        "Weight must be greater than 0 and no more than 10,000 kg."
                    )

                if disposal_method not in VALID_DISPOSAL_METHODS:
                    raise ValueError("Choose a valid disposal method.")

                impact = calculate_waste_scenario(
                    material, weight_kg, disposal_method
                )

                scan_id = request.POST.get("camera_scan_id")
                scan = None
                if scan_id:
                    scan = CameraDetection.objects.filter(
                        pk=scan_id
                    ).first()

                WasteImpact.objects.create(
                    camera_scan=scan,
                    material=material,
                    quantity=quantity,
                    estimated_weight_kg=weight_kg,
                    disposal_method=disposal_method,
                    baseline_emissions_kg=impact["baseline_emissions_kg"],
                    scenario_emissions_kg=impact["scenario_emissions_kg"],
                    estimated_avoided_emissions_kg=impact[
                        "estimated_avoided_emissions_kg"
                    ],
                )

                messages.success(
                    request,
                    "Waste record saved. Carbon figures are illustrative estimates.",
                )
                return redirect("sustainability")

            except (ValueError, TypeError) as exc:
                error = str(exc)

        elif action == "add_action":
            action_type = request.POST.get("action_type", "")
            description = request.POST.get("description", "").strip()

            if action_type not in ACTION_POINTS:
                error = "Please choose a valid sustainability action."
            else:
                EcoAction.objects.create(
                    action_type=action_type,
                    description=description[:250],
                    points=ACTION_POINTS[action_type],
                    completed=True,
                )
                messages.success(request, "Sustainability action recorded.")
                return redirect("sustainability")

        else:
            error = "Unknown form action."

    # Latest saved camera scans
    scans = CameraDetection.objects.all()[:10]
    latest_scan = scans.first()
    suggestions = []

    # Suggest categories for detected objects, excluding common non-waste classes
    if latest_scan:
        for detection in (latest_scan.detections or []):
            label = str(detection.get("name", "unknown")).strip().lower()

            if label in NON_WASTE_LABELS:
                continue

            suggestion = suggest_waste(label)
            suggestions.append({
                "name": label.title(),
                "confidence": detection.get("confidence", 0),
                "material": suggestion["material"],
                "category": suggestion["category"],
                "instruction": suggestion["instruction"],
                "needs_verification": suggestion["needs_verification"],
            })

    # Sustainability action score
    completed_actions = EcoAction.objects.filter(completed=True)
    total_points = (
        completed_actions.aggregate(total=Sum("points"))["total"] or 0
    )
    action_count = completed_actions.count()
    sustainability_score = min(100, total_points)

    # Waste record summaries
    waste_records = WasteImpact.objects.all()[:20]

    total_avoided = (
        WasteImpact.objects.aggregate(
            total=Sum("estimated_avoided_emissions_kg")
        )["total"] or 0
    )
    total_waste_kg = (
        WasteImpact.objects.aggregate(
            total=Sum("estimated_weight_kg")
        )["total"] or 0
    )

    # Chart data: latest 10 records, ordered oldest to newest
    chart_records = list(WasteImpact.objects.all()[:10])
    chart_records.reverse()

    carbon_chart = {
        "labels": [
            record.created_at.strftime("%d %b %H:%M")
            for record in chart_records
        ],
        "baseline": [
            record.baseline_emissions_kg
            for record in chart_records
        ],
        "scenario": [
            record.scenario_emissions_kg
            for record in chart_records
        ],
    }

    context = {
        "error": error,
        "suggestions": suggestions,
        "latest_scan": latest_scan,
        "scans": scans,
        "waste_records": waste_records,
        "actions": completed_actions[:20],
        "total_points": total_points,
        "action_count": action_count,
        "sustainability_score": sustainability_score,
        "total_avoided": total_avoided,
        "total_waste_kg": total_waste_kg,
        "carbon_chart": carbon_chart,
    }

    return render(
        request,
        "dashboard/sustainability.html",
        context,
    )
