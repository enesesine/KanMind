from django.urls import path
from kanban_app.api.views import (
    BoardListCreateView,
    BoardDetailView,
    MyAssignedTasksView,
    MyReviewingTasksView,
    TaskListCreateView,
    TaskDetailView,
    TaskCommentsView,
    CommentDeleteView,
)

urlpatterns = [
    # BOARDS
    path("boards/",           BoardListCreateView.as_view(), name="board-list-create"),
    path("boards/<int:id>/",  BoardDetailView.as_view(),     name="board-detail"),

    # TASK-LISTEN
    path("tasks/assigned-to-me/", MyAssignedTasksView.as_view(),  name="tasks-assigned"),
    path("tasks/reviewing/",      MyReviewingTasksView.as_view(), name="tasks-reviewing"),

    # TASK CREATE
    path("tasks/",            TaskListCreateView.as_view(), name="task-list-create"),

    # TASK DETAIL → GET, PATCH & DELETE
    path("tasks/<int:id>/",   TaskDetailView.as_view(),       name="task-detail"),
    
    # TASK COMMENTS → GET + POST
    path("tasks/<int:task_id>/comments/", TaskCommentsView.as_view(), name="task-comments"),
    path("tasks/<int:task_id>/comments/<int:comment_id>/",CommentDeleteView.as_view(),name="comment-delete"),
]
