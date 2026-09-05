from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_ocr_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="currency",
            field=models.CharField(
                blank=True,
                choices=[
                    ("GBP", "£ British Pound (GBP)"),
                    ("EUR", "€ Euro (EUR)"),
                    ("USD", "$ US Dollar (USD)"),
                ],
                default="GBP",
                help_text="The currency symbol shown throughout the app.",
                max_length=3,
            ),
        ),
    ]
