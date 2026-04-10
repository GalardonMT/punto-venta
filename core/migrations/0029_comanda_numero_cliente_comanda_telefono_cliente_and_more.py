from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_detallecomanda_nota'),
    ]

    operations = [
        migrations.AddField(
            model_name='comanda',
            name='numero_cliente',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='comanda',
            name='telefono_cliente',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='historialcomanda',
            name='numero_cliente',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historialcomanda',
            name='telefono_cliente',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
