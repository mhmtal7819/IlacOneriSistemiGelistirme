from django.contrib import admin
from .models import User, Medication, UserMedication

admin.site.register(User)
admin.site.register(Medication)
admin.site.register(UserMedication)
