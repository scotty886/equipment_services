from django.db import models

import logging
import datetime
from django.core.exceptions import ValidationError

# Create your models here.

logger = logging.getLogger(__name__)


class Production(models.Model):
    logger.error("Production model initialized")
    production_company = models.CharField(max_length=100, default="company")
    show_name = models.CharField(max_length=100, default="show")

    def __str__(self):
        return f"{self.production_company} - {self.show_name}"


class Department(models.Model):
    logger.error("Department model initialized")
    department_name = models.CharField(max_length=100, default="department")

    def __str__(self):
        return self.department_name

class VendorCategory(models.Model):
    logger.error("VendorCategory model initialized")
    name = models.CharField(max_length=100, default="category")

    def __str__(self):
        return self.name

class Vendor(models.Model):
    logger.error("Vendor model initialized")
    name = models.CharField(max_length=100, default="vendor")
    category = models.ForeignKey(VendorCategory, on_delete=models.CASCADE, null=True, blank=True)
    services = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField()
    contact = models.CharField(max_length=100, null=True, blank=True, default="contact")
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    agreement_signed = models.BooleanField(default=False)
    agreement_date = models.DateField(null=True, blank=True)
    COI_issued = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.services}"


class Rental(models.Model):
    rental_item = models.CharField(max_length=100, default="item")
    first_name = models.CharField(max_length=100, default="first")
    last_name = models.CharField(max_length=100, default="last")
    title = models.CharField(max_length=100, default="title")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    scene_info = models.CharField(max_length=300, null=True, blank=True)
    start_rental_date = models.DateField()
    end_rental_date = models.DateField()
    drop_off_location = models.CharField(max_length=300, null=True, blank=True)
    drop_off_time = models.TimeField(null=True, blank=True)
    pick_up_location = models.CharField(max_length=300, null=True, blank=True)
    pick_up_time = models.TimeField(null=True, blank=True)
    # selection box
    rental_type = models.CharField(max_length=100, choices=[('ROS', 'ROS'), ('Drop Load', 'Drop Load'), ('n/a', 'n/a')], default='choose rental type')
    category = models.CharField(max_length=100, choices=[('main_equipment', 'main_equipment'), ('special_equipment', 'special_equipment'), ('office_equipment', 'office_equipment'), ('set_equipment', 'set_equipment'), ('misc_equipment', 'misc_equipment')], default='choose category')
    addl_tax_fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchase_order = models.CharField(max_length=100, null=True, blank=True)
    quote_number = models.CharField(max_length=100, null=True, blank=True)
    payment_type = models.CharField(max_length=100, choices=[('net30', 'Net30'), ('check', 'Check'), ('credit_card', 'Credit Card'), ('cash', 'Cash')], default='choose payment type')
    notes1 = models.CharField(max_length=300, null=True, blank=True)
    notes2 = models.CharField(max_length=300, null=True, blank=True)
    notes3 = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.rental_item} - {self.department} - {self.vendor}"

    # Start date day of the week
    @property
    def start_day_of_week(self):
        if isinstance(self.start_rental_date, datetime.date):  # Ensure it's a date object
            return self.start_rental_date.strftime("%A")
        return None  # Handle cases where start_rental_date is not set

    # End date day of the week
    @property
    def end_day_of_week(self):
        if isinstance(self.end_rental_date, datetime.date):  # Ensure it's a date object
            return self.end_rental_date.strftime("%A")
        return None  # Handle cases where end_rental_date is not set

    # convert days to weeks
    @property
    def days_to_weeks(self):
        if self.start_rental_date and self.end_rental_date:
            if isinstance(self.start_rental_date, datetime.date) and isinstance(self.end_rental_date, datetime.date):
                delta = self.end_rental_date - self.start_rental_date
                return delta.days // 7
        return None

    # convert days to months
    @property
    def days_to_months(self):
        if self.start_rental_date and self.end_rental_date:
            if isinstance(self.start_rental_date, datetime.date) and isinstance(self.end_rental_date, datetime.date):
                delta = self.end_rental_date - self.start_rental_date
                return delta.days // 30
        return None

    @property
    def days_till_rental(self):
        today = datetime.date.today()
        rental_date = self.start_rental_date
        if isinstance(rental_date, datetime.date):  # Ensure it's a date object
            delta = rental_date - today
            return delta.days
        return None  # Handle cases where rental_date is not set

    @property
    def rental_duration(self):
        if self.start_rental_date and self.end_rental_date:
            if isinstance(self.start_rental_date, datetime.date) and isinstance(self.end_rental_date, datetime.date):
                delta = self.end_rental_date - self.start_rental_date
                return delta.days
        return None

    @property
    def days_past_rental(self):
        today = datetime.date.today()
        rental_date = self.end_rental_date
        if isinstance(rental_date, datetime.date):
            delta = today - rental_date
            return delta.days
        return None


    # Add date validation
    def clean(self):
        if self.start_rental_date and self.end_rental_date:
            if self.start_rental_date > self.end_rental_date:
                raise ValidationError("Start date cannot be after end date.")
    



class Service(models.Model):
    service = models.CharField(max_length=100, default="item")
    description = models.TextField(null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    requestor = models.CharField(max_length=100, default="requestor")
    title = models.CharField(max_length=100, default="title", null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    production = models.ForeignKey(Production, on_delete=models.CASCADE, null=True, blank=True)
    service_location = models.CharField(max_length=300, null=True, blank=True)
    start_service_date = models.DateField(null=True, blank=True)
    end_service_date = models.DateField(null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)
    purchase_order = models.CharField(max_length=100, null=True, blank=True)
    payment_type = models.CharField(max_length=100, choices=[('net30', 'Net30'), ('check', 'Check'), ('credit_card', 'Credit Card'), ('cash', 'Cash')], default='choose payment type')
    notes1 = models.CharField(max_length=300, null=True, blank=True)
    notes2 = models.CharField(max_length=300, null=True, blank=True)
    notes3 = models.TextField(null=True, blank=True)




    def __str__(self):
        return f"{self.service} - {self.department} - {self.vendor}"

    # Start date day of the week
    @property
    def start_day_of_week(self):
        if isinstance(self.start_service_date, datetime.date):  # Ensure it's a date object
            return self.start_service_date.strftime("%A")
        return None  # Handle cases where start_rental_date is not set

    # End date day of the week
    @property
    def end_day_of_week(self):
        if isinstance(self.end_service_date, datetime.date):  # Ensure it's a date object
            return self.end_service_date.strftime("%A")
        return None  # Handle cases where end_rental_date is not set

    # convert days to weeks
    @property
    def days_to_weeks(self):
        if self.start_service_date and self.end_service_date:
            if isinstance(self.start_service_date, datetime.date) and isinstance(self.end_service_date, datetime.date):
                delta = self.end_service_date - self.start_service_date
                return delta.days // 7
        return None

    @property
    def days_till_rental(self):
        today = datetime.date.today()
        rental_date = self.start_service_date
        if isinstance(rental_date, datetime.date):  # Ensure it's a date object
            delta = rental_date - today
            return delta.days
        return None  # Handle cases where rental_date is not set

    @property
    def service_duration(self):
        if self.start_service_date and self.end_service_date:
            if isinstance(self.start_service_date, datetime.date) and isinstance(self.end_service_date, datetime.date):
                delta = self.end_service_date - self.start_service_date
                return delta.days
        return None

    @property
    def days_to_end_service(self):
        today = datetime.date.today()
        service_date = self.end_service_date
        if isinstance(service_date, datetime.date):
            delta = service_date - today
            return delta.days
        return None

    @property
    def days_past_service(self):
        today = datetime.date.today()
        service_date = self.end_service_date
        if isinstance(service_date, datetime.date):
            delta = today - service_date
            return delta.days
        return None


    # Add date validation
    def clean(self):
        if self.start_service_date and self.end_service_date:
            if self.start_service_date > self.end_service_date:
                raise ValidationError("Start date cannot be after end date.")
      
        
