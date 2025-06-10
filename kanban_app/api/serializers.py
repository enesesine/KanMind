from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from auth_app.models import CustomUser


# ------------------------- #
# Compact user representation for nested use
# ------------------------- #
class UserMiniSerializer(serializers.ModelSerializer):
    """Lightweight user info with id, email and fullname."""
    class Meta:
        model  = CustomUser
        fields = ["id", "email", "fullname"]


# ------------------------- #
# Task – read-only serializer for GET requests
# ------------------------- #
class TaskSerializer(serializers.ModelSerializer):
    """Returns task details with assignee/reviewer as nested users."""
    assignee       = UserMiniSerializer(read_only=True)
    reviewer       = UserMiniSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    board          = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model  = Task
        fields = [
            "id", "title", "description",
            "status", "priority",
            "assignee", "reviewer",
            "due_date", "comments_count",
            "board",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


# ------------------------- #
# Task – write serializer for creating new tasks
# ------------------------- #
class TaskCreateSerializer(serializers.ModelSerializer):
    """Handles task creation with permission and board membership checks."""
    board_id    = serializers.IntegerField(write_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model  = Task
        fields = [
            "board_id", "title", "description",
            "status", "priority",
            "assignee_id", "reviewer_id",
            "due_date",
            "id", "board", "assignee", "reviewer",
        ]
        read_only_fields = ["id", "board", "assignee", "reviewer"]

    def validate(self, attrs):
        user     = self.context["request"].user
        board_id = attrs["board_id"]

        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise serializers.ValidationError({"board_id": "Board not found."})

        # Only board members or the owner can create a task
        if user != board.owner and user not in board.members.all():
            raise serializers.ValidationError("You are not a member of this board.")

        # Optional assignee/reviewer must also be members
        for key in ("assignee_id", "reviewer_id"):
            uid = attrs.get(key)
            if uid is not None:
                try:
                    board.members.get(pk=uid)
                except CustomUser.DoesNotExist:
                    raise serializers.ValidationError({key: "User is not a member of that board."})

        attrs["board"] = board
        return attrs

    def create(self, validated_data):
        board        = validated_data.pop("board")
        assignee_id  = validated_data.pop("assignee_id", None)
        reviewer_id  = validated_data.pop("reviewer_id", None)

        return Task.objects.create(
            board      = board,
            created_by = self.context["request"].user,
            assignee   = CustomUser.objects.filter(pk=assignee_id).first(),
            reviewer   = CustomUser.objects.filter(pk=reviewer_id).first(),
            **validated_data,
        )


# ------------------------- #
# Task – update serializer for PATCH requests
# ------------------------- #
class TaskUpdateSerializer(serializers.ModelSerializer):
    """Handles partial task updates with board membership validation."""
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model  = Task
        fields = [
            "title", "description",
            "status", "priority",
            "assignee_id", "reviewer_id",
            "due_date",
            "id", "board", "assignee", "reviewer",
        ]
        read_only_fields = ["id", "board", "assignee", "reviewer"]

    def validate(self, attrs):
        task  = self.instance
        board = task.board

        for key in ("assignee_id", "reviewer_id"):
            if key in attrs:
                uid = attrs[key]
                if uid is not None and uid not in (task.assignee_id, task.reviewer_id):
                    try:
                        board.members.get(pk=uid)
                    except CustomUser.DoesNotExist:
                        raise serializers.ValidationError({key: "User is not a member of that board."})
        return attrs

    def update(self, instance, validated_data):
        # Update simple fields
        for field in ("title", "description", "status", "priority", "due_date"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        # Update relations if new IDs were provided
        if "assignee_id" in validated_data:
            instance.assignee = CustomUser.objects.filter(pk=validated_data["assignee_id"]).first()
        if "reviewer_id" in validated_data:
            instance.reviewer = CustomUser.objects.filter(pk=validated_data["reviewer_id"]).first()

        instance.save()
        return instance


# ------------------------- #
# Comment – read-only serializer
# ------------------------- #
class CommentSerializer(serializers.ModelSerializer):
    """Returns comment content along with author name and timestamp."""
    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model  = Comment
        fields = ["id", "created_at", "author", "content"]


# ------------------------- #
# Comment – create serializer for POST
# ------------------------- #
class CommentCreateSerializer(serializers.ModelSerializer):
    """Validates and creates a new comment for a task."""
    content = serializers.CharField()

    class Meta:
        model  = Comment
        fields = ["content"]

    def validate(self, attrs):
        if not attrs.get("content", "").strip():
            raise serializers.ValidationError({"content": "This field may not be blank."})
        return attrs

    def create(self, validated_data):
        # 'author' and 'task' should be passed from the view
        return Comment.objects.create(**validated_data)


# ------------------------- #
# Board – general stats serializer
# ------------------------- #
class BoardSerializer(serializers.ModelSerializer):
    """Returns board info with member/task stats."""
    member_count          = serializers.SerializerMethodField()
    ticket_count          = serializers.SerializerMethodField()
    tasks_to_do_count     = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model  = Board
        fields = [
            "id", "title",
            "member_count", "ticket_count",
            "tasks_to_do_count", "tasks_high_prio_count",
            "owner_id",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="todo").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()


# ------------------------- #
# Board – detailed serializer incl. members and tasks
# ------------------------- #
class BoardDetailSerializer(serializers.ModelSerializer):
    """Returns full board info with member and task lists."""
    members = UserMiniSerializer(many=True, read_only=True)
    tasks   = TaskSerializer(many=True, read_only=True)

    class Meta:
        model  = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


# ------------------------- #
# Board – update serializer
# ------------------------- #
class BoardUpdateSerializer(serializers.ModelSerializer):
    """Used for updating board title and member list."""
    members      = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)
    owner_data   = UserMiniSerializer(source="owner",   read_only=True)
    members_data = UserMiniSerializer(source="members", many=True, read_only=True)

    class Meta:
        model  = Board
        fields = ["id", "title", "members", "owner_data", "members_data"]

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        members        = validated_data.pop("members", [])
        instance.save()
        instance.members.set(members)
        return instance
