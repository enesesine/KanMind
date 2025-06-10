from django.contrib import admin
from .models import Board, Task, Comment

# Admin configuration for the Board model
@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view
    list_display = ("title", "owner")
    # Enable search by board title and owner's email
    search_fields = ("title", "owner__email")

# Admin configuration for the Task model
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view
    list_display  = ("title", "board", "assignee", "reviewer", "status")
    # Enable filtering by status and priority in the admin sidebar
    list_filter   = ("status", "priority")
    # Enable search by task title and description
    search_fields = ("title", "description")

# Admin configuration for the Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view
    list_display  = ("id", "task", "author", "created_at")
    # Enable filtering by creation date
    list_filter   = ("created_at",)
    # Enable search by author's name and comment content
    search_fields = ("author__fullname", "content")
