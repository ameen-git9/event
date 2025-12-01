

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    staff_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    boy_id = models.CharField(max_length=20, unique=True, null=True, blank=True)

    is_staff_user = models.BooleanField(default=False)
    is_boy_user = models.BooleanField(default=False)

    # For catering boys - first time login
    first_time_login = models.BooleanField(default=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    upi_id = models.CharField(max_length=50, blank=True, null=True)










class Event(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    total_seats = models.PositiveIntegerField()
    payment_per_boy = models.PositiveIntegerField()

    event_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'is_staff_user': True}
    )

    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="event_images/", null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def available_seats(self):
        taken = Registration.objects.filter(event=self).count()
        return self.total_seats - taken


class Registration(models.Model):
    boy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_boy_user': True}
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField()
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.boy.username} - {self.event.title}"


class Payment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    )

    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_id = models.CharField(max_length=200, blank=True, null=True)  # Razorpay order/payment id
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.registration.boy.username} - {self.registration.event.title}"
