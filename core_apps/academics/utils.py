import secrets
from os import getenv
from typing import Union, List
from django.db import transaction
from .emails import send_account_creation_email

from .models import Teacher

def generate_teacher_empId():
    """Generate a unique employee ID for a teacher"""
    school_code = getenv("SCHOOL_CODE")
    school_location = getenv("SCHOOL_LOCATION_CODE")

    prefix = f"{school_code}{school_location}"

    remaining_length = 12 - len(prefix) - 1

    random_digits = "".join(
        secrets.choice("0123456789") for _ in range(remaining_length)
    )

    partial_empId = f"{prefix}{random_digits}"

    check_digit = calculate_luhn_check_digit(partial_empId)
    return f"{partial_empId}{check_digit}"

def calculate_luhn_check_digit(number: str) -> int:
    def split_into_digits(n: Union[str, int]) -> List[int]:
        return [int(digit) for digit in str(n)]
    
    digits = split_into_digits(number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)

    for d in even_digits:
        doubled = d * 2
        total += sum(split_into_digits(doubled))

    return (10 - (total % 10)) % 10