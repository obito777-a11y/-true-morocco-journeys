# Generated migration — adds Booking and ContactMessage models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id",           models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name",         models.CharField(max_length=100)),
                ("email",        models.EmailField(db_index=True, max_length=254)),
                ("phone",        models.CharField(blank=True, default="", max_length=20)),
                ("tour_name",    models.CharField(max_length=200)),
                ("travel_date",  models.DateField()),
                ("num_people",   models.PositiveIntegerField(default=1)),
                ("message",      models.TextField(blank=True, default="")),
                ("status",       models.CharField(choices=[("pending","Pending"),("confirmed","Confirmed"),("cancelled","Cancelled")], db_index=True, default="pending", max_length=20)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("notes",        models.TextField(blank=True, default="", verbose_name="Admin notes")),
            ],
            options={"ordering": ["-submitted_at"], "verbose_name": "Booking", "verbose_name_plural": "Bookings"},
        ),
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                ("id",           models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name",         models.CharField(max_length=100)),
                ("email",        models.EmailField(db_index=True, max_length=254)),
                ("phone",        models.CharField(blank=True, default="", max_length=20)),
                ("subject",      models.CharField(blank=True, default="", max_length=200)),
                ("message",      models.TextField()),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-submitted_at"], "verbose_name": "Contact Message", "verbose_name_plural": "Contact Messages"},
        ),
    ]
