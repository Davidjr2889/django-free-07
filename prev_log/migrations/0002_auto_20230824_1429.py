# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-08-24 13:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("prev_log", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="forecastmanualchangelog",
            unique_together=set(
                [
                    (
                        "artigo",
                        "familia",
                        "bo",
                        "empresa",
                        "ano",
                        "mes",
                        "created_at",
                        "utilizador",
                    )
                ]
            ),
        ),
        migrations.AlterUniqueTogether(
            name="purchaseforecast",
            unique_together=set([("artigo", "familia", "bo", "empresa", "ano", "mes")]),
        ),
        migrations.AlterUniqueTogether(
            name="purchaseforecastopenrequest",
            unique_together=set(
                [
                    (
                        "artigo",
                        "familia",
                        "bo",
                        "empresa",
                        "ano",
                        "mes",
                        "utilizador",
                        "created_at",
                    )
                ]
            ),
        ),
        migrations.AlterUniqueTogether(
            name="saleforecast",
            unique_together=set([("artigo", "familia", "bo", "empresa", "ano", "mes")]),
        ),
        migrations.AlterUniqueTogether(
            name="saleforecastopenrequest",
            unique_together=set(
                [
                    (
                        "artigo",
                        "familia",
                        "bo",
                        "empresa",
                        "ano",
                        "mes",
                        "utilizador",
                        "created_at",
                    )
                ]
            ),
        ),
        migrations.AlterUniqueTogether(
            name="stockforecast",
            unique_together=set([("artigo", "familia", "bo", "empresa", "ano", "mes")]),
        ),
        migrations.AlterUniqueTogether(
            name="stockforecastopenrequest",
            unique_together=set(
                [
                    (
                        "artigo",
                        "familia",
                        "bo",
                        "empresa",
                        "ano",
                        "mes",
                        "utilizador",
                        "created_at",
                    )
                ]
            ),
        ),
        migrations.AlterUniqueTogether(
            name="tendency",
            unique_together=set([("artigo", "familia", "empresa", "bo")]),
        ),
    ]
