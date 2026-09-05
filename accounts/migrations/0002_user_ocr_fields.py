from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="ocr_provider",
            field=models.CharField(
                blank=True,
                choices=[
                    ("anthropic", "Anthropic (Claude)"),
                    ("openai", "OpenAI (GPT-4o)"),
                ],
                default="anthropic",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="ocr_api_key",
            field=models.CharField(
                blank=True,
                help_text="Your Anthropic or OpenAI API key. Stored encrypted at rest.",
                max_length=200,
            ),
        ),
    ]
