from django.db import migrations


def seed_service_types(apps, schema_editor):
    ServiceType = apps.get_model('service', 'ServiceType')

    seed_data = [
        {
            'name': 'Cyber Security',
            'slug': 'cyber-security',
            'short_description': 'Protection for harassment, hacking threats, and digital privacy incidents.',
            'details': 'Cyber security experts help analyze incidents, preserve evidence, and secure accounts after online abuse or compromise.',
            'how_it_works': '1) Share your issue and files.\n2) Expert reviews evidence and risk.\n3) You receive action steps and follow-up support.',
        },
        {
            'name': 'Lawyer',
            'slug': 'lawyer',
            'short_description': 'Legal direction for rights, documentation, and complaint preparation.',
            'details': 'Law professionals provide guidance on legal pathways, reporting strategy, and document handling for sensitive cases.',
            'how_it_works': '1) Submit case summary.\n2) Lawyer reviews timeline and documents.\n3) Receive legal options and recommended next steps.',
        },
        {
            'name': 'Doctor',
            'slug': 'doctor',
            'short_description': 'Health-focused consultations and practical care guidance.',
            'details': 'Medical experts offer remote guidance for symptoms, recovery concerns, and deciding the right level of care.',
            'how_it_works': '1) Explain symptoms and upload reports.\n2) Doctor assesses concerns.\n3) Receive advice and referral guidance if needed.',
        },
        {
            'name': 'Detective',
            'slug': 'detective',
            'short_description': 'Investigative support for evidence analysis and case reconstruction.',
            'details': 'Detective experts help structure incidents, verify details, and organize findings for further action.',
            'how_it_works': '1) Provide known facts and files.\n2) Detective builds an investigation path.\n3) You get a structured findings summary.',
        },
    ]

    for entry in seed_data:
        ServiceType.objects.update_or_create(
            slug=entry['slug'],
            defaults={
                'name': entry['name'],
                'short_description': entry['short_description'],
                'details': entry['details'],
                'how_it_works': entry['how_it_works'],
                'is_active': True,
            },
        )


def unseed_service_types(apps, schema_editor):
    ServiceType = apps.get_model('service', 'ServiceType')
    ServiceType.objects.filter(slug__in=['cyber-security', 'lawyer', 'doctor', 'detective']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_service_types, unseed_service_types),
    ]
