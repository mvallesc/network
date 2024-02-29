from django.contrib import admin

from .models import User, Post

# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'likes_count', 'created_at')

    def likes_count(self, obj):
        return obj.likes.count()


admin.site.register(User)
admin.site.register(Post, PostAdmin)
