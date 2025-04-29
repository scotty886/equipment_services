from django.contrib import admin


from .models import Production, Department, Vendor, Rental, Service, VendorCategory

# Register your models here.

admin.site.register(Production)
admin.site.register(Department)
admin.site.register(Vendor)
admin.site.register(Rental)
admin.site.register(Service)
admin.site.register(VendorCategory)

