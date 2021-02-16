# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-16 15:56
from __future__ import unicode_literals

import django.core.validators
import django.db.models.deletion
import enumfields.fields
from django.db import migrations, models

import shuup_product_reviews.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shuup', '0050_move_product_status_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)], verbose_name='rating')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('would_recommend', models.BooleanField(default=False, help_text='Indicates whether you would recommend this product to a friend.', verbose_name='Would recommend to a friend?')),
                ('status', enumfields.fields.EnumIntegerField(db_index=True, default=1, enum=shuup_product_reviews.models.ReviewStatus)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to='shuup.Order', verbose_name='order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to='shuup.Product', verbose_name='product')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to='shuup.Contact', verbose_name='reviewer')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to='shuup.Shop', verbose_name='shop')),
            ],
        ),
        migrations.CreateModel(
            name='ProductReviewAggregation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.DecimalField(decimal_places=1, default=0, max_digits=2, verbose_name='rating')),
                ('review_count', models.PositiveIntegerField(default=0, verbose_name='review count')),
                ('would_recommend', models.PositiveIntegerField(default=0, verbose_name='users would recommend')),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews_aggregation', to='shuup.Product', verbose_name='product')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='productreview',
            unique_together=set([('reviewer', 'product')]),
        ),
    ]
