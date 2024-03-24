from django.db import models
from accounts.models import Account
# Create your models here.
class Post(models.Model):
    caption = models.CharField(max_length=250, null=True)
    thinking=models.TextField(max_length=250, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    mypost=models.FileField(upload_to='myposts', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.caption}"


class Like(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    liked_by=models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Liked by {self.liked_by.first_name}"

class Comment(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    commentor=models.ForeignKey(Account, on_delete=models.CASCADE)
    comment=models.TextField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True, null=True)
    updated_at=models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Commented By: {self.commentor.first_name}"

class Notification(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    like=models.ForeignKey(Like, on_delete=models.CASCADE, null=True)
    comment=models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    sender=models.ForeignKey(Account, on_delete=models.CASCADE)
    receiver=models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='not_rec')
    created_at=models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Send By: {self.sender.first_name}"