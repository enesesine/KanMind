# kanban_app/models.py
from django.db import models
from auth_app.models import CustomUser


class Board(models.Model):
    """
    Ein Kanban-Board.  Owner = Ersteller, Members = berechtigte User.
    """
    title = models.CharField(max_length=255)

    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )

    # weitere Nutzer mit Zugriff auf das Board
    members = models.ManyToManyField(
        CustomUser,
        related_name="boards",
        blank=True,
    )

    def __str__(self) -> str:
        return self.title


class Task(models.Model):
    """
    Eine einzelne Karte innerhalb eines Boards.
    """

    # ---------- Wahlfelder -------------------------------------------------
    PRIORITY_CHOICES = (
        ("low",    "Low"),
        ("medium", "Medium"),
        ("high",   "High"),
    )

    STATUS_CHOICES = (                              # inkl. „review“
        ("todo",        "To Do"),
        ("in_progress", "In Progress"),
        ("review",      "Review"),
        ("done",        "Done"),
    )

    # ---------- Grunddaten -------------------------------------------------
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

    # ---------- Beziehungen -----------------------------------------------
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    # wer die Task angelegt hat (für DELETE-Berechtigung)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
    )

    assignee = models.ForeignKey(                   # Bearbeiter
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    reviewer = models.ForeignKey(                   # Prüfer
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
    Ein Kommentar an eine Task.
    """
    task       = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author     = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment {self.id} on Task {self.task_id}"
