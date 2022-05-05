from django.db import models


class Tag(models.Model):
    title = models.CharField(max_length=30, help_text="tag's name")
    url = models.CharField(max_length=30, help_text='tag url')

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100, help_text='Title of post')
    date = models.DateTimeField(auto_now_add=True, help_text='Date of post')
    post_text = models.TextField(help_text='Post text')
    tag = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.CharField(max_length=100, help_text='Author of comment')
    date = models.DateTimeField(auto_now_add=True, help_text='Date of comment')
    comment_text = models.TextField(help_text='Comment text')
    email = models.CharField(max_length=100, help_text="Author's email")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment_text
