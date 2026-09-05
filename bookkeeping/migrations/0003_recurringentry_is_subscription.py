from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookkeeping", "0002_alter_expense_receipt"),
    ]

    operations = [
        migrations.AddField(
            model_name="recurringentry",
            name="is_subscription",
            field=models.BooleanField(
                default=False,
                help_text="Mark as a subscription (e.g. Netflix, Adobe) to include it on the Subscriptions overview.",
            ),
        ),
    ]
