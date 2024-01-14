from django.contrib import admin

from .models import Geopoint


@admin.register(Geopoint)
class GeopointAdmin(admin.ModelAdmin):
    pass
