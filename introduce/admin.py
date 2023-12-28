from django.contrib import admin
from .models import Post, Comment

# Register your models here.
class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1
    fields = ('content', 'user', 'writer', 'is_admin', 'created_at', 'updated_at')
    readonly_fields = ('writer', 'is_admin', 'created_at', 'updated_at')

    def writer(self, instance):
        return instance.user.nickname

    def is_admin(self, instance):
        return instance.user.is_admin

    is_admin.boolean = True
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'writer', 'is_admin', 'created_at', 'updated_at']
    list_display_links = ['title']
    inlines = [CommentInline]

    def writer(self, obj):
        return obj.user.nickname
    writer.admin_order_field = 'user__nickname'
    def is_admin(self, obj):
        return obj.user.is_admin
    is_admin.boolean = True
    is_admin.admin_order_field = 'user__is_admin'

admin.site.register(Post, PostAdmin)