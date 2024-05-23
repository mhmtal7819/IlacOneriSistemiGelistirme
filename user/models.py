from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100, verbose_name='Adı')
    username = models.CharField(max_length=100, unique=True, verbose_name='Kullanıcı Adı')
    surname = models.CharField(max_length=100, verbose_name='Soyadı', unique=False)
    weight = models.FloatField(verbose_name='Kilo')
    height = models.FloatField(verbose_name='Boy')
    age = models.FloatField(verbose_name='Yaş')
    GENDER_CHOICES = (
        ('M', 'Erkek'),
        ('F', 'Kadın'),
        ('O', 'Diğer'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Cinsiyet')

    def __str__(self):
        return f"{self.name}"

class Medication(models.Model):
    name = models.CharField(max_length=100, verbose_name='İlaç Adı')
    active_ingredient = models.CharField(max_length=100, verbose_name='Etken Hastalık')
    allergens = models.CharField(max_length=200, verbose_name='Alerjen Madde')
    kronik_rahatsizlik = models.CharField(max_length=200, verbose_name='Kronik Rahatsızlık')
    arac_kullanimi = models.BooleanField(default=False)
    kullanım_suresi = models.DurationField(verbose_name='Kullanım Süresi')
    kullanım_talimatı = models.CharField(max_length=200, verbose_name='Kullanım Talimatı')

    def __str__(self):
        return self.name

class UserMedication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    date_suggested = models.DateField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.name} - {self.medication.name}"


