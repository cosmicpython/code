from __future__ import annotations
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class Line:
    sku: str
    qty: int


class _Lines:

    def __init__(self, lines: dict):
        self.lines = [Line(sku, qty) for sku, qty in lines.items()]



class Order(_Lines):
    pass


class Warehouse(_Lines):
    pass

