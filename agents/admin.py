# siteapp/admin.py
from django.contrib import admin
from .models import Agent
from .models import GlobalWhatsApp
from .models import Post, Category


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('display_id', 'type_label', 'site_text', 'phone_display')  # ✅ Fixed
    prepopulated_fields = {'slug': ('display_id',)}

admin.site.register(GlobalWhatsApp)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    prepopulated_fields = {"slug": ("title",)}  # auto creates slug preview

admin.site.register(Post, PostAdmin)
admin.site.register(Category)