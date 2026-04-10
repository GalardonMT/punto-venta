from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_comanda_numero_cliente_comanda_telefono_cliente_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=30)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DireccionCliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(max_length=255)),
                ('cliente', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='direcciones', to='core.cliente')),
            ],
        ),
    ]
