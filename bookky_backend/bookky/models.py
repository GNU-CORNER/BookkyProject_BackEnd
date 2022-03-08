from django.db import models

class User(models.Model): 
    '''DB column'''
    UID                     = models.BigAutoField(primary_key=True)
    #PID                     = models.ManyToManyField('Product')
    pwToekn                 = models.CharField(max_length=255, null=False)
    email                   = models.EmailField(max_length=100, null=False)
    name                    = models.CharField(max_length=50, null=False)
    address                 = models.CharField(max_length=100, null=False)
    phone                   = models.CharField(max_length=20, null=False)
    nickname                = models.CharField(max_length=10, null=False, default="ABC")
    pushToken               = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.nickname