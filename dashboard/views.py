
import logging
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import CarbonCalculation, CameraDetection
from .carbon_calculator import calculate_emissions
from .computer_vision import detect_objects
from .recommendations import generate_recommendations


logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


def validate_image(uploaded_file):
    if not uploaded_file:
        return "No image was received."

    extension = Path(uploaded_file.name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return "Use JPG, JPEG, PNG, or WebP images."

    if uploaded_file.size > MAX_IMAGE_SIZE:
        return "Image size must not exceed 10 MB."

    return None


def make_recommendations(result, inputs):
    """Generate personalized carbon-reduction recommendations."""
    try:
        return generate_recommendations(
            electricity_kwh=inputs["electricity"],
            vehicles=inputs["vehicles"],
            distance_km=inputs["distance_km"],
            solar_kwh=inputs["solar_kwh"],
            ac_hours=inputs["ac_hours"],
            waste_kg=inputs["waste_kg"],
        )
    except Exception:
        logger.exception("Recommendation generation failed.")
        return [
            {
                "title": "Keep Tracking Your Carbon Footprint",
                "message": (
                    "Continue tracking your electricity, transport, "
                    "and waste to find ways to reduce emissions."
                ),
            }
        ]




def home(request):
    result = None
    error = None

    saved_emissions = 0
    reduced_emissions = 0
    reduction_percent = 20

    grid_electricity = None
    ac_electricity = None

    uploaded_image_url = None
    annotated_image_url = None
    object_counts = {}
    detections = []
    total_objects = 0
    recommendations = []

    inputs = {
        "electricity": 100.0,
        "vehicles": 1,
        "distance_km": 10.0,
        "solar_kwh": 0.0,
        "ac_hours": 2.0,
        "waste_kg": 1.0,
    }

    if request.method == "POST":
        action = request.POST.get("action", "calculate")

        if action == "calculate":
            try:
                inputs = {
                    "electricity": float(
                        request.POST.get("electricity", 100)
                    ),
                    "vehicles": int(
                        request.POST.get("vehicles", 1)
                    ),
                    "distance_km": float(
                        request.POST.get("distance_km", 10)
                    ),
                    "solar_kwh": float(
                        request.POST.get("solar_kwh", 0)
                    ),
                    "ac_hours": float(
                        request.POST.get("ac_hours", 2)
                    ),
                    "waste_kg": float(
                        request.POST.get("waste_kg", 1)
                    ),
                }

                if any(value < 0 for value in inputs.values()):
                    raise ValueError("Values cannot be negative.")

                result = calculate_emissions(
                    electricity_kwh=inputs["electricity"],
                    vehicles=inputs["vehicles"],
                    distance_km=inputs["distance_km"],
                    solar_kwh=inputs["solar_kwh"],
                    ac_hours=inputs["ac_hours"],
                    waste_kg=inputs["waste_kg"],
                )

                total = float(result["Total"])
                saved_emissions = total * reduction_percent / 100
                reduced_emissions = total - saved_emissions

                grid_electricity = result.get("Grid electricity")
                ac_electricity = result.get("AC electricity")

                CarbonCalculation.objects.create(
                    electricity=inputs["electricity"],
                    vehicles=inputs["vehicles"],
                    distance_km=inputs["distance_km"],
                    solar_kwh=inputs["solar_kwh"],
                    ac_hours=inputs["ac_hours"],
                    waste_kg=inputs["waste_kg"],
                    total_emissions=total,
                    reduction_percent=reduction_percent,
                    reduced_emissions=reduced_emissions,
                    saved_emissions=saved_emissions,
                )

                recommendations = make_recommendations(result, inputs)

            except (ValueError, TypeError, KeyError) as exc:
                error = f"Invalid calculator input: {exc}"

            except Exception:
                logger.exception("Carbon calculation failed.")
                error = "Calculation failed. Check the Django terminal."

        elif action == "detect_image":
            uploaded_file = request.FILES.get("image")
            validation_error = validate_image(uploaded_file)

            if validation_error:
                error = validation_error
            else:
                try:
                    original_name = (
                        f"uploads/{uuid.uuid4().hex}"
                        f"{Path(uploaded_file.name).suffix.lower()}"
                    )

                    saved_name = default_storage.save(
                        original_name, uploaded_file
                    )

                    source_path = default_storage.path(saved_name)

                    annotated_name = (
                        f"annotated/{uuid.uuid4().hex}.jpg"
                    )
                    annotated_path = (
                        Path(settings.MEDIA_ROOT) / annotated_name
                    )
                    annotated_path.parent.mkdir(
                        parents=True, exist_ok=True
                    )

                    detection_result = detect_objects(
                        source_path,
                        str(annotated_path),
                    )

                    uploaded_image_url = default_storage.url(saved_name)
                    annotated_image_url = (
                        settings.MEDIA_URL + annotated_name
                    )

                    object_counts = detection_result.get(
                        "object_counts", {}
                    )
                    detections = detection_result.get("detections", [])
                    total_objects = detection_result.get(
                        "total_objects", len(detections)
                    )

                except Exception:
                    logger.exception("Uploaded image detection failed.")
                    error = (
                        "Image detection failed. "
                        "Check the Django terminal."
                    )

    context = {
        "result": result,
        "saved_emissions": saved_emissions,
        "reduced_emissions": reduced_emissions,
        "reduction_percent": reduction_percent,
        "grid_electricity": grid_electricity,
        "ac_electricity": ac_electricity,
        "uploaded_image_url": uploaded_image_url,
        "annotated_image_url": annotated_image_url,
        "object_counts": object_counts,
        "detections": detections,
        "total_objects": total_objects,
        "recommendations": recommendations,
        "saved_calculations": CarbonCalculation.objects.all()[:20],
        "camera_history": CameraDetection.objects.all()[:20],
        "error": error,
        "footprint_status": (
            "Calculated" if result is not None else "Not calculated"
        ),
    }

    return render(request, "dashboard/home.html", context)


def recommendations(request):
    latest = CarbonCalculation.objects.order_by("-created_at").first()

    if latest:
        items = generate_recommendations(
            electricity_kwh=latest.electricity,
            vehicles=latest.vehicles,
            distance_km=latest.distance_km,
            solar_kwh=latest.solar_kwh,
            ac_hours=latest.ac_hours,
            waste_kg=latest.waste_kg,
        )
    else:
        items = [
            {
                "title": "Reduce Electricity Consumption",
                "message": "Switch off unused appliances and use LED lights.",
            },
            {
                "title": "Choose Sustainable Transport",
                "message": "Walk, cycle, carpool, or use public transport.",
            },
            {
                "title": "Reduce Waste",
                "message": "Reuse items and separate recyclable waste.",
            },
        ]

    return render(
        request,
        "dashboard/recommendations.html",
        {
            "latest": latest,
            "recommendations": items,
        },
    )

@require_POST
def camera_detect(request):
    """Process one webcam frame, run YOLO, and save the results."""

    uploaded_frame = request.FILES.get("frame")
    validation_error = validate_image(uploaded_frame)

    if validation_error:
        return JsonResponse({"error": validation_error}, status=400)

    scan = None
    annotated_path = None

    try:
        scan = CameraDetection.objects.create(
            image=uploaded_frame,
            total_objects=0,
            object_counts={},
            detections=[],
        )

        annotated_name = (
            f"annotated_camera/{uuid.uuid4().hex}.jpg"
        )
        annotated_path = Path(settings.MEDIA_ROOT) / annotated_name
        annotated_path.parent.mkdir(parents=True, exist_ok=True)

        detection_result = detect_objects(
            scan.image.path,
            str(annotated_path),
        )

        detections = detection_result.get("detections", [])
        object_counts = detection_result.get("object_counts", {})
        total_objects = detection_result.get(
            "total_objects", len(detections)
        )

        scan.total_objects = total_objects
        scan.object_counts = object_counts
        scan.detections = detections
        scan.save(
            update_fields=[
                "total_objects",
                "object_counts",
                "detections",
            ]
        )

        return JsonResponse({
            "id": scan.pk,
            "created_at": timezone.localtime(
                scan.created_at
            ).strftime("%d %b %Y, %H:%M:%S"),
            "total_objects": total_objects,
            "object_counts": object_counts,
            "detections": detections,
            "image_url": settings.MEDIA_URL + annotated_name,
        })

    except Exception as exc:
        logger.exception("Camera detection failed.")

        if scan is not None:
            try:
                scan.delete()
            except Exception:
                logger.exception("Could not remove failed scan.")

        if annotated_path and annotated_path.exists():
            try:
                annotated_path.unlink()
            except OSError:
                logger.exception("Could not remove annotated image.")

        # Detailed errors are useful during local development.
        if settings.DEBUG:
            message = f"{type(exc).__name__}: {exc}"
        else:
            message = "Camera detection failed. Please try again."

        return JsonResponse({"error": message}, status=500)


@require_GET
def camera_history_api(request):
    """Return the latest saved scans to the frontend."""

    try:
        scans = CameraDetection.objects.all().order_by(
            "-created_at"
        )[:50]

        history = []

        for scan in scans:
            history.append({
                "id": scan.pk,
                "created_at": timezone.localtime(
                    scan.created_at
                ).strftime("%d %b %Y, %H:%M:%S"),
                "total_objects": scan.total_objects,
                "object_counts": scan.object_counts or {},
                "detections": scan.detections or [],
                "image_url": (
                    scan.image.url if scan.image else None
                ),
            })

        return JsonResponse({"history": history})

    except Exception as exc:
        logger.exception("Camera history retrieval failed.")

        message = (
            f"{type(exc).__name__}: {exc}"
            if settings.DEBUG
            else "Could not load camera history."
        )

        return JsonResponse({"error": message}, status=500)


from django.views.decorators.http import require_POST
from django.shortcuts import redirect


@require_POST
def clear_calculation_history(request):
    CarbonCalculation.objects.all().delete()
    return redirect("home")


@require_POST
def clear_camera_history(request):
    CameraDetection.objects.all().delete()
    return redirect("home")
