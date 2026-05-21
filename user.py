from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    username: str
    email: str
    password_hash: str
    profile_pic: str = ""

    def get_user_id(self) -> int:
        return self.user_id

    def get_username(self) -> str:
        return self.username

    def get_email(self) -> str:
        return self.email

    def get_password_hash(self) -> str:
        return self.password_hash

    def get_profile_pic(self) -> str:
        return self.profile_pic
