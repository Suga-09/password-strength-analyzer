import re

def validate_password_input(password):
    """
    Validate password input for security
    """
    if not isinstance(password, str):
        return False
    
    if len(password) > 100:  # Prevent extremely long inputs
        return False
    
    # Check for invalid characters (prevent injection attacks)
    if re.search(r'[<>"\']', password):
        return False
    
    return True

def sanitize_input(input_string):
    """
    Sanitize input to prevent XSS
    """
    # Remove potential dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    for char in dangerous_chars:
        input_string = input_string.replace(char, '')
    return input_string

def validate_strength_threshold(threshold):
    """
    Validate strength threshold input
    """
    try:
        threshold = int(threshold)
        return 0 <= threshold <= 100
    except (ValueError, TypeError):
        return False

def validate_password_length(length):
    """
    Validate password length for generation
    """
    try:
        length = int(length)
        return 8 <= length <= 64
    except (ValueError, TypeError):
        return False
    