from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    def get_absolute_url(self):
        return reverse('profile', args=[str(self.id)])


class Sen(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{User.objects.get(username=self.user.username).last_name} ' \
               f'{User.objects.get(username=self.user.username).first_name}'


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sen = models.ForeignKey(Sen, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)

    def __str__(self):
        return f'{User.objects.get(username=self.user.username).last_name} ' \
               f'{User.objects.get(username=self.user.username).first_name}'


class Mid(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sen = models.ForeignKey(Sen, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)

    def __str__(self):
        return f'{User.objects.get(username=self.user.username).last_name} ' \
               f'{User.objects.get(username=self.user.username).first_name}'


class Jun(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mid = models.ForeignKey(Mid, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)

    def __str__(self):
        return f'{User.objects.get(username=self.user.username).last_name} ' \
               f'{User.objects.get(username=self.user.username).first_name}'


class PermissionToJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jobs = models.ForeignKey('Jobs', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} {self.user.last_name} <----> {self.jobs.job_type}'


class Jobs(models.Model):
    job_type = models.CharField(max_length=30, blank=False, unique=True)
    job_reward = models.FloatField(default=0)

    def __str__(self):
        return f'{self.job_type}'


class Detail(models.Model):
    time_when_created = models.DateTimeField(auto_now_add=True)
    time_when_done = models.DateTimeField(auto_now=True)
    is_done = models.BooleanField(default=False)
    order_num = models.CharField(max_length=20, blank=False)
    name = models.CharField(max_length=200, blank=False)
    numbers = models.IntegerField(blank=False)
    numbers_in_order = models.IntegerField(blank=False)
    price = models.FloatField(blank=False)
    jobs = models.ForeignKey(Jobs, on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, default=0)

    def __str__(self):
        return f'{self.order_num} {self.name}'


class DoneDetail(models.Model):
    time_when_done = models.DateTimeField(auto_now_add=True)
    order_num = models.CharField(max_length=20, blank=False)
    name = models.CharField(max_length=200, blank=False)
    numbers = models.IntegerField(blank=False)
    price = models.FloatField(blank=False)
    reward = models.FloatField(blank=False, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jobs = models.ForeignKey(Jobs, on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.order_num} {self.name}'


class Order(models.Model):
    time_when_created = models.DateTimeField(auto_now_add=True)
    time_when_done = models.DateTimeField(auto_now=True)
    order_num = models.CharField(max_length=20, blank=False)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.order_num}'

