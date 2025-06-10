
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



#  BOARDS

class BoardListCreateView(ListCreateAPIView):
    serializer_class   = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        return Board.objects.filter(owner=u) | Board.objects.filter(members=u)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=request.user)

        payload = BoardSerializer(board).data | {
            "owner_id":              request.user.id,
            "member_count":          board.members.count(),
            "ticket_count":          board.tasks.count(),
            "tasks_to_do_count":     board.tasks.filter(status="todo").count(),
            "tasks_high_prio_count": board.tasks.filter(priority="high").count(),
        }
        return Response(payload, status=201)


class BoardDetailView(RetrieveUpdateDestroyAPIView):
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
            raise PermissionDenied("Kein Zugriff auf dieses Board.")
        return board

    def delete(self, request, *args, **kwargs):
        board = self.get_object()
        if request.user != board.owner:
            raise PermissionDenied("Nur der Eigentümer darf das Board löschen.")
        board.delete()
        return Response(status=204)


#  TASK-LISTEN (Assigned / Reviewing)

class MyAssignedTasksView(ListAPIView):
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        return Task.objects.filter(Q(assignee=u) | Q(reviewer=u))


class MyReviewingTasksView(ListAPIView):
    serializer_class   = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        return Task.objects.filter(reviewer=u).exclude(assignee=u)



#  TASK – Create  (POST /api/tasks/)

class TaskListCreateView(ListCreateAPIView):
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



#  TASK – Detail / Update / Delete (GET, PATCH, DELETE /api/tasks/<id>/)

class TaskDetailView(RetrieveUpdateDestroyAPIView):
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
            raise PermissionDenied("Kein Zugriff – du bist kein Mitglied dieses Boards.")
        return task

    def perform_destroy(self, instance: Task):
        user = self.request.user
        if user != instance.created_by and user != instance.board.owner:
            raise PermissionDenied("Nur Ersteller oder Board-Owner dürfen löschen.")
        instance.delete()



#  TASK – Comments  (GET & POST /api/tasks/<task_id>/comments/)

class TaskCommentsView(ListCreateAPIView):
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
            raise PermissionDenied("Nur Mitglieder des Boards dürfen Kommentare sehen oder anlegen.")

        return task.comments.all()

    def perform_create(self, serializer):
        task = get_object_or_404(Task.objects.select_related("board"), pk=self.kwargs["task_id"])
        user  = self.request.user
        board = task.board
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied("Nur Mitglieder des Boards dürfen Kommentare anlegen.")
        serializer.save(author=user, task=task)



#  COMMENT – Delete  (DELETE /api/tasks/<task_id>/comments/<comment_id>/)

class CommentDeleteView(DestroyAPIView):
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
            raise PermissionDenied("Nur der Ersteller des Kommentars darf ihn löschen.")
        return comment
