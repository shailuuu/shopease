def cart_count(request):
    if request.user.is_authenticated:
        try: return {'cart_count': sum(item.quantity for item in request.user.cart.items.all())}
        except Exception: pass
    return {'cart_count': 0}
