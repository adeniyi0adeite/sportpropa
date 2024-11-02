from django.contrib import admin
from .models import UserProfile, Post, Comment, Like


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'date_of_birth', 'favorite_team', 'bio')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'bio')
    list_filter = ('favorite_team',)

    def username(self, obj):
        return obj.user.username

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    username.admin_order_field = 'user__username'  # Allows column order sorting
    first_name.admin_order_field = 'user__first_name'  # Allows column order sorting
    last_name.admin_order_field = 'user__last_name'  # Allows column order sorting
    username.short_description = 'Username'  # Renames column head
    first_name.short_description = 'First Name'  # Renames column head
    last_name.short_description = 'Last Name'  # Renames column head

admin.site.register(UserProfile, UserProfileAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'caption', 'created_at', 'updated_at', 'image')
    search_fields = ('author__user__username', 'caption')
    list_filter = ('created_at', 'updated_at')

admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'parent', 'content', 'created_at')
    search_fields = ('author__user__username', 'content')
    list_filter = ('created_at',)
    raw_id_fields = ('post', 'parent', 'author')

admin.site.register(Comment, CommentAdmin)


class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'comment', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)

admin.site.register(Like, LikeAdmin)
