# Generated by Django 5.2.4 on 2025-07-20 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestionContratos', '0006_terminoscondiciones_actividadusuario_registrosesion'),
    ]

    operations = [
        migrations.AddField(
            model_name='terminoscondiciones',
            name='fecha_modificacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
