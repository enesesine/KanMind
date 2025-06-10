from django.db import models
from auth_app.models import CustomUser


class Board(models.Model):
    """
    A Kanban board. 'owner' creates the board, 'members' can access it.
    """
    title = models.CharField(max_length=255)

    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )

    # Users who are members of this board
    members = models.ManyToManyField(
        CustomUser,
        related_name="boards",
        blank=True,
    )

    def __str__(self) -> str:
        return self.title


class Task(models.Model):
    """
    A task card within a board.
    """

    # ----------- Choice fields ----------
    PRIORITY_CHOICES = (
        ("low",    "Low"),
        ("medium", "Medium"),
        ("high",   "High"),
    )

    STATUS_CHOICES = (
        ("todo",        "To Do"),
        ("in_progress", "In Progress"),
        ("review",      "Review"),
        ("done",        "Done"),
    )

    # ----------- Core fields -----------
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="todo",
    )

    # ----------- Relations -------------
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    # User who created the task (used for permission checks)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
    )

    # Assigned user (optional)
    assignee = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )

    # Reviewer user (optional)
    reviewer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_to_review",
    )

    due_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """
    A comment attached to a task.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment {self.id} on Task {self.task_id}"
