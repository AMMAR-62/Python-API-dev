from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# creating the hash of passwor, which can be retrieved from the user.password.
def hash(pwd : str):
    return pwd_context.hash(pwd)

def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)