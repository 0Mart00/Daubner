from django.db import models

class Order(models.Model):
    class OrderType(models.TextChoices):
        TAKEAWAY = 'elvitel', 'Elvitel'
        EAT_IN = 'helyben fogyasztas', 'Helyben fogyasztás'

    termek = models.CharField(max_length=100, null=True, blank=True)
    mennyiseg = models.IntegerField(null=True, blank=True)
    meret = models.CharField(max_length=50, null=True, blank=True)
    atvetel_datuma = models.DateField(null=True, blank=True)
    atvetel_idoppontja = models.TimeField(null=True, blank=True)
    nev = models.CharField(max_length=100, null=True, blank=True)
    telefonszam = models.CharField(max_length=50, null=True, blank=True)
    tipus = models.CharField(max_length=20, choices=OrderType.choices, null=True, blank=True)
    megjegyzes = models.TextField(null=True, blank=True)
    letrehozva = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rendelés: {self.termek or 'Ismeretlen'} - {self.nev or 'Ismeretlen'}"