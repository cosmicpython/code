# pylint: disable=too-few-public-methods, protected-access
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict

from allocation.domain import model
from allocation.adapters import repository
from allocation.service_layer import unit_of_work


class CsvRepository(repository.AbstractRepository):
    def __init__(self, folder):
        self._batches_path = Path(folder) / "batches.csv"
        self._allocations_path = Path(folder) / "allocations.csv"
        self._batches = {}  # type: Dict[str, model.Batch]
        self._load()

    def get(self, reference):
        return self._batches.get(reference)

    def add(self, batch):
        self._batches[batch.reference] = batch

    def _load(self):
        with self._batches_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                ref, sku = row["ref"], row["sku"]
                qty = int(row["qty"])
                if row["eta"]:
                    eta = datetime.strptime(row["eta"], "%Y-%m-%d").date()
                else:
                    eta = None
                self._batches[ref] = model.Batch(ref=ref, sku=sku, qty=qty, eta=eta)
        if self._allocations_path.exists() is False:
            return
        with self._allocations_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                batchref, orderid, sku = row["batchref"], row["orderid"], row["sku"]
                qty = int(row["qty"])
                line = model.OrderLine(orderid, sku, qty)
                batch = self._batches[batchref]
                batch._allocations.add(line)

    def list(self):
        return list(self._batches.values())


class CsvUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self, folder):
        self.batches = CsvRepository(folder)

    def commit(self):
        with self.batches._allocations_path.open("w") as f:
            writer = csv.writer(f)
            writer.writerow(["orderid", "sku", "qty", "batchref"])
            for batch in self.batches.list():
                for line in batch._allocations:
                    writer.writerow(
                        [line.orderid, line.sku, line.qty, batch.reference]
                    )

    def rollback(self):
        pass
