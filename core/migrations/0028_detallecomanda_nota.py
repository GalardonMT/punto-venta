from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20250714_0427'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallecomanda',
            name='nota',
            field=models.TextField(blank=True, null=True),
        ),
    ]
