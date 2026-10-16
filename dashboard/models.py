
from django.db import models


class CarbonCalculation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    electricity = models.FloatField(default=0)
    vehicles = models.PositiveIntegerField(default=0)
    distance_km = models.FloatField(default=0)
    solar_kwh = models.FloatField(default=0)
    ac_hours = models.FloatField(default=0)
    waste_kg = models.FloatField(default=0)

    total_emissions = models.FloatField(default=0)
    reduction_percent = models.FloatField(default=20)
    reduced_emissions = models.FloatField(default=0)
    saved_emissions = models.FloatField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Calculation {self.id} - "
            f"{self.total_emissions:.2f} kg CO2e"
        )


class CameraDetection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    total_objects = models.PositiveIntegerField(default=0)
    object_counts = models.JSONField(default=dict, blank=True)
    detections = models.JSONField(default=list, blank=True)

    # Store the original camera frame or uploaded image.
    image = models.ImageField(
        upload_to="camera_detections/",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Camera scan {self.id} - "
            f"{self.total_objects} objects"
        )



class WasteImpact(models.Model):
    MATERIAL_CHOICES = [
        ("plastic", "Plastic"),
        ("paper", "Paper and cardboard"),
        ("metal", "Metal"),
        ("glass", "Glass"),
        ("organic", "Organic waste"),
        ("ewaste", "Electronic waste"),
        ("general", "General waste"),
        ("unknown", "Needs verification"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)

    camera_scan = models.ForeignKey(
        "CameraDetection",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="waste_impacts",
    )

    material = models.CharField(
        max_length=20,
        choices=MATERIAL_CHOICES,
        default="unknown",
    )
    quantity = models.PositiveIntegerField(default=1)
    estimated_weight_kg = models.FloatField(default=0)
    disposal_method = models.CharField(
        max_length=30,
        default="not_recorded",
    )
    baseline_emissions_kg = models.FloatField(default=0)
    scenario_emissions_kg = models.FloatField(default=0)
    estimated_avoided_emissions_kg = models.FloatField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_material_display()} - {self.estimated_weight_kg} kg"


class EcoAction(models.Model):
    ACTION_CHOICES = [
        ("recycling", "Sorted waste correctly"),
        ("reusable", "Used a reusable item"),
        ("energy", "Reduced electricity use"),
        ("transport", "Used low-carbon transport"),
        ("composting", "Composted organic waste"),
        ("water", "Reduced water use"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
    )
    description = models.CharField(max_length=250, blank=True)
    points = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.points} points"
