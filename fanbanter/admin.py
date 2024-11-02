from django.contrib import admin
from .models import FanBanterPost, FanBanterLike, FanBanterComment



# Dynamic registration of models without customization
models = [ FanBanterPost, FanBanterLike, FanBanterComment ]

for model in models:
    admin.site.register(model)