import os

DJANGO_ENV = os.getenv("DJANGO_ENV", "local")

if DJANGO_ENV == "docker":
    from .docker import *
else:
    from .local import *
