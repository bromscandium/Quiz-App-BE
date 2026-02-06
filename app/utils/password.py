from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash


class PasswordUtil:
    def __init__(self):
        self.ph = PasswordHasher(
            time_cost=2, memory_cost=32768, parallelism=2, hash_len=32, salt_len=16
        )

    def hash_password(self, password: str) -> str:
        return self.ph.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        try:
            return self.ph.verify(hashed_password, password)
        except (VerifyMismatchError, VerificationError, InvalidHash):
            return False
