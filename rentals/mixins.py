
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.urls import reverse
from django.http import HttpResponse # <---- Import to generate text file
import csv # <---- Import to generate excel file

# below imports are for generating pdf file
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.utils import timezone
from .models import Rental, Vendor




# Rental List by category mixin
class RentalListMixin:
    """
    Mixin to filter rentals by category.
    """
    # get the cateogry from database
    def get_queryset(self, category):
        """
        Get the queryset of rentals filtered by category.
        """
        return Rental.objects.filter(category=category)

    # calculate total cost of rentals
    def calculate_total_cost(self, rentals):
        """
        Calculate the total cost of rentals.
        """
        total_cost = 0
        for rental in rentals:
            total_cost += rental.total_cost
        return total_cost

    # Render the template with rentals and total cost
    def render_rentals(self, request, rentals, total_cost):
        """
        Render the rentals template with rentals and total cost.
        """
        context = {'rentals': rentals, 'total_cost': total_cost}
        return render(request, 'rental_list.html', context)









""" User list page view. This is for admins to view all users.
    rentals = Rental.objects.filter(category='office_equipment').order_by('start_rental_date')
    # add up total cost totals
    total_cost = 0
    for rental in rentals:
        total_cost += rental.total_cost
    # add total cost to context
    context = {'rentals': rentals, 'total_cost': total_cost}
    return render(request, 'equipment_list_office.html', context)
"""







