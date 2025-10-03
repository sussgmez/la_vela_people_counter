from django.contrib import admin
from .models import Entrance, File, Report, ReportDetail


@admin.register(Entrance)
class EntranceAdmin(admin.ModelAdmin):
    pass


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    pass


@admin.register(ReportDetail)
class ReportDetailAdmin(admin.ModelAdmin):
    pass
