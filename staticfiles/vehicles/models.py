from django.db import models

from rentals.models import Rental, Department, Vendor, Production
import datetime

# Create your models here.


class Vehicle(models.Model):
    """
    Vehicle models for rental vehicles
    """
    driver = models.CharField(max_length=100)
    production = models.ForeignKey(Production, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=100, default="plate_number")
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    start_rental_date = models.DateField()
    end_rental_date = models.DateField()
    contract_number = models.CharField(max_length=100, blank=True, null=True)
    purchase_order = models.CharField(max_length=100)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    weekly_rate = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    misc_fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    po_total = models.DecimalField(max_digits=10, decimal_places=2)
    on_rental = models.BooleanField(default=False)
    # rental status as choice field
    rental_status = models.CharField(
        max_length=100,
        choices=[
            ('on_rental', 'On Rental'),
            ('returned', 'Returned'),
            ('swapped', 'Swapped'),
        ],
        default='On Rental',
    )
    new_swapped = models.BooleanField(default=False)
    notes1 = models.CharField(max_length=300, blank=True)
    notes2 = models.CharField(max_length=300, blank=True)
    notes3 = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.driver} - {self.title} - {self.department} - {self.vehicle_type} - {self.make} - {self.model} - {self.color}"

    def save(self, *args, **kwargs):
        self.days = self.rental_duration  # Access the property without parentheses
        super().save(*args, **kwargs)

    @property
    def rental_duration(self):
        if self.start_rental_date and self.end_rental_date:
            if isinstance(self.start_rental_date, datetime.date) and isinstance(self.end_rental_date, datetime.date):
                delta = self.end_rental_date - self.start_rental_date
                return delta.days
            return None

    def cal_rates(self):
        """
        Calculate the rates based on the rental duration.
        """
        if self.rental_duration:
            if self.rental_duration <= 7:
                return int(self.daily_rate or 0) * self.rental_duration
            elif self.rental_duration <= 30:
                return int(self.weekly_rate or 0) * (self.rental_duration // 7)
            else:
                return int(self.monthly_rate or 0) * (self.rental_duration // 30)
        return None

    def cal_tax(self, tax_rate):
        """
        Calculate the tax based on the rental rate.
        """
        rental_rate = self.cal_rates()  # Use the cal_rates method to get the rental rate
        if rental_rate:
            return rental_rate * tax_rate
        return None

    # calculate the total rental cost using cal rates, tax, and misc fees
    def cal_total(self):
        """
        Calculate the total rental cost.
        """
        sub_total = self.cal_rates() + self.cal_tax(self.tax) + (self.misc_fees or 0)
        return sub_total

