from django.contrib import admin
from .models import StatusReport

# Register your models here.


class StatusReportAdmin(admin.ModelAdmin):
    model = StatusReport

admin.site.register(StatusReport, StatusReportAdmin)