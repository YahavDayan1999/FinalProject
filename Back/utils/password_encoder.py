import hashlib

class PasswordEncoder:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes the password using SHA-512 and returns the hex digest."""
        return hashlib.sha512(password.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a password by comparing the hashed value of the input to the stored hash."""
        return PasswordEncoder.hash_password(plain_password) == hashed_password
