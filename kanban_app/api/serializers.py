# kanban_app/api/serializers.py
from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from auth_app.models import CustomUser


# ------------------------------------------------------------------ #
#  Mini‐Darstellung User
# ------------------------------------------------------------------ #
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = ["id", "email", "fullname"]


# ------------------------------------------------------------------ #
#  Task – Read-Serializer
# ------------------------------------------------------------------ #
class TaskSerializer(serializers.ModelSerializer):
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


# ------------------------------------------------------------------ #
#  Task – Create-Serializer  (POST /api/tasks/)
# ------------------------------------------------------------------ #
class TaskCreateSerializer(serializers.ModelSerializer):
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

        if user != board.owner and user not in board.members.all():
            raise serializers.ValidationError("You are not a member of this board.")

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


# ------------------------------------------------------------------ #
#  Task – Update-Serializer  (PATCH /api/tasks/<id>/)
# ------------------------------------------------------------------ #
class TaskUpdateSerializer(serializers.ModelSerializer):
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
        for field in ("title", "description", "status", "priority", "due_date"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        if "assignee_id" in validated_data:
            instance.assignee = CustomUser.objects.filter(pk=validated_data["assignee_id"]).first()
        if "reviewer_id" in validated_data:
            instance.reviewer = CustomUser.objects.filter(pk=validated_data["reviewer_id"]).first()

        instance.save()
        return instance


# ------------------------------------------------------------------ #
#  Comment – Read-Serializer
# ------------------------------------------------------------------ #
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model  = Comment
        fields = ["id", "created_at", "author", "content"]


# ------------------------------------------------------------------ #
#  Comment – Create-Serializer
# ------------------------------------------------------------------ #
class CommentCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField()

    class Meta:
        model  = Comment
        fields = ["content"]

    def validate(self, attrs):
        if not attrs.get("content", "").strip():
            raise serializers.ValidationError({"content": "This field may not be blank."})
        return attrs

    def create(self, validated_data):
        # Wir bekommen 'author' und 'task' über serializer.save(author=..., task=...)
        # im View als Teil von validated_data rein, daher können wir sie direkt verwenden.
        return Comment.objects.create(**validated_data)


# ------------------------------------------------------------------ #
#  Board – Listen / Create / Update / Detail
# ------------------------------------------------------------------ #
class BoardSerializer(serializers.ModelSerializer):
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


class BoardDetailSerializer(serializers.ModelSerializer):
    members = UserMiniSerializer(many=True, read_only=True)
    tasks   = TaskSerializer(many=True, read_only=True)

    class Meta:
        model  = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
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
