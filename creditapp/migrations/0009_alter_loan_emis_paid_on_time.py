# Generated by Django 5.0.2 on 2024-02-17 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creditapp', '0008_rename_monthly_repayment_loan_monthly_installment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='emis_paid_on_time',
            field=models.IntegerField(null=True),
        ),
    ]