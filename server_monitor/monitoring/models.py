from django.db import models

class WebsiteUptime(models.Model):
    timestamp = models.DateTimeField()
    twitter = models.FloatField(default=100.0)
    amazon = models.FloatField(default=100.0)
    apple = models.FloatField(default=100.0)
    facebook = models.FloatField(default=100.0)
    friendster = models.FloatField(default=100.0)  # ✅ Fixed default value
    geocities = models.FloatField(default=100.0)
    google = models.FloatField(default=100.0)
    microsoft = models.FloatField(default=100.0)
    myspace = models.FloatField(default=100.0)
    netflix = models.FloatField(default=100.0)
    reddit = models.FloatField(default=100.0)
    wikipedia = models.FloatField(default=100.0)
    youtube = models.FloatField(default=100.0)



    def __str__(self):
        return f"Uptime Data for {self.timestamp}"
#from django.db import models

class HourlyWebsiteUptime(models.Model):
    timestamp = models.DateTimeField(unique=True)
    twitter = models.FloatField(default=100.0, blank=True, null=True)
    amazon = models.FloatField(default=100.0, blank=True, null=True)
    apple = models.FloatField(default=100.0, blank=True, null=True)
    facebook = models.FloatField(default=100.0, blank=True, null=True)
    friendster = models.FloatField(default=100.0, blank=True, null=True)
    geocities = models.FloatField(default=100.0, blank=True, null=True)
    google = models.FloatField(default=100.0, blank=True, null=True)
    microsoft = models.FloatField(default=100.0, blank=True, null=True)
    myspace = models.FloatField(default=100.0, blank=True, null=True)
    netflix = models.FloatField(default=100.0, blank=True, null=True)
    reddit = models.FloatField(default=100.0, blank=True, null=True)
    wikipedia = models.FloatField(default=100.0, blank=True, null=True)
    youtube = models.FloatField(default=100.0, blank=True, null=True)

    def __str__(self):
        return f"Hourly Uptime for {self.timestamp}"


class DailyWebsiteUptime(models.Model):
    timestamp = models.DateTimeField(unique=True)
    twitter = models.FloatField(default=100.0, blank=True, null=True)
    amazon = models.FloatField(default=100.0, blank=True, null=True)
    apple = models.FloatField(default=100.0, blank=True, null=True)
    facebook = models.FloatField(default=100.0, blank=True, null=True)
    friendster = models.FloatField(default=100.0, blank=True, null=True)
    geocities = models.FloatField(default=100.0, blank=True, null=True)
    google = models.FloatField(default=100.0, blank=True, null=True)
    microsoft = models.FloatField(default=100.0, blank=True, null=True)
    myspace = models.FloatField(default=100.0, blank=True, null=True)
    netflix = models.FloatField(default=100.0, blank=True, null=True)
    reddit = models.FloatField(default=100.0, blank=True, null=True)
    wikipedia = models.FloatField(default=100.0, blank=True, null=True)
    youtube = models.FloatField(default=100.0, blank=True, null=True)

    def __str__(self):
        return f"Daily Uptime for {self.timestamp}"


