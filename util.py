import os
import hashlib
import binascii
import re

# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/


def hash_pass(password):
    """Hash a password for storing."""

    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash)  # return bytes


def verify_pass(provided_password, stored_password):
    """Verify a stored password against one provided by user"""

    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password



def validate_password(password):

    # Define regex patterns for each constraint
    has_lowercase = re.compile(r'[a-z]')
    has_uppercase = re.compile(r'[A-Z]')
    has_digit = re.compile(r'\d')

    # Check each constraint..
    if not has_lowercase.search(password):
        return False, "Password must contain at least one lowercase letter"
    if not has_uppercase.search(password):
        return False, "Password must contain at least one uppercase letter"
    if not has_digit.search(password):
        return False, "Password must contain at least one digit"

    
    # Check length constraint
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # If all constraints are met, return True for validation
    return True, "Password is valid"
