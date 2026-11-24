from django.db import migrations


def map_roles_forward(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    # Update university users
    CustomUser.objects.filter(role='university').update(role='organization', org_type='university')
    # Update industry users
    CustomUser.objects.filter(role='industry').update(role='organization', org_type='industry')
    # Update student users
    CustomUser.objects.filter(role='student').update(role='citizen')


def map_roles_reverse(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    CustomUser.objects.filter(role='organization', org_type='university').update(role='university')
    CustomUser.objects.filter(role='organization', org_type='industry').update(role='industry')
    CustomUser.objects.filter(role='organization', org_type='government_ngo').update(role='industry')
    CustomUser.objects.filter(role='citizen').update(role='student')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_customuser_org_type_alter_customuser_is_verified_and_more'),
    ]

    operations = [
        migrations.RunPython(map_roles_forward, map_roles_reverse),
    ]
