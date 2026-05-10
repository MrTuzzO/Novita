from django.contrib import admin

from .models import Course, CourseModule, Enrollment, LessonProgress, ModuleLesson


class ModuleLessonInline(admin.TabularInline):
    model = ModuleLesson
    extra = 1
    fields = ('title', 'video_url', 'video_file', 'order')


class CourseModuleInline(admin.StackedInline):
    model = CourseModule
    extra = 1
    fields = ('title', 'summary', 'order')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'mode', 'fee', 'is_active', 'start_date', 'duration_weeks')
    list_filter = ('mode', 'is_active')
    search_fields = ('title', 'short_description', 'description')
    fields = ('title', 'mode', 'short_description', 'description', 'thumbnail', 'fee', 'stripe_product_id', 'location', 'start_date', 'duration_weeks', 'is_active')


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [ModuleLessonInline]


@admin.register(ModuleLesson)
class ModuleLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    list_filter = ('module__course', 'module')
    search_fields = ('title', 'module__title', 'module__course__title')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'enrolled_at', 'payment_confirmed_at', 'completed_at')
    list_filter = ('course', 'status', 'enrolled_at', 'payment_confirmed_at', 'completed_at')
    search_fields = ('user__email', 'user__full_name', 'course__title')
    readonly_fields = ('enrolled_at', 'stripe_session_id', 'payment_confirmed_at')
    fields = ('user', 'course', 'status', 'enrolled_at', 'payment_confirmed_at', 'completed_at', 'stripe_session_id')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed', 'lesson__module__course')
    search_fields = ('enrollment__user__email', 'lesson__title', 'lesson__module__course__title')
