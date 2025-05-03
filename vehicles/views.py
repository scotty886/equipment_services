"""
views for vehicles app"""
from django.shortcuts import get_object_or_404
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
from django.db.models import Q

# below imports are for generating pdf file
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.utils import timezone


from django.views.generic import (TemplateView, FormView,
                                  ListView, DetailView, CreateView, UpdateView, DeleteView)
from rentals.forms import SignUpForm, UpdateUserForm, PasswordChangeForm


from rentals.models import Production, Vendor, Department, Rental, Service, VendorCategory
from rentals.mixins import RentalListMixin

from .models import Vehicle


# Create your views here.

# Vehicles home view
def vehicles(request):
    return render(request, 'vehicles.html')

def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by('start_rental_date')
    # rental duration

    total_cost = 0
    for vehicle in vehicles:
        if vehicle.start_rental_date and vehicle.end_rental_date:
              total_cost += vehicle.po_total
    return render(request, 'vehicle_list.html', {'vehicles': vehicles, 'total_cost': total_cost})

# vehicle detail view
class VehicleDetailView(DetailView):
    """Vehicle detail view. This is for the admin to view vehicle details."""
    model = Vehicle
    template_name = 'vehicle_detail.html'
    context_object_name = 'vehicle'

    def get_object(self, queryset=None):
        return get_object_or_404(Vehicle, pk=self.kwargs.get('pk'))


# vehicle create view
class VehicleCreateView(CreateView):
    """Vehicle create view. This is for the admin to create a new vehicle."""
    model = Vehicle
    template_name = 'vehicle_form.html'
    fields = ['production', 'driver', 'title', 'department', 'vendor', 'vehicle_type', 'plate_number', 'make', 'model', 'color', 'start_rental_date', 'end_rental_date', 'contract_number', 'purchase_order', 'daily_rate', 'weekly_rate', 'monthly_rate', 'tax', 'misc_fees', 'po_total']
    context_object_name = 'form'
    success_url = reverse_lazy('vehicle_list')

    def form_valid(self, form):
        start_rental_date = form.cleaned_data.get('start_rental_date')
        end_rental_date = form.cleaned_data.get('end_rental_date')

        # end rental date must be after start date
        if end_rental_date < start_rental_date:
            form.add_error('end_rental_date', "End rental date must be after start rental date.")
            return self.form_invalid(form)

        # start date must be before end date
        if start_rental_date > end_rental_date:
            form.add_error('start_rental_date', "Start rental date must be before end rental date.")
            return self.form_invalid(form)


        messages.success(self.request, "Vehicle information saved successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Vehicle information failed to save.")
        return super().form_invalid(form)

    def clean(self):
        cleaned_data = super().clean()
        start_rental_date = cleaned_data.get('start_rental_date')
        end_rental_date = cleaned_data.get('end_rental_date')

        if start_rental_date and end_rental_date and start_rental_date > end_rental_date:
            raise forms.ValidationError("End rental date must be after start rental date.")
        return cleaned_data


# vehicle update view
class VehicleUpdateView(UpdateView):
    """Vehicle update view. This is for the admin to update vehicle details."""
    model = Vehicle
    template_name = 'vehicle_form.html'
    fields = ['production', 'driver', 'title', 'department', 'vendor', 'vehicle_type', 'plate_number', 'make', 'model', 'color', 'start_rental_date', 'end_rental_date', 'contract_number', 'purchase_order', 'daily_rate', 'weekly_rate', 'monthly_rate', 'tax', 'misc_fees', 'po_total']
    context_object_name = 'form'
    success_url = reverse_lazy('vehicle_list')


# vehicle delete view
class VehicleDeleteView(DeleteView):
    """Vehicle delete view. This is for the admin to delete vehicle details."""
    model = Vehicle
    template_name = 'vehicle_delete.html'
    context_object_name = 'vehicle'
    success_url = reverse_lazy('vehicle_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Vehicle information deleted successfully.")
        return super().delete(request, *args, **kwargs)

# vehicle search view
class VehicleSearchView(ListView):
    """Vehicle search view. This is for the admin to search for vehicle details."""
    model = Vehicle
    template_name = 'vehicle_search.html'
    context_object_name = 'vehicles'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(driver__icontains=query) |
                Q(department__department_name__icontains=query) |
                Q(vendor__name__icontains=query) |
                Q(vehicle_type__icontains=query) |
                Q(plate_number__icontains=query) |
                Q(contract_number__icontains=query) |
                Q(purchase_order__icontains=query)

            )
            # add up total cost totals
            total_cost = 0
            for rental in queryset:
                total_cost += rental.po_total
            # add total cost to context
            self.extra_context = {'total_cost': total_cost}

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        data = context
        return context

# print vehicle list as text view
def vehicle_list_txt(request):
    """ This will print a text file of the service list."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="set_rentals_report.txt"'
    vehicles = Vehicle.objects.all().order_by('start_rental_date')
    lines = []
    #fields = ['service', 'description', 'rate', 'total', 'start_service_date', 'end_service_date', 'vendor', 'service_location', 'requestor', 'title', 'production', 'department', 'purchase_order', 'payment_type', 'notes1', 'notes2', 'notes3',]
    for vehicle in vehicles:
        lines.append(f"Driver: {vehicle.driver}\n, "
                    f"Title: {vehicle.title}\n"
                    f"Department: {vehicle.department}\n"
                    f"Vendor: {vehicle.vendor}\n"
                    f"Vehicle Type: {vehicle.vehicle_type}\n"
                    f"Plate Number: {vehicle.plate_number}\n"
                    f"Make: {vehicle.make}\n"
                    f"Model: {vehicle.model}\n"
                    f"Color: {vehicle.color}\n"
                    f"Start Rental Date: {vehicle.start_rental_date}\n"
                    f"End Rental Date: {vehicle.end_rental_date}\n"
                    f"Contract Number: {vehicle.contract_number}\n"
                    f"Purchase Order: {vehicle.purchase_order}\n"
                    f"Daily Rate: {vehicle.daily_rate}\n"
                    f"Weekly Rate: {vehicle.weekly_rate}\n"
                    f"Monthly Rate: {vehicle.monthly_rate}\n"
                    f"Tax: {vehicle.tax}\n"
                    f"Misc Fees: {vehicle.misc_fees}\n"
                    f"PO Total: {vehicle.po_total}\n\n")
        response.writelines(lines)
    return response


# print vehicle list as csv view
def vehicle_list_csv(request):
    """ This will print a csv file of the vehicle list."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vehicle_list.csv"'
    writer = csv.writer(response)
    writer.writerow(['Driver', 'Title', 'Department', 'Vendor', 'Vehicle Type', 'Plate Number', 'Make', 'Model', 'Color', 'Start Rental', 'End Rental', 'Contract #', 'PO Number', 'Daily Rate', 'Weekly Rate', 'Monthly Rate', 'Tax', 'Misc Fees', 'PO Total'])
    vehicles = Vehicle.objects.all().order_by('start_rental_date')
    for vehicle in vehicles:
        writer.writerow([vehicle.driver, vehicle.title, vehicle.department, vehicle.vendor.name, vehicle.vehicle_type, vehicle.plate_number, vehicle.make, vehicle.model, vehicle.color, vehicle.start_rental_date, vehicle.end_rental_date, vehicle.contract_number, vehicle.purchase_order, vehicle.daily_rate, vehicle.weekly_rate, vehicle.monthly_rate, vehicle.tax, vehicle.misc_fees, vehicle.po_total])
    return response




# rental detail text
def rental_detail_txt(request, pk):
    """ This will print a text file of rental details."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="rental_detail_report.txt"'
    rental = get_object_or_404(Rental, pk=pk)
    lines = []
    lines.append(f"Rental Item: {rental.rental_item}\n First Name: {rental.first_name}\n Last Name: {rental.last_name}\n Title: {rental.title}\n Department: {rental.department}\n Production: {rental.production}\n Vendor: {rental.vendor}\n Scene Info: {rental.scene_info}\n Start Rental Date: {rental.start_rental_date}\n End Rental Date: {rental.end_rental_date}\n Drop Off Location: {rental.drop_off_location}\n Drop Off Time: {rental.drop_off_time}\n Pick Up Location: {rental.pick_up_location}\n Pick Up Time: {rental.pick_up_time}\n Rental Type: {rental.rental_type}\n Category: {rental.category}\n Additional Tax Fees: ${rental.addl_tax_fees:,.2F}\n Total Cost: ${rental.total_cost:,.2F}\n Purchase Order: {rental.purchase_order}\n Quote Number: {rental.quote_number}\n Notes 1: {rental.notes1}\n Notes 2: {rental.notes2}\n Notes 3: {rental.notes3}")
    response.writelines(lines)
    return response

# rental detail pdf
def rental_detail_pdf(request, pk):
    """ PDF view of rental detail """
    # create Bytestream buffer
    buffer = io.BytesIO()
    # create a canvas and set multiple pages
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    # create text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    rental = get_object_or_404(Rental, pk=pk)

    lines = []
    lines.append("")
    lines.append(f'{rental.production}')
    lines.append('___________________________')
    lines.append('')
    lines.append(f"Rental Item: {rental.rental_item}")
    lines.append(f"First Name: {rental.first_name}")
    lines.append(f"Last Name: {rental.last_name}")
    lines.append(f"Title: {rental.title}")
    lines.append(f"Department: {rental.department}")
    lines.append(f"Production: {rental.production}")
    lines.append(f"Vendor: {rental.vendor}")
    lines.append(f"Purpose/Scene Info: {rental.scene_info}")
    lines.append(f"Start Rental Date: {rental.start_rental_date}")
    lines.append(f"End Rental Date: {rental.end_rental_date}")
    lines.append(f"Drop Off Location: {rental.drop_off_location}")
    lines.append(f"Drop Off Time: {rental.drop_off_time}")
    lines.append(f"Pick Up Location: {rental.pick_up_location}")
    lines.append(f"Pick Up Time: {rental.pick_up_time}")
    lines.append(f"Rental Type: {rental.rental_type}")
    lines.append(f"Category: {rental.category}")
    lines.append(f"Additional Tax Fees: ${rental.addl_tax_fees:,.2F}")
    lines.append(f"Total Cost: ${rental.total_cost:,.2F}")
    lines.append(f"Purchase Order: {rental.purchase_order}")
    lines.append(f"Quote Number: {rental.quote_number}")
    lines.append(f"Notes 1: {rental.notes1}")
    lines.append(f"Notes 2: {rental.notes2}")
    lines.append(f"Notes 3: {rental.notes3}")
    lines.append("")
    for line in lines:
        textob.textLine(line)
    # Draw the text object on the canvas
    p.drawText(textob)
    p.showPage()
    p.save()
    buffer.seek(0)
    # Return response
    return FileResponse(buffer, as_attachment=True, filename='Rental_Detail_Report.pdf')



# vehicle detail text
def vehicle_detail_txt(request, pk):
    """ This will print a text file of the vehicle details."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="vehicle_detail_report.txt"'
    vehicle = get_object_or_404(Vehicle, pk=pk)
    lines = []
    lines.append(f"Driver: {vehicle.driver}\n"
                f"Title: {vehicle.title}\n"
                f"Department: {vehicle.department}\n"
                f"Vendor: {vehicle.vendor}\n"
                f"Vehicle Type: {vehicle.vehicle_type}\n"
                f"Plate Number: {vehicle.plate_number}\n"
                f"Make: {vehicle.make}\n"
                f"Model: {vehicle.model}\n"
                f"Color: {vehicle.color}\n"
                f"Start Rental Date: {vehicle.start_rental_date}\n"
                f"End Rental Date: {vehicle.end_rental_date}\n"
                f"Contract Number: {vehicle.contract_number}\n"
                f"Purchase Order: {vehicle.purchase_order}\n"
                f"Daily Rate: {vehicle.daily_rate}\n"
                f"Weekly Rate: {vehicle.weekly_rate}\n"
                f"Monthly Rate: {vehicle.monthly_rate}\n"
                f"Tax: {vehicle.tax}\n"
                f"Misc Fees: {vehicle.misc_fees}\n"
                f"PO Total: {vehicle.po_total}")
    response.writelines(lines)
    return response



# vehicle detail pdf
def vehicle_detail_pdf(request, pk):
    """ PDF view of vehicle detail """
    # create Bytestream buffer
    buffer = io.BytesIO()
    # create a canvas and set multiple pages
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    # create text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    vehicle = get_object_or_404(Vehicle, pk=pk)

    lines = []
    lines.append("")
    lines.append(f'{vehicle.production}')
    lines.append('___________________________')
    lines.append('')
    lines.append(f"Driver: {vehicle.driver}")
    lines.append(f"Title: {vehicle.title}")
    lines.append(f"Department: {vehicle.department}")
    lines.append(f"Vendor: {vehicle.vendor}")
    lines.append(f"Vehicle Type: {vehicle.vehicle_type}")
    lines.append(f"Plate Number: {vehicle.plate_number}")
    lines.append(f"Make: {vehicle.make}")
    lines.append(f"Model: {vehicle.model}")
    lines.append(f"Color: {vehicle.color}")
    lines.append(f"Start Rental Date: {vehicle.start_rental_date}")
    lines.append(f"End Rental Date: {vehicle.end_rental_date}")
    lines.append(f"Contract Number: {vehicle.contract_number}")
    lines.append(f"Purchase Order: {vehicle.purchase_order}")
    lines.append(f"Daily Rate: {vehicle.daily_rate}")
    lines.append(f"Weekly Rate: {vehicle.weekly_rate}")
    lines.append(f"Monthly Rate: {vehicle.monthly_rate}")
    lines.append(f"Tax: {vehicle.tax}")
    lines.append(f"Misc Fees: {vehicle.misc_fees}")
    lines.append(f"PO Total: {vehicle.po_total}")
    lines.append("")

    for line in lines:
        textob.textLine(line)
    # Draw the text object on the canvas
    p.drawText(textob)
    p.showPage()
    p.save()
    buffer.seek(0)
    # Return response
    return FileResponse(buffer, as_attachment=True, filename='Vehicle_Detail_Report.pdf')

