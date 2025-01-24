# Standard library imports for random number generation and string operations
import random
import string

def generate_otp(length=6) -> str:
    """
    Generate a random numeric One-Time Password (OTP).
    
    Args:
        length (int, optional): The length of the OTP to generate. Defaults to 6 digits.
    
    Returns:
        str: A string containing random digits of specified length.
        
    Example:
        >>> generate_otp()
        '123456'
        >>> generate_otp(length=4)
        '1234'
    """
    return "".join(random.choices(string.digits, k=length))