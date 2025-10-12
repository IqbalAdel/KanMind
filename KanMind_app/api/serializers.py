from rest_framework import serializers
from KanMind_app.models import Board, User, Task, Comment

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']


class TaskSerializer(serializers.ModelSerializer):
    assignee = MemberSerializer(read_only=True, required=False, allow_null=True)
    reviewer = MemberSerializer(read_only=True, required=False, allow_null=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True
    )
    comments_count = serializers.SerializerMethodField()

    def get_comments_count(self, obj):
        return obj.comments.count()
    class Meta: 
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority','assignee_id','reviewer_id', 'assignee', 'reviewer', 'due_date', 'comments_count']

    def validate(self, attrs):
        board = attrs.get('board')
        user = self.context['request'].user

        # Creator must be owner or member
        if user != board.user and user not in board.members.all():
            raise serializers.ValidationError("You must be a member or owner of the board to create a task.")

        # Only validate assignee/reviewer if provided
        assignee = attrs.get('assignee')
        if assignee and assignee != board.user and assignee not in board.members.all():
            raise serializers.ValidationError("Assignee must be a member of the board.")

        reviewer = attrs.get('reviewer')
        if reviewer and reviewer != board.user and reviewer not in board.members.all():
            raise serializers.ValidationError("Reviewer must be a member of the board.")

        return attrs

class TaskDetailSerializer(TaskSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(read_only = True)
    reviewer_id = serializers.PrimaryKeyRelatedField(read_only = True)

    class Meta: 
        model = Task
        fields = ['title', 'description', 'status', 'priority','assignee_id', 'reviewer_id','due_date']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id','created_at', 'author' ,'content']


class BoardSerializer(serializers.ModelSerializer):
    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many = True,
        write_only = True,
        source = 'members'
    )

    member_count = serializers.SerializerMethodField()
    owner_id = serializers.PrimaryKeyRelatedField(
        source='user',  
        read_only=True
    )
    tasks_high_prio_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'member_ids', 'member_count', "ticket_count", "tasks_to_do_count", "tasks_high_prio_count", 'owner_id']

    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(priority__iexact='to-do').count()
    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority__iexact='high').count()


class BoardDetailSerializer(BoardSerializer):
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'user', 'members', 'tasks']