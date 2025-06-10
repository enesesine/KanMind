from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from kanban_app.models import Board, Task, Comment
from kanban_app.api.serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
)
from auth_app.models import CustomUser


# ==========================
# BOARDS
# ==========================

class BoardListCreateView(ListCreateAPIView):
    """List all boards where user is owner or member; create new board."""
    serializer_class   = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        return Board.objects.filter(owner=u) | Board.objects.filter(members=u)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=request.user)

        # Build response including stats
        payload = BoardSerializer(board).data | {
            "owner_id":              request.user.id,
            "member_count":          board.members.count(),
            "ticket_count":          board.tasks.count(),
            "tasks_to_do_count":     board.tasks.filter(status="todo").count(),
            "tasks_high_prio_count": board.tasks.filter(priority="high").count(),
        }
        return Response(payload, status=201)


class BoardDetailView(RetrieveUpdateDestroyAPIView):
    """View, update or delete a specific board."""
    queryset           = Board.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field       = "id"

    def get_serializer_class(self):
        if self.request.method.upper() == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_object(self):
        board = super().get_object()
        user  = self.request.user
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("Access denied – not a board member.")
        return board

    def delete(self, request, *args, **kwargs):
        board = self.get_object()
        if request.user != board.owner:
            raise PermissionDenied("Only the owner can delete the board.")
        board.delete()
        return Response(status=204)


# ==========================
# TASK LISTS
# ==========================

class MyAssignedTasksView(ListAPIView):
    """List tasks where the user is assignee or reviewer."""
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        return Task.objects.filter(Q(assignee=u) | Q(reviewer=u))


class MyReviewingTasksView(ListAPIView):
    """List tasks where the user is reviewer but not assignee."""
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        return Task.objects.filter(reviewer=u).exclude(assignee=u)


# ==========================
# TASK – Create and List
# ==========================

class TaskListCreateView(ListCreateAPIView):
    """List tasks across all accessible boards; create new task."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method.upper() == "POST":
            return TaskCreateSerializer
        return TaskSerializer

    def get_queryset(self):
        u = self.request.user
        return Task.objects.filter(Q(board__owner=u) | Q(board__members=u)).distinct()

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        task = ser.save()
        return Response(TaskSerializer(task).data, status=201)


# ==========================
# TASK – Detail / Update / Delete
# ==========================

class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """View, update or delete a specific task."""
    permission_classes = [IsAuthenticated]
    lookup_field       = "id"
    queryset           = Task.objects.select_related("board", "assignee", "reviewer")

    def get_serializer_class(self):
        if self.request.method.upper() == "PATCH":
            return TaskUpdateSerializer
        return TaskSerializer

    def get_object(self):
        task  = super().get_object()
        user  = self.request.user
        board = task.board
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("Access denied – not a board member.")
        return task

    def perform_destroy(self, instance: Task):
        user = self.request.user
        if user != instance.created_by and user != instance.board.owner:
            raise PermissionDenied("Only the creator or board owner may delete this task.")
        instance.delete()


# ==========================
# TASK – Comments List / Create
# ==========================

class TaskCommentsView(ListCreateAPIView):
    """List or create comments for a task."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method.upper() == "POST":
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        task = get_object_or_404(Task.objects.select_related("board"), pk=task_id)

        user  = self.request.user
        board = task.board
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("Only board members may view or create comments.")

        return task.comments.all()

    def perform_create(self, serializer):
        task  = get_object_or_404(Task.objects.select_related("board"), pk=self.kwargs["task_id"])
        user  = self.request.user
        board = task.board
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("Only board members may create comments.")
        serializer.save(author=user, task=task)


# ==========================
# COMMENT – Delete
# ==========================

class CommentDeleteView(DestroyAPIView):
    """Delete a specific comment (only allowed for author)."""
    permission_classes = [IsAuthenticated]

    def get_object(self):
        task_id    = self.kwargs["task_id"]
        comment_id = self.kwargs["comment_id"]
        comment = get_object_or_404(
            Comment.objects.select_related("author", "task"),
            pk=comment_id,
            task_id=task_id
        )

        if self.request.user != comment.author:
            raise PermissionDenied("Only the author may delete this comment.")
        return comment
