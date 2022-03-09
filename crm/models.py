from enum import unique
from django.db import models

class Developers(models.Model):
    dev = models.CharField("Разработчик", max_length=255)

class Folders(models.Model):
    folder_name = models.CharField("Название папки", max_length=255, unique=True)

class Admobs(models.Model):
    admob_name = models.CharField("Название AdMob", max_length=255, unique=True)
    admob_secret_file = models.JSONField("Секретный файл AdMob", max_length=255, unique=True)
    publisher_id = models.CharField("Секретный файл AdMob", max_length=100, unique=True, null=True)

class Apps(models.Model):
    app_id = models.CharField("ID приложения", max_length=255, unique=True)
    add_time = models.DateTimeField("Время добавления")
    folder = models.ForeignKey(Folders, on_delete = models.CASCADE, default=None)
    
    app_name = models.CharField("Название приложения", max_length=255, default="Не существует")
    last_update = models.CharField("Последнее обновление", max_length=255, default="Не существует")
    installs = models.IntegerField("Всего установок", default=0)
    status = models.BooleanField("Статус", default=False)
    admob = models.ForeignKey(Admobs, on_delete = models.CASCADE, null=True, default=None)

class History(models.Model):
    date_time = models.DateTimeField("Дата/время")
    installs = models.IntegerField("Установки")
    app = models.ForeignKey(Apps, on_delete = models.CASCADE)