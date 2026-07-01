from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class DareExchange(models.Model):

    user = models.ForeignKey(User, on_delete = models.CASCADE)
    #user = models.ForeignKey(User, on_delete = models.PROTECTED)

    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10)
    deadline = models.DateField(blank = True,null = True)

    dare_image = models.ImageField(upload_to = "dare_images/", blank = True, null = True)

    is_edited = models.BooleanField(default=False)



    dare = models.TextField()



#=======Inheritance=========