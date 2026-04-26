from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Wire up the post_save signal that auto-assigns Django Groups
        import accounts.signals  # noqa: F401
