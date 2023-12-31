from dataclasses import dataclass
from typing import NamedTuple
import pytest

from model import Batch


@dataclass
class Name:
    first_name: str
    surname: str


class Money(NamedTuple):
    currency: str
    value: int


fiver = Money('gbp', 5)
tenner = Money('gbp', 10)


# def can_add_money_values_for_the_same_currency():
#     assert fiver + fiver == tenner


# def can_subtract_money_values():
#     assert tenner - fiver == fiver


# def adding_different_currencies_fails():
#     with pytest.raises(ValueError):
#         Money('usd', 10) + Money('gbp', 10)


# def can_multiply_money_by_a_number():
#     assert fiver * 5 == Money('gbp', 25)


# def multiplying_two_money_values_is_an_error():
#     with pytest.raises(TypeError):
#         tenner * fiver


class Person:
    def __init__(self, name: Name) -> None:
        self.name = name
