"""
Views for the rental application.
Views will include:
Home and About page views
User authentication views
Form views for creating, updating, and deleting rentals
List views for rentals
"""
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
from .forms import SignUpForm, UpdateUserForm, PasswordChangeForm

#import logging
from .models import Production, Vendor, Department, Rental, Service, VendorCategory
from .mixins import RentalListMixin

# Create your views here.

#logger = logging.getLogger(__name__)


def home(request):
    """ Home page view.
     Homepage will give a general description of the application."""
    return render(request, 'home.html')


def about(request):
    """ About page view.
     About page will give a quick rundown of the types of rentals the application will handle."""
    return render(request, 'about.html')

##################  USER AUTHENTICATION ######################

# user login view
def login_user(request):
    """ Login page view.
     Login page will allow users to login to the application using their username and password."""
    #logger.error("Login page accessed")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "you have been logged in successfully.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login_user')
    else:
        messages.error(request, "Invalid request method.")
        return render(request, 'login_user.html')

# user logout view
def logout_user(request):
    """ Logout page view."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

# user registration view
def register_user(request):
    """ Registration page view. This is for new users to create an account.
    """
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check the form.")
            return redirect('register_user')
    else:
        messages.error(request, "Invalid request method.")
        context = {'form': form}
        return render(request, 'register_user.html', context)

# user update view
def update_user(request):
    """ Update user page view. This is for users to update their profile information."""
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, 'User details updated successfully.')
            return redirect('home')
        return render(request, 'update_user.html', {'user_form': user_form})
    else:
        messages.error(request, 'You need to be logged in to update your profile.')
        return redirect('home')

# user password update view
def update_password(request):
    """ Update password page view. This is for users to update their password."""
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = PasswordChangeForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password updated successfully.')
                login(request, current_user)
                return redirect('update_user')
            else:
                messages.error(request, 'Password update failed. Please try again.')
                return redirect('update_password')
        else:
            form = PasswordChangeForm(current_user)
            context = {'form': form}
            return render(request, 'update_password.html', context)
    else:
        messages.error(request, 'You need to be logged in to update your password.')
        return redirect('home')

# user list view
def user_list(request):
    """ User list page view. This is for admins to view all users."""
    users = User.objects.all().order_by('first_name')
    return render(request, 'user_list.html', {'users': users})



##################  FORMS TO ENTER INFORMATION INTO THE DATABASE ######################

class ProductionInfoFormView(CreateView):
    """ Production information form view. This is for the admin to enter production information."""
    model = Production
    template_name = 'production_form.html'
    fields = ['production_company', 'show_name']
    context_object_name = 'form'
    success_url = reverse_lazy('home')
    # show success message
    def form_valid(self, form):
        messages.success(self.request, "Production information saved successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Production information failed to save.")
        return super().form_invalid(form)


######### VENDOR VIEWS #########

# Vendor List function view
def vendor_list(request):
    """ User list page view. This is for admins to view all users."""
    vendors = Vendor.objects.all().order_by('name')
    return render(request, 'vendor_list.html', {'vendors': vendors})

# Vendor detail view
class VendorDetailView(DetailView):
    """ Vendor detail view. This is for the admin to view vendor details. """
    model = Vendor
    template_name = 'vendor_detail.html'
    context_object_name = 'vendor'

    def get_object(self, queryset=None):
        return get_object_or_404(Vendor, pk=self.kwargs.get('pk'))

# Vendor update view
class VendorUpdateView(UpdateView):
    """ Vendor update view. This is for the admin to update vendor information."""
    model = Vendor
    template_name = 'vendor_update.html'
    fields = ['name', 'services', 'category', 'address', 'contact', 'phone', 'email', 'agreement_signed', 'agreement_date', 'COI_issued', 'notes']
    context_object_name = 'form'
    success_url = reverse_lazy('vendor_list')

    def form_valid(self, form):
        messages.success(self.request, "Vendor information updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Vendor information failed to update.")
        return super().form_invalid(form)


# Vendor delete view
class VendorDeleteView(DeleteView):
    """ Vendor delete view. This is for the admin to delete vendor information."""
    model = Vendor
    template_name = 'vendor_delete.html'
    context_object_name = 'vendor'
    success_url = reverse_lazy('vendor_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Vendor deleted successfully.")
        return super().delete(request, *args, **kwargs)

# vendor form view
class VendorFormView(CreateView):
    """ Vendor information form view. This is for the admin to enter vendor information."""
    model = Vendor
    template_name = 'vendor_form.html'
    fields = ['name', 'services', 'category', 'address', 'contact', 'phone', 'email', 'agreement_signed', 'agreement_date', 'COI_issued', 'notes']
    context_object_name = 'form'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Vendor information saved successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Vendor information failed to save.")
        return super().form_invalid(form)


class VendorCategoryFormView(CreateView):
    """ Vendor category information form view. This is for the admin to enter vendor category information."""
    model = VendorCategory
    template_name = 'vendor_category_form.html'
    fields = ['name']
    context_object_name = 'form'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Vendor category information saved successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Vendor category information failed to save.")
        return super().form_invalid(form)

### Generate text file Vendor List
def vendor_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="vendor_list.txt"'

    vendors = Vendor.objects.all()
    lines = []
    for vendor in vendors:
        lines.append(f"Vendor Name: {vendor.name}\n Vender Services: {vendor.services}\n Address: {vendor.address}\n Contact: {vendor.contact}\n Phone: {vendor.phone}\n Email: {vendor.email}\n Agreement Signed: {vendor.agreement_signed}\n Agreement Date: {vendor.agreement_date}\n COI Issued: {vendor.COI_issued}\n Notes: {vendor.notes}\n\n")
    response.writelines(lines)
    return response

### Generate text file Vendor List
def vendor_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vendor_list.csv"'

    # Create a csv writer
    writer = csv.writer(response)

    # Designate The Model
    vendors = Vendor.objects.all()

    # Add colum headings to the csv file
    writer.writerow(['Vendor Name', 'Services', 'Address', 'Contact', 'Phone', 'Email', 'Notes'])

    # Loop through the vendors and write to the csv file
    for vendor in vendors:
            writer.writerow([vendor.name, vendor.services, vendor.address, vendor.contact, vendor.phone, vendor.email, vendor.notes])

    return response

# Generate PDF file Vendor List
def vendor_pdf(request):
    # create Bytestream buffer
    buffer = io.BytesIO()
    # create a canvas
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    # create text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)


    # Get all vendors from the database
    vendors = Vendor.objects.all()

    lines = []

    for vendor in vendors:
        lines.append(vendor.name)
        lines.append(vendor.services)
        lines.append(vendor.address)
        lines.append(vendor.contact)
        lines.append(vendor.phone)
        lines.append(vendor.email)
        lines.append(vendor.notes)
        lines.append("")

    for line in lines:
        textob.textLine(line)

    # Draw the text object on the canvas
    p.drawText(textob)
    p.showPage()
    p.save()
    buffer.seek(0)

    # Return response
    return FileResponse(buffer, as_attachment=True, filename='vendor_list.pdf')





######### DEPARTMENT VIEWS #########

# department list view

# department detail view

# department update view

# department delete view

# department details view

# department form view
class DepartmentFormView(CreateView):
    """ Department information form view. This is for the admin to enter department information."""
    model = Department
    template_name = 'department_form.html'
    fields = ['department_name']
    context_object_name = 'form'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Department information saved successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Department information failed to save.")
        return super().form_invalid(form)


########################################## RENTAL VIEWS ###############################################
########################################## RENTAL VIEWS ###############################################
########################################## RENTAL VIEWS ###############################################
########################################## RENTAL VIEWS ###############################################

# rentals list view
class RentalListView(ListView):
    """ Rental list view. This is for the admin to view all rentals."""
    model = Rental
    template_name = 'rental_list.html'
    context_object_name = 'rentals'
    # arrange results in alphabetical order
    ordering = ['rental_item']

    def get_queryset(self):
        return Rental.objects.all()

# rentals update view
class RentalUpdateView(UpdateView):
    """ Rental update view. This is for the admin to update rental information."""
    model = Rental
    template_name = 'rental_update.html'
    fields = ['rental_item', 'first_name', 'last_name', 'title', 'department', 'production', 'vendor', 'scene_info',
              'start_rental_date', 'end_rental_date', 'drop_off_location', 'drop_off_time', 'pick_up_location',
              'pick_up_time', 'rental_type', 'category', 'addl_tax_fees', 'total_cost', 'purchase_order',
              'quote_number', 'payment_type', 'notes1', 'notes2', 'notes3']
    context_object_name = 'form'
    success_url = reverse_lazy('rental_list')

    def form_valid(self, form):
        messages.success(self.request, "Rental information updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Rental information failed to update.")
        return super().form_invalid(form)

# rentals delete view
class RentalDeleteView(DeleteView):
    """ Rental delete view. This is for the admin to delete rental information."""
    model = Rental
    template_name = 'rental_delete.html'
    context_object_name = 'rental'
    success_url = reverse_lazy('rental_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Rental deleted successfully.")
        return super().delete(request, *args, **kwargs)

# rentals details view
class RentalDetailView(DetailView):
    """ Rental detail view. This is for the admin to view rental details. """
    model = Rental
    template_name = 'rental_detail.html'
    context_object_name = 'rental'

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


# rentals form view
class RentalFormView(CreateView):
    """ Rental information form view. This is for the admin to enter rental information."""
    model = Rental
    template_name = 'rental_form.html'
    fields = ['rental_item', 'first_name', 'last_name', 'title', 'department', 'production', 'vendor', 'scene_info', 'start_rental_date', 'end_rental_date', 'drop_off_location', 'drop_off_time', 'pick_up_location', 'pick_up_time', 'rental_type', 'category', 'addl_tax_fees', 'total_cost', 'purchase_order', 'quote_number', 'payment_type', 'notes1', 'notes2', 'notes3']
    context_object_name = 'form'
    success_url = reverse_lazy('rental_list')

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

         messages.success(self.request, "Rental information saved successfully.")
         return super().form_valid(form)

    def form_invalid(self, form):
         messages.error(self.request, "Rental information failed to save.")
         return super().form_invalid(form)

     # form datetime validation
    def clean(self):
         cleaned_data = super().clean()
         start_rental_date = cleaned_data.get('start_rental_date')
         end_rental_date = cleaned_data.get('end_rental_date')

         if start_rental_date and end_rental_date and start_rental_date > end_rental_date:
             raise forms.ValidationError("End rental date must be after start rental date.")
         return cleaned_data

# rental equipment print txt report
def rental_txt(request):
    """ This will print a text file of all the rental equipment."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="rental_report.txt"'
    rentals = Rental.objects.all()
    lines = []
    for rental in rentals:
        lines.append(f"Rental Item: {rental.rental_item}\n First Name: {rental.first_name}\n Last Name: {rental.last_name}\n Title: {rental.title}\n Department: {rental.department}\n Production: {rental.production}\n Vendor: {rental.vendor}\n Scene Info: {rental.scene_info}\n Start Rental Date: {rental.start_rental_date}\n End Rental Date: {rental.end_rental_date}\n Drop Off Location: {rental.drop_off_location}\n Drop Off Time: {rental.drop_off_time}\n Pick Up Location: {rental.pick_up_location}\n Pick Up Time: {rental.pick_up_time}\n Rental Type: {rental.rental_type}\n Category: {rental.category}\n Additional Tax Fees: {rental.addl_tax_fees}\n Total Cost: {rental.total_cost}\n Purchase Order: {rental.purchase_order}\n Quote Number: {rental.quote_number}\n Notes 1: {rental.notes1}\n Notes 2: {rental.notes2}\n Notes 3: {rental.notes3}\n\n ")
        response.writelines(lines)
    return response

# rental equipment print csv report
def rental_csv(request):
    """" create csv file of rental equipment report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rental_report.csv"'

    # Create a csv writer
    writer = csv.writer(response)

    # Designate The Model
    rentals = Rental.objects.all()

    # Add colum headings to the csv file
    writer.writerow(['Rental Item', 'First Name', 'Last Name', 'Title', 'Department', 'Vendor', 'Purpose', 'Start Rental', 'End Rental', 'Rental Type', 'Category', 'Total Cost', 'Purchase Order', 'Quote Number'])

    # Loop through the rentals and write to the csv file
    for rental in rentals:
        writer.writerow([rental.rental_item, rental.first_name, rental.last_name, rental.title, rental.department, rental.vendor.name, rental.scene_info, rental.start_rental_date, rental.end_rental_date, rental.rental_type, rental.category, rental.total_cost, rental.purchase_order, rental.quote_number])

    return response

# rental equipment print pdf report
def rental_pdf(request):
    """ PDF view of rental list"""
    # create Bytestream buffer
    buffer = io.BytesIO()
    # create a canvas and set multiple pages
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    # create text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    rentals = Rental.objects.all()

    lines = []

    for rental in rentals:
        lines.append(f"Rental Item: {rental.rental_item}")
        lines.append(f"First Name: {rental.first_name}")
        lines.append(f"Last Name: {rental.last_name}")
        lines.append(f"Title: {rental.title}")
        lines.append(f"Department: {rental.department} ")
        lines.append(f"Production: {rental.production}" )
        lines.append(f"Vendor: {rental.vendor}" )
        lines.append(f"Purpose/Scene Info: {rental.scene_info}")
        lines.append(f"Start Rental Date: {rental.start_rental_date}")
        lines.append(f"End Rental Date: {rental.end_rental_date}")
        lines.append(f"Drop Off Location: {rental.drop_off_location}")
        lines.append(f"Drop Off Time: {rental.drop_off_time}")
        lines.append(f"Pick Up Location: {rental.pick_up_location}")
        lines.append(f"Pick Up Time: {rental.pick_up_time}")
        lines.append(f"Rental Type: {rental.rental_type}")
        lines.append(f"Category: {rental.category}")
        lines.append(f"Additional Tax Fees:{rental.addl_tax_fees} ")
        lines.append(f"Total Cost: {rental.total_cost}")
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
    return FileResponse(buffer, as_attachment=True, filename='Rental_Report.pdf')


#################  main equipment rental list view #####################
#################  main equipment rental list view #####################

def main_equipment_list(request):
    """ User list page view. This is for admins to view all users."""
    rentals = Rental.objects.filter(category='main_equipment').order_by('start_rental_date')
    # add up total cost totals
    total_cost = 0
    for rental in rentals:
        total_cost += rental.total_cost
    # add total cost to context
    context = {'rentals': rentals, 'total_cost': total_cost}
    return render(request, 'equipment_list_main.html', context)


# Generate text report of main equipment rentals
def main_equipment_txt(request):
    """ This will print a text file of all the rental equipment."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="main_rentals_report.txt"'
    rentals = Rental.objects.filter(category='main_equipment').order_by('start_rental_date')
    lines = []
    for rental in rentals:
        lines.append(f"Rental Item: {rental.rental_item}\n First Name: {rental.first_name}\n Last Name: {rental.last_name}\n Title: {rental.title}\n Department: {rental.department}\n Production: {rental.production}\n Vendor: {rental.vendor}\n Scene Info: {rental.scene_info}\n Start Rental Date: {rental.start_rental_date}\n End Rental Date: {rental.end_rental_date}\n Drop Off Location: {rental.drop_off_location}\n Drop Off Time: {rental.drop_off_time}\n Pick Up Location: {rental.pick_up_location}\n Pick Up Time: {rental.pick_up_time}\n Rental Type: {rental.rental_type}\n Category: {rental.category}\n Additional Tax Fees: {rental.addl_tax_fees}\n Total Cost: {rental.total_cost}\n Purchase Order: {rental.purchase_order}\n Quote Number: {rental.quote_number}\n Notes 1: {rental.notes1}\n Notes 2: {rental.notes2}\n Notes 3: {rental.notes3}\n\n ")
        response.writelines(lines)
    return response


# Generate csv report of main equipment rentals
def main_equipment_csv(request):
    """" create csv file of rental equipment report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rental_report.csv"'

    # Create a csv writer
    writer = csv.writer(response)

    # Designate The Model
    rentals = Rental.objects.filter(category='main_equipment').order_by('start_rental_date')

    # Add colum headings to the csv file
    writer.writerow(
        ['Rental Item', 'First Name', 'Last Name', 'Title', 'Department', 'Vendor', 'Purpose',
         'Start Rental', 'End Rental',
         'Rental Type', 'Category', 'Total Cost', 'Purchase Order',
         'Quote Number'])

    # Loop through the rentals and write to the csv file
    for rental in rentals:
        writer.writerow([rental.rental_item, rental.first_name, rental.last_name, rental.title, rental.department,
                         rental.vendor.name, rental.scene_info, rental.start_rental_date,
                         rental.end_rental_date, rental.rental_type, rental.category,
                         rental.total_cost, rental.purchase_order, rental.quote_number,
                         ])

    return response

# Generate pdf report of main equipment rentals
def main_equipment_pdf(request):
    """ PDF view of rental list """
    # create Bytestream buffer
    buffer = io.BytesIO()
    # create a canvas and set multiple pages
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    # create text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    rentals = Rental.objects.filter(category='main_equipment').order_by('start_rental_date')

    lines = []

    for rental in rentals:
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
        lines.append(f"Additional Tax Fees: {rental.addl_tax_fees}")
        lines.append(f"Total Cost: {rental.total_cost}")
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
    return FileResponse(buffer, as_attachment=True, filename='main_equipment_report.pdf')



#################  spacial equipment rental list view #####################
#################  special equipment rental list view #####################

# special equipment list view
def special_equipment_list(request):
    """ User list page view. This is for admins to view all users."""
    rentals = Rental.objects.filter(category='special_equipment').order_by('start_rental_date')
    # add up total cost totals
    total_cost = 0
    for rental in rentals:
        total_cost += rental.total_cost
    # add total cost to context
    context = {'rentals': rentals, 'total_cost': total_cost}
    return render(request, 'equipment_list_special.html', context)


# Generate text report of special equipment rentals
def special_equipment_txt(request):
    """ This will print a text file of all the rental equipment."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="special_rentals_report.txt"'
    rentals = Rental.objects.filter(category='special_equipment').order_by('start_rental_date')
    lines = []
    for rental in rentals:
        lines.append(f"Rental Item: {rental.rental_item}\n First Name: {rental.first_name}\n Last Name: {rental.last_name}\n Title: {rental.title}\n Department: {rental.department}\n Production: {rental.production}\n Vendor: {rental.vendor}\n Scene Info: {rental.scene_info}\n Start Rental Date: {rental.start_rental_date}\n End Rental Date: {rental.end_rental_date}\n Drop Off Location: {rental.drop_off_location}\n Drop Off Time: {rental.drop_off_time}\n Pick Up Location: {rental.pick_up_location}\n Pick Up Time: {rental.pick_up_time}\n Rental Type: {rental.rental_type}\n Category: {rental.category}\n Additional Tax Fees: {rental.addl_tax_fees}\n Total Cost: {rental.total_cost}\n Purchase Order: {rental.purchase_order}\n Quote Number: {rental.quote_number}\n Notes 1: {rental.notes1}\n Notes 2: {rental.notes2}\n Notes 3: {rental.notes3}\n\n ")
        response.writelines(lines)
    return response

# Generate csv report of special equipment rentals
def special_equipment_csv(request):
    """" create csv file of rental equipment report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="special_equipment_report.csv"'

    # Create a csv writer
    writer = csv.writer(response)

    # Designate The Model
    rentals = Rental.objects.filter(category='special_equipment').order_by('start_rental_date')

    # Add colum headings to the csv file
    writer.writerow(
        ['Rental Item', 'First Name', 'Last Name', 'Title', 'Department', 'Vendor', 'Purpose',
         'Start Rental', 'End Rental',
         'Rental Type', 'Category', 'Total Cost', 'Purchase Order',
         'Quote Number'])

    # Loop through the rentals and write to the csv file
    for rental in rentals:
        writer.writerow([rental.rental_item, rental.first_name, rental.last_name, rental.title, rental.department,
                         rental.vendor.name, rental.scene_info, rental.start_rental_date,
                         rental.end_rental_date,
                         rental.rental_type, rental.category,
                         rental.total_cost, rental.purchase_order, rental.quote_number])

    return response

# Generate pdf report of special equipment rentals
def special_equipment_pdf(request):
    """ PDF view of rental list """
    # create Bytestream buffer
    buffer = io.BytesIO()
    # create a canvas and set multiple pages
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    # create text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    rentals = Rental.objects.filter(category='special_equipment').order_by('start_rental_date')

    lines = []

    for rental in rentals:
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
        lines.append(f"Additional Tax Fees: {rental.addl_tax_fees}")
        lines.append(f"Total Cost: {rental.total_cost}")
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
    return FileResponse(buffer, as_attachment=True, filename='special_equipment_report.pdf')


#################  set production equipment rental list view #####################
#################  set production equipment rental list view #####################

# Set production equipment list view
def set_equipment_list(request):
    """ User list page view. This is for admins to view all users."""
    rentals = Rental.objects.filter(category='set_equipment').order_by('start_rental_date')
    # add up total cost totals
    total_cost = 0
    for rental in rentals:
        total_cost += rental.total_cost
    # add total cost to context
    context = {'rentals': rentals, 'total_cost': total_cost}
    return render(request, 'equipment_list_set.html', context)


# Generate text report of set equipment rentals
def set_equipment_txt(request):
    """ This will print a text file of all the rental equipment."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="set_rentals_report.txt"'
    rentals = Rental.objects.filter(category='set_equipment').order_by('start_rental_date')
    lines = []
    for rental in rentals:
        lines.append(f"Rental Item: {rental.rental_item}\n First Name: {rental.first_name}\n Last Name: {rental.last_name}\n Title: {rental.title}\n Department: {rental.department}\n Production: {rental.production}\n Vendor: {rental.vendor}\n Scene Info: {rental.scene_info}\n Start Rental Date: {rental.start_rental_date}\n End Rental Date: {rental.end_rental_date}\n Drop Off Location: {rental.drop_off_location}\n Drop Off Time: {rental.drop_off_time}\n Pick Up Location: {rental.pick_up_location}\n Pick Up Time: {rental.pick_up_time}\n Rental Type: {rental.rental_type}\n Category: {rental.category}\n Additional Tax Fees: {rental.addl_tax_fees}\n Total Cost: {rental.total_cost}\n Purchase Order: {rental.purchase_order}\n Quote Number: {rental.quote_number}\n Notes 1: {rental.notes1}\n Notes 2: {rental.notes2}\n Notes 3: {rental.notes3}\n\n ")
        response.writelines(lines)
    return response

# Generate csv report of set equipment rentals
def set_equipment_csv(request):
    """" create csv file of rental equipment report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="set_equipment_report.csv"'

    # Create a csv writer
    writer = csv.writer(response)

    # Designate The Model
    rentals = Rental.objects.filter(category='set_equipment').order_by('start_rental_date')

    # Add colum headings to the csv file
    writer.writerow(
        ['Rental Item', 'First Name', 'Last Name', 'Title', 'Department', 'Vendor', 'Scene Info',
         'Start Rental', 'End Rental',
         'Rental Type', 'Category', 'Total Cost', 'Purchase Order',
         'Quote Number'])

    # Loop through the rentals and write to the csv file
    for rental in rentals:
        writer.writerow([rental.rental_item, rental.first_name, rental.last_name, rental.title, rental.department,
                         rental.vendor.name, rental.scene_info, rental.start_rental_date,
                         rental.end_rental_date,
                         rental.rental_type, rental.category,
                         rental.total_cost, rental.purchase_order, rental.quote_number
                         ])

    return response

# Generate pdf report of set equipment rentals
def set_equipment_pdf(request):
    """ PDF view of rental list """
    # create Bytestream buffer
    buffer = io.BytesIO()
    # create a canvas and set multiple pages
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    # create text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    rentals = Rental.objects.filter(category='set_equipment').order_by('start_rental_date')

    lines = []

    for rental in rentals:
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
        lines.append(f"Additional Tax Fees: {rental.addl_tax_fees}")
        lines.append(f"Total Cost: {rental.total_cost}")
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
    return FileResponse(buffer, as_attachment=True, filename='set_equipment_report.pdf')



#################  office equipment rental list view #####################
#################  office equipment rental list view #####################

# production office equipment list view
def production_office_equipment_list(request):
     """ User list page view. This is for admins to view all users."""
     rentals = Rental.objects.filter(category='office_equipment').order_by('start_rental_date')
     # add up total cost totals
     total_cost = 0
     for rental in rentals:
         total_cost += rental.total_cost
     # add total cost to context
     context = {'rentals': rentals, 'total_cost': total_cost}
     return render(request, 'equipment_list_office.html', context)

# Generate text report of set equipment rentals
def office_equipment_txt(request):
    """ This will print a text file of all the rental equipment."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="office_rentals_report.txt"'
    rentals = Rental.objects.filter(category='office_equipment').order_by('start_rental_date')
    lines = []
    for rental in rentals:
        lines.append(f"Rental Item: {rental.rental_item}\n First Name: {rental.first_name}\n Last Name: {rental.last_name}\n Title: {rental.title}\n Department: {rental.department}\n Production: {rental.production}\n Vendor: {rental.vendor}\n Scene Info: {rental.scene_info}\n Start Rental Date: {rental.start_rental_date}\n End Rental Date: {rental.end_rental_date}\n Drop Off Location: {rental.drop_off_location}\n Drop Off Time: {rental.drop_off_time}\n Pick Up Location: {rental.pick_up_location}\n Pick Up Time: {rental.pick_up_time}\n Rental Type: {rental.rental_type}\n Category: {rental.category}\n Additional Tax Fees: {rental.addl_tax_fees}\n Total Cost: {rental.total_cost}\n Purchase Order: {rental.purchase_order}\n Quote Number: {rental.quote_number}\n Notes 1: {rental.notes1}\n Notes 2: {rental.notes2}\n Notes 3: {rental.notes3}\n\n ")
        response.writelines(lines)
    return response

# Generate csv report of set equipment rentals
def office_equipment_csv(request):
    """" create csv file of rental equipment report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="office_equipment_report.csv"'

    # Create a csv writer
    writer = csv.writer(response)

    # Designate The Model
    rentals = Rental.objects.filter(category='office_equipment').order_by('start_rental_date')

    # Add colum headings to the csv file
    writer.writerow(
        ['Rental Item', 'First Name', 'Last Name', 'Title', 'Department', 'Vendor', 'Purpose',
         'Start Rental', 'End Rental',
         'Rental Type', 'Category','Total Cost', 'Purchase Order',
         'Quote Number'])

    # Loop through the rentals and write to the csv file
    for rental in rentals:
        writer.writerow([rental.rental_item, rental.first_name, rental.last_name, rental.title, rental.department,
                         rental.vendor.name, rental.scene_info, rental.start_rental_date,
                         rental.end_rental_date,
                        rental.rental_type, rental.category,
                         rental.total_cost, rental.purchase_order, rental.quote_number])

    return response

# Generate pdf report of set equipment rentals
def office_equipment_pdf(request):
    """ PDF view of rental list """
    # create Bytestream buffer
    buffer = io.BytesIO()
    # create a canvas and set multiple pages
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    # create text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    rentals = Rental.objects.filter(category='office_equipment').order_by('start_rental_date')

    lines = []

    for rental in rentals:
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
        lines.append(f"Additional Tax Fees: {rental.addl_tax_fees}")
        lines.append(f"Total Cost: {rental.total_cost}")
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
    return FileResponse(buffer, as_attachment=True, filename='office_equipment_report.pdf')

#################  misc equipment rental list view #####################
#################  misc equipment rental list view #####################

# Misc equipment list view
def misc_equipment_list(request):
    """ User list page view. This is for admins to view all users."""
    rentals = Rental.objects.filter(category='misc_equipment').order_by('start_rental_date')
    # add up total cost totals
    total_cost = 0
    for rental in rentals:
        total_cost += rental.total_cost
    # add total cost to context
    context = {'rentals': rentals, 'total_cost': total_cost}
    return render(request, 'equipment_list_misc.html', context)



#################  service list view #####################
#################  service list view #####################

# service list view
def service_list(request):
    """ User list page view. This is for admins to view all users."""
    services = Service.objects.all().order_by('start_service_date')
    days_till_end = Service.days_to_end_service
    # add up total cost totals
    total_cost = 0
    for service in services:
        total_cost += service.total
    # add total cost to context
    context = {'services': services, 'total_cost': total_cost, 'days_till_end': days_till_end}
    return render(request, 'services_list.html', context)


# Print Service list as text
# Generate text report of set equipment rentals
def service_list_txt(request):
    """ This will print a text file of the service list."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="set_rentals_report.txt"'
    services = Service.objects.all().order_by('start_service_date')
    lines = []
    #fields = ['service', 'description', 'rate', 'total', 'start_service_date', 'end_service_date', 'vendor', 'service_location', 'requestor', 'title', 'production', 'department', 'purchase_order', 'payment_type', 'notes1', 'notes2', 'notes3',]
    for service in services:
        lines.append(f"Service: {service.service}\n Description: {service.description}\n Rate: {service.rate}\n Total: {service.total}\n Start Service Date: {service.start_service_date}\n End Service Date: {service.end_service_date}\n Vendor: {service.vendor}\n Service Location: {service.service_location}\n Requestor: {service.requestor}\n Title: {service.title}\n Production: {service.production}\n Department: {service.department}\n Purchase Order: {service.purchase_order}\n Payment Type: {service.payment_type}\n Notes 1: {service.notes1}\n Notes 2: {service.notes2}\n Notes 3: {service.notes3}\n\n ")
        response.writelines(lines)
    return response

# Print service list as csv
def service_list_csv(request):
    """" create csv file of rental equipment report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="service_report.csv"'

    # Create a csv writer
    writer = csv.writer(response)

    # Designate The Model
    services = Service.objects.all().order_by('start_service_date')

    # Add colum headings to the csv file
    writer.writerow(
        ['Service', 'Description', 'Total', 'Start Date', 'End Date', 'Vendor', 'Service Location',
         'Requestor', 'Title', 'Department', 'Purchase Order', 'Payment Type'])

    # Loop through the rentals and write to the csv file
    for service in services:
        writer.writerow([service.service, service.description, service.total, service.start_service_date,
                         service.end_service_date, service.vendor.name, service.service_location, service.requestor,
                         service.title, service.department, service.purchase_order,
                         service.payment_type])

    return response

# print service list as pdf
def service_list_pdf(request):
    """ PDF view of service list """
    # create Bytestream buffer
    buffer = io.BytesIO()
    # create a canvas and set multiple pages
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    # create text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)
    services = Service.objects.all().order_by('start_service_date')
    lines = []
    for service in services:
        lines.append(f"Service: {service.service}")
        lines.append(f"Description: {service.description}")
        lines.append(f"Rate: {service.rate}")
        lines.append(f"Total: {service.total}")
        lines.append(f"Start Service Date: {service.start_service_date}")
        lines.append(f"End Service Date: {service.end_service_date}")
        lines.append(f"Vendor: {service.vendor}")
        lines.append(f"Service Location: {service.service_location}")
        lines.append(f"Requestor: {service.requestor}")
        lines.append(f"Title: {service.title}")
        lines.append(f"Production: {service.production}")
        lines.append(f"Department: {service.department} ")
        lines.append(f"Purchase Order: {service.purchase_order} ")
        lines.append(f"Payment Type: {service.payment_type} ")
        lines.append(f"Notes 1: {service.notes1} ")
        lines.append(f"Notes 2: {service.notes2} ")
        lines.append(f"Notes 3: {service.notes3} ")
        lines.append("")
    for line in lines:
        textob.textLine(line)
    # Draw the text object on the canvas
    p.drawText(textob)
    p.showPage()
    p.save()
    buffer.seek(0)
    # Return response
    return FileResponse(buffer, as_attachment=True, filename='service_report.pdf')


# Service form
class ServiceFormView(CreateView):
    """ Rental information form view. This is for the admin to enter rental information."""
    model = Service
    template_name = 'service_form.html'
    fields = ['service', 'description', 'rate', 'total', 'start_service_date', 'end_service_date', 'vendor', 'service_location', 'requestor', 'title', 'production', 'department', 'purchase_order', 'payment_type', 'notes1', 'notes2', 'notes3',]
    context_object_name = 'form'
    success_url = reverse_lazy('service_form')

    def form_valid(self, form):
        start_service_date = form.cleaned_data.get('start_service_date')
        end_service_date = form.cleaned_data.get('end_service_date')

        # end rental date must be after start date
        if end_service_date < start_service_date:
            form.add_error('end_service_date', "End rental date must be after start service date.")
            return self.form_invalid(form)

        # start date must be before end date
        if start_service_date > end_service_date:
            form.add_error('start_service_date', "Start service date must be before end service date.")
            return self.form_invalid(form)

        messages.success(self.request, "Service information saved successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Service information failed to save.")
        return super().form_invalid(form)

# Service detail view
class ServiceDetailView(DetailView):
    """Service detail view. This is for the admin to view service details."""
    model = Service
    template_name = 'service_detail.html'
    context_object_name = 'service'

    def get_object(self, queryset=None):
        return get_object_or_404(Service, pk=self.kwargs.get('pk'))

# print service details as txt
def service_detail_txt(request, pk):
    """ This will print a text file of the service details."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="service_report.txt"'
    service = get_object_or_404(Service, pk=pk)
    lines = []
    lines.append(f"\n\n\n SERVICE DETAILS\n Production: {service.production}\n Service: {service.service}\n Description: {service.description}\n Rate: ${service.rate:,.2F}\n Total: ${service.total:,.2F}\n Start Service Date: {service.start_service_date}\n End Service Date: {service.end_service_date}\n Vendor: {service.vendor}\n Service Location: {service.service_location}\n Requestor: {service.requestor}\n Title: {service.title}\n Production: {service.production}\n Department: {service.department}\n Purchase Order: {service.purchase_order}\n Payment Type: {service.payment_type}\n Notes 1: {service.notes1}\n Notes 2: {service.notes2}\n Notes 3: {service.notes3}")
    response.writelines(lines)
    return response

# print service details as pdf
def service_detail_pdf(request, pk):
    """ PDF view of service details """
    # create Bytestream buffer
    buffer = io.BytesIO()
    # create a canvas and set multiple pages
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    # create text object
    textob = p.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)
    service = get_object_or_404(Service, pk=pk)
    lines = []
    lines.append('')
    lines.append('SERVICE DETAILS')
    lines.append('___________________')
    lines.append('')
    lines.append(f'Production: {service.production}')
    lines.append(f'Service: {service.service}')
    lines.append(f'Description: {service.description}')
    lines.append(f'Rate: ${service.rate:,.2f}')
    lines.append(f'Total: ${service.total:,.2f}')
    lines.append(f'Start Service Date: {service.start_service_date}')
    lines.append(f'End Service Date: {service.end_service_date}')
    lines.append(f'Vendor: {service.vendor}')
    lines.append(f'Service Location: {service.service_location}')
    lines.append(f'Requestor: {service.requestor}')
    lines.append(f'Title: {service.title}')
    lines.append(f'Department: {service.department}')
    lines.append(f'Purchase Order: {service.purchase_order}')
    lines.append(f'Payment Type: {service.payment_type}')
    lines.append(f'Notes 1: {service.notes1}')
    lines.append(f'Notes 2: {service.notes2}')
    lines.append(f'Notes 3: {service.notes3}')
    lines.append("")
    for line in lines:
        textob.textLine(line)
    # Draw the text object on the canvas
    p.drawText(textob)
    p.showPage()
    p.save()
    buffer.seek(0)
    # Return response
    return FileResponse(buffer, as_attachment=True, filename='service_report.pdf')

# Vendor update view
class ServiceUpdateView(UpdateView):
    """ Vendor update view. This is for the admin to update vendor information."""
    model = Service
    template_name = 'service_update.html'
    fields = ['service', 'description', 'rate', 'total', 'start_service_date', 'end_service_date', 'vendor',
              'service_location', 'requestor', 'title', 'production', 'department', 'purchase_order', 'payment_type', 'notes1', 'notes2', 'notes3',]
    context_object_name = 'form'
    success_url = reverse_lazy('service_list')

    def form_valid(self, form):
        messages.success(self.request, "Service information updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Service information failed to update.")
        return super().form_invalid(form)


# Vendor delete view
class ServiceDeleteView(DeleteView):
    """ Vendor delete view. This is for the admin to delete vendor information."""
    model = Service
    template_name = 'service_delete.html'
    context_object_name = 'service'
    success_url = reverse_lazy('service_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Service deleted successfully.")
        return super().delete(request, *args, **kwargs)



################## SEARCH VIEWS #####################
################## SEARCH VIEWS #####################
################## SEARCH VIEWS #####################
################## SEARCH VIEWS #####################


# search_by_category
class SearchRentals(ListView):
    model = Rental
    template_name = 'search_rentals.html'
    context_object_name = 'rentals'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                 Q(category__icontains=query) |
                 Q(rental_item__icontains=query) |
                 Q(first_name__icontains=query) |
                 Q(last_name__icontains=query) |
                 Q(rental_type__icontains=query) |
                 Q(total_cost__icontains=query) |
                 Q(purchase_order__contains=query) |
                 Q(quote_number__icontains=query) |
                 Q(department__department_name__icontains=query) |
                 Q(vendor__name__icontains=query)
            )

            # add up total cost totals
            total_cost = 0
            for rental in queryset:
                total_cost += rental.total_cost
            # add total cost to context
            self.extra_context = {'total_cost': total_cost}

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        data = context
        return context

# search_by_service
class SearchServices(ListView):
    model = Service
    template_name = 'search_service.html'
    context_object_name = 'services'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(service__icontains=query) |
                Q(vendor__name__icontains=query) |
                Q(requestor__icontains=query) |
                Q(purchase_order__contains=query) |
                Q(department__department_name__icontains=query)
            )

            # add up total cost totals
            total_cost = 0
            for service in queryset:
                total_cost += service.total
            # add total cost to context
            self.extra_context = {'total_cost': total_cost}


        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context



# Search vendors
class SearchVendors(ListView):
    model = Vendor
    template_name = 'search_vendors.html'
    context_object_name = 'vendors'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(category__name__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
