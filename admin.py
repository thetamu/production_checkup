from django.contrib import admin
from django.urls import path, include
from .models import Jun, Mid, Sen, Manager, Jobs, User, Detail, PermissionToJob, DoneDetail, Order

admin.site.register(Jun)
admin.site.register(Mid)
admin.site.register(Sen)
admin.site.register(Manager)
admin.site.register(Jobs)
admin.site.register(User)
admin.site.register(Detail)
admin.site.register(DoneDetail)
admin.site.register(PermissionToJob)
admin.site.register(Order)
