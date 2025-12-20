from .models import Order, Transaction
from django.db import transaction as db_transaction
from core.models import UserBalance

def match_orders():
    """
    Простой matching engine: ищет совпадающие BUY и SELL заявки по цене.
    Обновляет балансы пользователей при исполнении сделки.
    """
    buy_orders = Order.objects.filter(order_type='BUY', status='PENDING').order_by('-price', 'created_at')
    sell_orders = Order.objects.filter(order_type='SELL', status='PENDING').order_by('price', 'created_at')

    for buy in buy_orders:
        for sell in sell_orders:
            if buy.skin == sell.skin and buy.price >= sell.price:
                # Исполняем сделку
                with db_transaction.atomic():
                    quantity = min(buy.quantity, sell.quantity)
                    total_price = sell.price * quantity

                    # Создаём транзакцию
                    Transaction.objects.create(
                        buyer=buy.user,
                        seller=sell.user,
                        skin=buy.skin,
                        price=sell.price,
                        quantity=quantity
                    )

                    # Обновляем балансы
                    try:
                        # Получаем или создаем балансы пользователей
                        buyer_balance, _ = UserBalance.objects.get_or_create(user=buy.user)
                        seller_balance, _ = UserBalance.objects.get_or_create(user=sell.user)
                        
                        # Проверяем, достаточно ли средств у покупателя
                        if buyer_balance.amount >= total_price:
                            # Списание с покупателя
                            buyer_balance.amount -= total_price
                            buyer_balance.save()
                            
                            # Зачисление продавцу
                            seller_balance.amount += total_price
                            seller_balance.save()
                            
                            print(f"Балансы обновлены: покупатель -{total_price}, продавец +{total_price}")
                        else:
                            print(f"Недостаточно средств у покупателя {buy.user.username}: {buyer_balance.amount} < {total_price}")
                            continue  # Пропускаем эту сделку
                    except UserBalance.DoesNotExist:
                        print("Ошибка: балансы пользователей не найдены")
                        continue

                    # Обновляем количества заявок
                    buy.quantity -= quantity
                    sell.quantity -= quantity

                    if buy.quantity == 0:
                        buy.status = 'EXECUTED'
                    if sell.quantity == 0:
                        sell.status = 'EXECUTED'

                    buy.save()
                    sell.save()

                # Если заявки исполнены, удаляем их из списка
                if buy.quantity == 0:
                    break
        if buy.quantity == 0:
            continue