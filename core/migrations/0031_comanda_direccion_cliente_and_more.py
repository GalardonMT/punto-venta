from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_cliente_direccioncliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='comanda',
            name='direccion_cliente',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='historialcomanda',
            name='direccion_cliente',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
