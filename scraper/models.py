from django.db import models

class App(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    installs = models.IntegerField()
    size = models.IntegerField()
    updated_at = models.DateField(null=True, blank=True)
    image_urls = models.JSONField(default=list)

    def __str__(self):
        return self.name


class User(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return self.display_name


class Comment(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    rating = models.IntegerField()
    comment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.display_name} ({self.app.name})"