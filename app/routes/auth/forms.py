from dataclasses import dataclass

@dataclass
class LoginForm:
    email: str
    password: str

@dataclass
class RegisterForm:
    username: str
    email: str
    password: str
    confirm: str
