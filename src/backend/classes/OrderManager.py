import random

class OrderManager():
    def __init__(self):
        self._orders = []

    def get_next_id(self):
        try:
            current_order = self._orders[-1]['id']
            return current_order + 1
        except IndexError:
            return 1

    def create(self):
        order = {
            'amount': '{0}.00'.format(random.randrange(10, 200)),
            'currency': random.choice(['CAD', 'USD', 'EUR']),
            'id': self.get_next_id(),
            'paid': False,
        }

        self._orders.append(order)

        return order

    def get_by_id(self, order_id):
        for order in self._orders:
            if str(order['id']) == str(order_id):
                return order
        else:
            raise Exception('Order id "{0}" not found'.format(order_id))

