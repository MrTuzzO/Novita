from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_category_is_featured_blogpost_approval'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='blogpost',
            name='slug',
        ),
    ]
