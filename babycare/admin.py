from django.contrib import admin

from .models import BabyCareRequest, BabyCareUpdate


class BabyCareUpdateInline(admin.TabularInline):
    model = BabyCareUpdate
    extra = 0
    fields = ('note', 'is_visible_to_parent', 'created_by', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(BabyCareRequest)
class BabyCareRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'parent_full_name', 'child_name', 'care_shift', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('request_id', 'parent_full_name', 'email', 'phone_number', 'child_name', 'care_requirements')
    readonly_fields = ('request_id', 'created_at', 'updated_at')
    inlines = [BabyCareUpdateInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, BabyCareUpdate) and not obj.created_by_id:
                obj.created_by = request.user
            obj.save()
        formset.save_m2m()


@admin.register(BabyCareUpdate)
class BabyCareUpdateAdmin(admin.ModelAdmin):
    list_display = ('care_request', 'is_visible_to_parent', 'created_by', 'created_at')
    list_filter = ('is_visible_to_parent', 'created_at')
    search_fields = ('care_request__request_id', 'care_request__parent_full_name', 'note')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
