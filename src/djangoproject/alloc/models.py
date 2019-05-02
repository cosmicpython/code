from django.db import models
from allocation.domain import model as domain_model


class Batch(models.Model):
    reference = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    qty = models.IntegerField()
    eta = models.DateField(blank=True, null=True)

    @classmethod
    def from_domain(self, batch: domain_model.Batch):
        try:
            b = Batch.objects.get(reference=batch.reference)
        except Batch.DoesNotExist:
            b = Batch(reference=batch.reference)
        b.sku = batch.sku
        b.qty = batch._purchased_quantity
        b.eta = batch.eta
        return b

    def to_domain(self):
        return domain_model.Batch(ref=self.reference, sku=self.sku, qty=self.qty)


class OrderLine(models.Model):
    orderid = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    qty = models.IntegerField()


class Allocation(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    line = models.ForeignKey(OrderLine, on_delete=models.CASCADE)
