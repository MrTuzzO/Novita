from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import BlogPost, Category, Comment, PostLike

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_featured', 'post_count', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['name', 'description']
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_approved', 'approved_by', 'is_featured', 'views_count', 'created_at']
    list_filter = ['status', 'is_approved', 'category', 'is_featured', 'created_at']
    search_fields = ['title', 'excerpt', 'content']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    actions = ['approve_posts', 'unapprove_posts']
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'author', 'category')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Publishing', {
            'fields': ('status', 'is_approved', 'approved_at', 'approved_by', 'is_featured', 'published_at'),
            'classes': ['collapse']
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count'),
            'classes': ['collapse'],
        }),
    )
    
    readonly_fields = ['views_count', 'likes_count', 'approved_at', 'approved_by']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author" and not request.user.is_superuser:
            kwargs["queryset"] = request.user.__class__.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new post
            obj.author = request.user

        if obj.status == 'published' and obj.is_approved and not obj.approved_at:
            obj.approved_at = timezone.now()
            obj.approved_by = request.user

        if obj.status != 'published':
            obj.is_approved = False
            obj.approved_at = None
            obj.approved_by = None

        super().save_model(request, obj, form, change)

    @admin.action(description='Approve selected posts')
    def approve_posts(self, request, queryset):
        updated = queryset.filter(status='published').update(
            is_approved=True,
            approved_at=timezone.now(),
            approved_by=request.user,
        )
        self.message_user(request, f'{updated} post(s) approved.')

    @admin.action(description='Unapprove selected posts')
    def unapprove_posts(self, request, queryset):
        updated = queryset.update(
            is_approved=False,
            approved_at=None,
            approved_by=None,
        )
        self.message_user(request, f'{updated} post(s) moved back to pending approval.')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'content_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['author__email', 'post__title', 'content']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'post__title']
    ordering = ['-created_at']
