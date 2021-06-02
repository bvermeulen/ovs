from django.db import models
from django.contrib.auth.models import User

class Position(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def voted(self):
        return self.votes.all()

    def __str__(self):
        return self.title


class Candidate(models.Model):
    name = models.CharField(max_length=50)
    total_vote = models.IntegerField(default=0, editable=False)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name="Candidate Pic", upload_to='images/')

    def voted(self):
        return self.votes.all()

    def __str__(self):
        return f'{self.name} - {self.position.title}'


class ControlVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name='votes', null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='votes')
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} - {self.position} - {self.status}'
