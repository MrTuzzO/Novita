from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'event_date', 'location', 'is_active', 'interested_total')
    list_filter = ('category', 'is_active', 'event_date')
    search_fields = ('title', 'summary', 'location')
    filter_horizontal = ('interested_users',)

    def interested_total(self, obj):
        return obj.interested_users.count()

    interested_total.short_description = 'Interested Users'
