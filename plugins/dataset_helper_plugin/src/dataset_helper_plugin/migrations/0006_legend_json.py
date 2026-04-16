from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset_helper_plugin', '0005_sort_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogentry',
            name='legend_json',
            field=models.JSONField(
                blank=True,
                null=True,
                verbose_name='Legend',
                help_text='Custom legend definition: {type, items: [{name, color}]}',
            ),
        ),
    ]
