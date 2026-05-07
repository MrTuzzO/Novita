from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import BlogPost, Category, Comment, PostLike
from .forms import BlogPostForm, CommentForm, BlogSearchForm

def blog_home(request):
    """Community forum homepage with recent posts and popular content"""
    # Show recent community posts
    recent_posts = BlogPost.objects.filter(
        status='published',
        is_approved=True,
    ).select_related('author', 'category')[:9]
    
    # Show popular posts (most liked)
    popular_posts = BlogPost.objects.filter(
        status='published',
        is_approved=True,
    ).select_related('author', 'category').order_by('-likes_count', '-views_count')[:3]
    
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published', posts__is_approved=True))
    ).filter(post_count__gt=0)
    
    context = {
        'recent_posts': recent_posts,
        'popular_posts': popular_posts,
        'categories': categories,
    }
    return render(request, 'blog/home.html', context)

def blog_list(request):
    """Blog post list with pagination and filtering"""
    posts = BlogPost.objects.filter(status='published', is_approved=True).select_related(
        'author', 'category'
    )

    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published', posts__is_approved=True))
    ).filter(post_count__gt=0)
    
    # Search functionality
    search_form = BlogSearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        
        if query:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(content__icontains=query)
            )
        
        if category:
            posts = posts.filter(category=category)
    
    # Pagination
    paginator = Paginator(posts, 6)  # 6 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_posts': posts.count(),
        'categories': categories,
    }
    return render(request, 'blog/list.html', context)

def blog_detail(request, pk):
    """Individual blog post detail view"""
    post = get_object_or_404(
        BlogPost.objects.select_related('author', 'category'),
        pk=pk,
    )

    can_preview = request.user.is_authenticated and (
        request.user == post.author or request.user.is_staff or request.user.is_superuser
    )

    # Archived posts are not visible from detail page.
    if post.status == 'archived' and not can_preview:
        post = get_object_or_404(
            BlogPost.objects.select_related('author', 'category'),
            pk=pk,
            status='published',
            is_approved=True,
        )

    # Draft posts can only be previewed by author/staff/admin.
    if post.status == 'draft' and not can_preview:
        post = get_object_or_404(
            BlogPost.objects.select_related('author', 'category'),
            pk=pk,
            status='published',
            is_approved=True,
        )

    if post.status == 'published' and not post.is_approved and not can_preview:
        post = get_object_or_404(
            BlogPost.objects.select_related('author', 'category'),
            pk=pk,
            status='published',
            is_approved=True,
        )
    
    # Increment view count
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    # Get comments
    comments = post.comments.filter(
        is_approved=True, 
        parent=None
    ).select_related('author').prefetch_related('replies')
    
    # Check if user liked the post
    user_liked = False
    if request.user.is_authenticated:
        user_liked = PostLike.objects.filter(post=post, user=request.user).exists()
    
    # Related posts
    related_posts = BlogPost.objects.filter(
        category=post.category,
        status='published',
        is_approved=True,
    ).exclude(id=post.id)[:3]
    
    # Comment form
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_liked': user_liked,
        'related_posts': related_posts,
    }
    return render(request, 'blog/detail.html', context)

@login_required
def create_post(request):
    """Create new blog post"""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = form.save()
            
            # Show appropriate success message based on status
            if post.status == 'draft':
                messages.success(request, f'Draft "{post.title}" has been saved successfully!')
            elif post.status == 'published':
                if post.is_approved:
                    messages.success(request, f'Post "{post.title}" has been published successfully!')
                else:
                    messages.success(request, f'Post "{post.title}" was submitted and is waiting for staff approval.')
            elif post.status == 'archived':
                messages.success(request, f'Post "{post.title}" has been archived successfully!')
            
            # Redirect based on post status
            if post.status == 'archived':
                return redirect('blog:my_posts')
            else:
                return redirect('blog:detail', pk=post.pk)
    else:
        form = BlogPostForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create New Post'
    }
    return render(request, 'blog/create_post.html', context)

@login_required
def edit_post(request, pk):
    """Edit existing blog post"""
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post, user=request.user)
        if form.is_valid():
            post = form.save()
            
            # Show appropriate success message based on status
            if post.status == 'draft':
                messages.success(request, f'Draft "{post.title}" has been updated successfully!')
            elif post.status == 'published':
                if post.is_approved:
                    messages.success(request, f'Post "{post.title}" has been updated and is published!')
                else:
                    messages.success(request, f'Post "{post.title}" has been updated and is waiting for staff approval.')
            elif post.status == 'archived':
                messages.success(request, f'Post "{post.title}" has been archived successfully!')
                
            # Redirect based on post status
            if post.status == 'archived':
                return redirect('blog:my_posts')
            else:
                return redirect('blog:detail', pk=post.pk)
    else:
        form = BlogPostForm(instance=post, user=request.user)
    
    context = {
        'form': form,
        'post': post,
        'title': f'Edit: {post.title}'
    }
    return render(request, 'blog/edit_post.html', context)

@login_required
def delete_post(request, pk):
    """Delete a blog post (author only)"""
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f'Your post "{post_title}" has been deleted successfully.')
        return redirect('blog:my_posts')
    
    context = {
        'post': post,
    }
    return render(request, 'blog/delete_post.html', context)

@login_required
@require_POST
def add_comment(request, pk):
    """Add comment to blog post"""
    post = get_object_or_404(BlogPost, pk=pk, status='published', is_approved=True)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        
        # Handle parent comment for replies
        parent_id = request.POST.get('parent_id')
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            comment.parent = parent_comment
        
        comment.save()
        messages.success(request, 'Your comment has been added successfully!')
    else:
        messages.error(request, 'Please correct the errors in your comment.')
    
    return redirect('blog:detail', pk=pk)

@login_required
@require_POST
def toggle_like(request, pk):
    """Toggle like/unlike for a blog post"""
    post = get_object_or_404(BlogPost, pk=pk, status='published', is_approved=True)
    
    like, created = PostLike.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if not created:
        # Unlike the post
        like.delete()
        liked = False
        post.likes_count -= 1
    else:
        # Like the post
        liked = True
        post.likes_count += 1
    
    post.save(update_fields=['likes_count'])
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes_count
    })

def category_posts(request, pk):
    """Posts filtered by category"""
    category = get_object_or_404(Category, pk=pk)
    posts = BlogPost.objects.filter(
        category=category,
        status='published',
        is_approved=True,
    ).select_related('author', 'category')

    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published', posts__is_approved=True))
    ).filter(post_count__gt=0)
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'total_posts': posts.count(),
        'categories': categories,
    }
    return render(request, 'blog/category.html', context)

@login_required
def my_posts(request):
    """User's own blog posts (including archived)"""
    posts = BlogPost.objects.filter(
        author=request.user
    ).select_related('category')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_posts': posts.count(),
    }
    return render(request, 'blog/my_posts.html', context)
