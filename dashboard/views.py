
from pathlib import Path
from uuid import uuid4

from django.shortcuts import render
from django.core.files.storage import default_storage

from PIL import Image, UnidentifiedImageError

from .computer_vision import detect_objects


def home(request):
    # Computer Vision defaults
    image_message = None
    uploaded_image_url = None
    annotated_image_url = None
    detection_error = None

    detections = []
    object_counts = {}
    total_objects = 0

    # Carbon calculator defaults
    result = None
    electricity = None
    emission_factor = 0.7  # Illustrative demo factor

    reduced_usage = None
    reduced_emissions = None
    saved_emissions = None
    footprint_status = None

    reduction_percent = 20
    bar_width = 80
    calculation_error = None

    if request.method == "POST":

        # ------------------------------------------
        # 1. IMAGE UPLOAD AND VALIDATION
        # ------------------------------------------
        uploaded_image = request.FILES.get("building_image")

        if uploaded_image:
            try:
                if uploaded_image.size > 5 * 1024 * 1024:
                    image_message = (
                        "Image must be smaller than 5 MB."
                    )
                else:
                    # Check the actual image format
                    with Image.open(uploaded_image) as image:
                        if image.format not in (
                            "JPEG",
                            "PNG",
                            "WEBP",
                        ):
                            raise ValueError(
                                "Unsupported image format."
                            )

                        image.verify()

                    uploaded_image.seek(0)

                    extension = Path(
                        uploaded_image.name
                    ).suffix.lower()

                    if extension not in (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".webp",
                    ):
                        extension = ".jpg"

                    unique_name = (
                        f"building_images/{uuid4().hex}{extension}"
                    )

                    saved_name = default_storage.save(
                        unique_name,
                        uploaded_image,
                    )

                    uploaded_image_url = default_storage.url(
                        saved_name
                    )

                    image_message = "Image uploaded successfully."

                    # ------------------------------------------
                    # 2. YOLO OBJECT DETECTION
                    # ------------------------------------------
                    try:
                        saved_path = default_storage.path(
                            saved_name
                        )

                        annotated_name = (
                            "building_images/"
                            f"annotated_{uuid4().hex}.jpg"
                        )

                        annotated_path = default_storage.path(
                            annotated_name
                        )

                        analysis = detect_objects(
                            saved_path,
                            annotated_image_path=annotated_path,
                        )

                        detections = analysis["detections"]
                        object_counts = analysis["object_counts"]
                        total_objects = analysis["total_objects"]

                        if Path(annotated_path).is_file():
                            annotated_image_url = (
                                default_storage.url(annotated_name)
                            )

                        if total_objects == 0:
                            image_message = (
                                "Image uploaded. No supported objects "
                                "were detected. Try a clearer image."
                            )

                    except Exception as error:
                        # Print the real error in the terminal
                        print(
                            "YOLO object detection error:",
                            repr(error),
                        )

                        detection_error = (
                            "Detection failed. Check the VS Code "
                            "terminal for the detailed error."
                        )

            except (
                UnidentifiedImageError,
                OSError,
                ValueError,
            ):
                image_message = (
                    "Please upload a valid JPEG, PNG, or WebP image."
                )

        # ------------------------------------------
        # 3. CARBON FOOTPRINT CALCULATOR
        # ------------------------------------------
        try:
            electricity = float(
                request.POST.get("electricity", "")
            )

            reduction_percent = float(
                request.POST.get("reduction_percent", "20")
            )

            if (
                electricity < 0
                or not 0 <= reduction_percent <= 100
            ):
                raise ValueError

            bar_width = 100 - reduction_percent

            # Estimated current emissions
            result = electricity * emission_factor

            # Digital Twin simulation
            reduced_usage = electricity * (
                1 - reduction_percent / 100
            )

            reduced_emissions = (
                reduced_usage * emission_factor
            )

            saved_emissions = result - reduced_emissions

            # Demo thresholds only, not universal standards
            if result < 100:
                footprint_status = "Low"
            elif result < 300:
                footprint_status = "Moderate"
            else:
                footprint_status = "High"

        except (ValueError, TypeError):
            calculation_error = (
                "Enter valid numbers. Electricity must be non-negative "
                "and reduction must be between 0 and 100."
            )

    # ------------------------------------------
    # 4. SEND RESULTS TO THE TEMPLATE
    # ------------------------------------------
    context = {
        "image_message": image_message,
        "uploaded_image_url": uploaded_image_url,
        "annotated_image_url": annotated_image_url,
        "detection_error": detection_error,
        "detections": detections,
        "object_counts": object_counts,
        "total_objects": total_objects,

        "result": result,
        "electricity": electricity,
        "emission_factor": emission_factor,
        "reduced_usage": reduced_usage,
        "reduced_emissions": reduced_emissions,
        "saved_emissions": saved_emissions,
        "footprint_status": footprint_status,
        "reduction_percent": reduction_percent,
        "bar_width": bar_width,
        "calculation_error": calculation_error,
    }

    return render(
        request,
        "dashboard/home.html",
        context,
    )
