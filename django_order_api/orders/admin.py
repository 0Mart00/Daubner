from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('nev', 'termek', 'mennyiseg', 'tipus', 'atvetel_datuma', 'letrehozva')
    list_filter = ('tipus', 'atvetel_datuma')
    search_fields = ('nev', 'termek', 'telefonszam')
