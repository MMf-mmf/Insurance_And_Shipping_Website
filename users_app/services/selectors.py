from payments_app.models import Order, OrderItem 

def get_orders(request):
    orders = Order.objects.filter(user_id=request.user.id, paid=True)
    return orders
