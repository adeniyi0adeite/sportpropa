from django.contrib import admin

# Register your models here.
from .models import Standing






# Dynamic registration of models without customization
models = [ Standing ]

for model in models:
    admin.site.register(model)