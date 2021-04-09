from config.config import salt
from passlib.hash import pbkdf2_sha256

# 회원가입
# 유저가 입력한 비밀번호를 암호화 해주는 함수
def hash_passwd(password):
    return pbkdf2_sha256.hash(password + salt)

# 로그인시
# 유저가 입력한 비밀번호와 DB에 저장된 비밀번호가 같은지 확인해 주는 함수
def check_passwd(password, hashed_password) :
    return pbkdf2_sha256.verify(password + salt, hashed_password)

