from rest_framework import serializers
from KanMind_app.models import Board, User, Task, Comment

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']


class TaskSerializer(serializers.ModelSerializer):
    assignee = MemberSerializer(read_only=True)
    reviewer = MemberSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    

    def get_comments_count(self, obj):
        return obj.comments.count()
    class Meta: 
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']


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