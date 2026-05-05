from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import ExpertProfile, ServiceInquiry, ServiceMessage, ServiceMessageAttachment, ServiceType

User = get_user_model()


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'icon_class', 'short_description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'title', 'years_of_experience', 'is_available')
    list_filter = ('is_available', 'services')
    search_fields = ('user__email', 'user__full_name', 'title', 'specialization')
    filter_horizontal = ('services',)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'user':
    #         kwargs['queryset'] = User.objects.filter(
    #             role='expert',
    #             is_active=True,
    #         ).filter(Q(expert_profile__isnull=True))
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ServiceMessageAttachmentInline(admin.TabularInline):
    model = ServiceMessageAttachment
    extra = 0
    readonly_fields = ('uploaded_at', 'uploaded_by', 'file_size')


@admin.register(ServiceMessage)
class ServiceMessageAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('inquiry__inquiry_id', 'inquiry__subject', 'message', 'user__email')
    inlines = [ServiceMessageAttachmentInline]


@admin.register(ServiceInquiry)
class ServiceInquiryAdmin(admin.ModelAdmin):
    list_display = ('inquiry_id', 'subject', 'service_type', 'user', 'expert', 'status', 'created_at')
    list_filter = ('status', 'service_type', 'created_at')
    search_fields = ('inquiry_id', 'subject', 'user__email', 'expert__email')
    readonly_fields = ('inquiry_id', 'created_at', 'updated_at', 'closed_at')


@admin.register(ServiceMessageAttachment)
class ServiceMessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ('message', 'original_filename', 'uploaded_by', 'uploaded_at')
    search_fields = ('message__inquiry__inquiry_id', 'original_filename', 'uploaded_by__email')
