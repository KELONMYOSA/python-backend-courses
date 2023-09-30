from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"


# Сравнение пароля и хэша
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, str.encode(hashed_password))


# Создание хэшированного пароля
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Создание токена
def create_access_token(email: str) -> str:
    payload = {"sub": email}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
