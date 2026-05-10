from django.contrib import admin

from .models import AdmissionRequest, AdmissionUpdate


class AdmissionUpdateInline(admin.TabularInline):
    model = AdmissionUpdate
    extra = 0
    fields = ('note', 'is_visible_to_applicant', 'created_by', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(AdmissionRequest)
class AdmissionRequestAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'full_name', 'email', 'phone_number', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('application_id', 'full_name', 'email', 'phone_number')
    readonly_fields = ('application_id', 'created_at', 'updated_at')
    inlines = [AdmissionUpdateInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, AdmissionUpdate) and not obj.created_by_id:
                obj.created_by = request.user
            obj.save()
        formset.save_m2m()


@admin.register(AdmissionUpdate)
class AdmissionUpdateAdmin(admin.ModelAdmin):
    list_display = ('admission_request', 'is_visible_to_applicant', 'created_by', 'created_at')
    list_filter = ('is_visible_to_applicant', 'created_at')
    search_fields = ('admission_request__application_id', 'admission_request__full_name', 'note')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
