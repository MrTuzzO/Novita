from django import forms
from django.contrib.auth import get_user_model
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import BlogPost, Comment, Category

User = get_user_model()

_INPUT = (
    'w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-800 '
    'placeholder:text-slate-400 focus:outline-none focus:ring-2 '
    'focus:ring-[var(--color-primary)] focus:border-transparent'
)


class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget(config_name='blog_post'))

    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'excerpt', 'content', 'featured_image', 'status']
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name != 'content':
                field.widget.attrs.setdefault('class', _INPUT)

        self.fields['title'].label = 'What would you like to share?'
        self.fields['title'].help_text = 'Create an engaging title that captures your story or message'
        self.fields['excerpt'].label = 'Brief Summary'
        self.fields['excerpt'].help_text = 'A short preview of your story that will appear in the community feed'
        self.fields['content'].label = 'Your Story'
        self.fields['featured_image'].label = 'Add an Image (Optional)'
        self.fields['featured_image'].help_text = 'Share a meaningful image with your story (recommended: 1200x600px)'
        self.fields['category'].label = 'Blog Category'
        self.fields['category'].help_text = 'Choose the most relevant topic for your post'
        self.fields['status'].label = 'Post Status'
        self.fields['status'].help_text = 'Draft: Only visible to you | Published: Visible to community | Archived: Hidden from everyone'

    def save(self, commit=True):
        blog_post = super().save(commit=False)
        if self.user:
            blog_post.author = self.user
        if commit:
            blog_post.save()
            self.save_m2m()
        return blog_post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your comment here...',
                'class': _INPUT,
            })
        }


class BlogSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search posts...'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="All Categories",
        required=False,
    )