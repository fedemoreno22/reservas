import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reservas.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "admin@example.com"
password = "admin"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superusuario '{username}' creado con éxito.")
else:
    print(f"El superusuario '{username}' ya existe.")
