

#MySQL접속 정보를 딕셔너리 형태로 저장한다.
db_config={ 'host' : 'database-2.cumcickeiqsl.ap-northeast-2.rds.amazonaws.com',
            'database' :'yhdb',
            'user' : 'streamlit',
            'password' :'yh1234'}

# 클래스란 속성과 함수로 구성된것

# 클래스를 만드는 이유?

class Config :
    DEBUG =True
    PORT = 5002
    
    # JWT 암호화를 위한 변수 설정
    SECRET_KEY = 'super-secret-key'

# 비밀번호 암호화를 위한 변수 설정 => 해킹 방지
salt = 'hello_test'

