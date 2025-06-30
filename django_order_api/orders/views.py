from rest_framework import generics
from .models import Order
from .serializers import OrderSerializer

class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by('-letrehozva')
    serializer_class = OrderSerializer