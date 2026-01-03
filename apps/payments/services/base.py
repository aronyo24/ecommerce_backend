from abc import ABC, abstractmethod

class PaymentProvider(ABC):
    @abstractmethod
    def create_payment_intent(self, amount, currency='usd', metadata=None):
        pass
    
    @abstractmethod
    def confirm_payment(self, payment_intent_id):
        pass
