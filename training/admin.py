
from django.contrib import admin
from .models import Training, ModuleType

@admin.register(ModuleType)
class ModuleTypeAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "code", "created_at", "updated_at")
	search_fields = ("name", "code")
	list_filter = ("created_at", "updated_at")

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "date", "module_type", "status", "training_type", "training_center", "created_at", "updated_at")
	search_fields = ("name", "sponsor", "training_center")
	list_filter = ("status", "training_type", "module_type", "created_at", "updated_at")
	filter_horizontal = ("users", "cohorts")
