# Generated by Django 5.0.6 on 2024-07-15 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qdubl',
            name='op1',
            field=models.CharField(max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='qdubl',
            name='op2',
            field=models.CharField(max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='qdubl',
            name='op3',
            field=models.CharField(max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='qdubl',
            name='op4',
            field=models.CharField(max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='op1',
            field=models.CharField(max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='op2',
            field=models.CharField(max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='op3',
            field=models.CharField(max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='op4',
            field=models.CharField(max_length=10000, null=True),
        ),
    ]
