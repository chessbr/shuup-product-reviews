# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-07-24 08:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import parler.models


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0069_shop_supplier_service_providers'),
        ('shuup_vendor_reviews', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorReviewOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=False, verbose_name='enabled')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_reviews_option', to='shuup.Shop', verbose_name='supplier')),
            ],
            options={
                'verbose_name': 'Vendor Review Option',
                'verbose_name_plural': 'Vendor Review Options',
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='VendorReviewOptionTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='shuup_vendor_reviews.VendorReviewOption')),
            ],
            options={
                'verbose_name': 'Vendor Review Option Translation',
                'db_table': 'shuup_vendor_reviews_vendorreviewoption_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.AlterField(
            model_name='vendorreviewaggregation',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_reviews_aggregation', to='shuup.Supplier', verbose_name='supplier'),
        ),
        migrations.AddField(
            model_name='vendorreview',
            name='option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vendor_review_options', to='shuup_vendor_reviews.VendorReviewOption'),
        ),
        migrations.AddField(
            model_name='vendorreviewaggregation',
            name='option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vendor_review_agg_options', to='shuup_vendor_reviews.VendorReviewOption'),
        ),
        migrations.AlterUniqueTogether(
            name='vendorreviewaggregation',
            unique_together=set([('supplier', 'option')]),
        ),
        migrations.AlterUniqueTogether(
            name='vendorreviewoptiontranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
