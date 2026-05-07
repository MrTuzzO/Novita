from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('summary', models.CharField(max_length=220)),
                ('image', models.ImageField(blank=True, null=True, upload_to='events/')),
                ('category', models.CharField(choices=[('recovery', 'Recovery Program'), ('wellness', 'Wellness Session'), ('community', 'Community Event'), ('workshop', 'Workshop')], default='recovery', max_length=20)),
                ('event_date', models.DateField()),
                ('location', models.CharField(max_length=140)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('interested_users', models.ManyToManyField(blank=True, related_name='interested_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['event_date', 'title']},
        ),
    ]
