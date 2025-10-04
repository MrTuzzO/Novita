from django import forms
from django.contrib.auth import get_user_model
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div, Field
from .models import BlogPost, Comment, Category

User = get_user_model()

class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget(config_name='blog_post'))
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'category', 'excerpt', 'content', 
            'featured_image', 'status'
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-8 mb-3'),
                Column('category', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            'excerpt',
            'content',
            Row(
                Column('featured_image', css_class='form-group col-md-8 mb-3'),
                Column('status', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Div(
                Submit('save', 'Save Post', css_class='btn btn-primary'),
                css_class='d-flex justify-content-center'
            )
        )
        
        # Update field attributes
        for field_name, field in self.fields.items():
            if field_name not in []:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Customize labels and help text
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
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'content',
            Div(
                Submit('submit', 'Post Comment', css_class='btn btn-primary'),
                css_class='d-flex justify-content-end'
            )
        )

class BlogSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search posts...',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="All Categories",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('query', css_class='form-group col-md-8 mb-3'),
                Column('category', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Div(
                Submit('search', 'Search', css_class='btn btn-primary'),
                css_class='d-flex justify-content-center'
            )
        )