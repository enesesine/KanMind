from django.contrib import admin
from .models import Board, Task, Comment


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("title", "owner")
    search_fields = ("title", "owner__email")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ("title", "board", "assignee", "reviewer", "status")
    list_filter   = ("status", "priority")
    search_fields = ("title", "description")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ("id", "task", "author", "created_at")
    list_filter   = ("created_at",)
    search_fields = ("author__fullname", "content")
