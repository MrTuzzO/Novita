from django.db import migrations


def seed_service_icons(apps, schema_editor):
    ServiceType = apps.get_model('service', 'ServiceType')

    icon_map = {
        'cyber-security': 'fa-shield-halved',
        'lawyer': 'fa-scale-balanced',
        'doctor': 'fa-user-doctor',
        'detective': 'fa-user-secret',
    }

    for slug, icon_class in icon_map.items():
        ServiceType.objects.filter(slug=slug).update(icon_class=icon_class)


def noop_reverse(apps, schema_editor):
    # Keep user-customized icons intact on reverse.
    return


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_servicetype_icon_class'),
    ]

    operations = [
        migrations.RunPython(seed_service_icons, noop_reverse),
    ]
