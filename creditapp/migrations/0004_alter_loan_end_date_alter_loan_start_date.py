# Generated by Django 5.0.2 on 2024-02-16 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creditapp', '0003_alter_customer_current_debt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]
