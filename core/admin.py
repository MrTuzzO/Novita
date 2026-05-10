from django.contrib import admin
from .models import Banner, ContactMessage, ExpertApplication

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
	list_display = ('title', 'is_active')
	list_filter = ('is_active',)
	search_fields = ('title', 'description')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'email', 'subject', 'created_at')
	search_fields = ('full_name', 'email', 'subject', 'message')
	readonly_fields = ('created_at',)


@admin.register(ExpertApplication)
class ExpertApplicationAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'email', 'title', 'years_of_experience', 'status', 'submitted_at')
	list_filter = ('status',)
	search_fields = ('full_name', 'email', 'title', 'specialization')
	filter_horizontal = ('services',)
	readonly_fields = ('submitted_at',)
	list_editable = ('status',)
	fields = ('full_name', 'email', 'phone_number', 'title', 'specialization',
	          'years_of_experience', 'bio', 'services', 'document', 'status', 'submitted_at')
