from django.db import models
from django.contrib.auth.models import User




class Board(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name="members")
    

    def __str__(self):
        return self.title
    
 


class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    status = models.CharField(max_length=100)
    priority = models.CharField(max_length=100)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="assigned_tasks",null=True, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL , related_name="reviewed", null=True, blank=True)
    due_date = models.DateField()


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name = 'comments')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="author_comments",null=True, blank=True)
    content = models.TextField(blank=True, null=True)
    

