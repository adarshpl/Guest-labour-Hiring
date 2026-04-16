from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('hiring', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='PoliceOfficer',
            fields=[
                ('pid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(unique=True)),
                ('badge_number', models.CharField(blank=True, max_length=50)),
                ('login', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='police_profile',
                    to='hiring.userprofile'
                )),
            ],
        ),
    ]
