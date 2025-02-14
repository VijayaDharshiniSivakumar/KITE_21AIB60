from django.shortcuts import render, redirect,get_object_or_404
from .models import stock
from django.contrib import messages

def display_data(request):
    data = stock.objects.all()
    total_value = sum(item.value for item in data)
    return render(request, 'display.html', {'data': data, 'total_value': total_value})

def add_data(request):
    if request.method == "POST":
        name = request.POST.get('name')
        value = int(request.POST.get('value'))
        total_value = sum(item.value for item in stock.objects.all()) + value
        threshold = 100
        stock.objects.create(name=name, value=value)
        if total_value > threshold:
            messages.warning(request, "Sell some goods to maintain a balanced trade!")
        return redirect('display_data')
    return render(request, 'add_data.html')

def delete_product(request, product_id):
    product = get_object_or_404(stock, id=product_id)
    product.delete()
    messages.success(request, f"{product.name} has been deleted successfully!")
    return redirect('display_data')