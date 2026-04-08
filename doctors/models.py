from django.db import models
from django.utils import timezone


class Remake(models.Model):
    month = models.CharField(max_length=20)
    case_number = models.CharField(max_length=20)
    doctor_name = models.CharField(max_length=255)
    department = models.CharField(max_length=100)

    #product details section

    product_id = models.CharField(max_length=50, blank=True, null=True)
    invoice_description = models.TextField(blank=True, null=True)

    #production information section
    production_lab = models.CharField(max_length=100)
    mill_used = models.CharField(max_length=100, blank=True, null=True)
    milling_technician = models.CharField(max_length=100, blank=True, null=True)
    design_location = models.CharField(max_length=100, blank=True, null=True)
    units = models.IntegerField(default=0)

    # Remake Specifics
    original_case_number = models.CharField(max_length=50, blank=True, null=True)
    original_month = models.CharField(max_length=20, blank=True, null=True)
    original_production_lab = models.CharField(max_length=100, blank=True, null=True)
    remake_reason = models.TextField(blank=True, null=True)

    # Financials/Adjustments
    charge_doctor = models.BooleanField(default=False)
    remake_units = models.IntegerField(default=0)
    adjustment_units = models.IntegerField(default=0)
    lab_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    lab_discount_units = models.IntegerField(default=0)

    # Internal tracking for the 12-month window
    date_entered = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.case_number} - {self.doctor_name}"

