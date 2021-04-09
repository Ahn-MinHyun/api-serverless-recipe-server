from flask_restful import Resource
from flask import request
from http import HTTPStatus

# 이메일 형식 체크하기 위한 import
from email_validator import validate_email, EmailNotValidError
from mysql.connector import Error

# 패스워드 비밀번호 암호화 및 체크를 위한 import
from utils import hash_passwd, check_passwd
from db.db import get_mysql_connection

# 유저인증을 위한 JWT 라이브러리 import 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

# 로그아웃 기능 구현
from flask_jwt_extended import get_jti
jwt_blocklist = set()

# 회원가입 API
class User_List(Resource):
    def post(self):
        data =request.get_json()

        # 오류 체크
        if "username" not in data or "email" not in data or "password" not in data:
            return {'error_code': 1}, HTTPStatus.BAD_REQUEST

        # 1. 이메일 유효한지 체크
        try:
            # Validate.
            valid = validate_email(data['email'])

        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return {'error_code':3},HTTPStatus.BAD_REQUEST

        # 2. 비밀 번호 암호화
        if len(data["password"]) < 4 or len(data["password"]) > 10:
            return {'error_code': 2}, HTTPStatus.BAD_REQUEST 

        password = hash_passwd(data['password'])
        print(password)

        # 3. 데이터 베이스에 저장
        try:
            connection = get_mysql_connection()
            cursor = connection.cursor()
            query = ''' insert into user(username, email, password)
                        values (%s, %s, %s);'''
            param = (data['username'],data['email'],password)

            cursor.execute(query,param)
            connection.commit()
            # print('------------------확인용 -----------------')
            user_id = cursor.lastrowid
          
            print(user_id)

        except Error as e : 
            print(e)
            return {'error_code': "{}".format(e)}

        finally:
            cursor.close()
            connection.close()

        access_token = create_access_token(identity = user_id)

        return {'token': access_token}, HTTPStatus.OK


class UserResource(Resource):
    # login API
    def post(self):
        data = request.get_json()
        print(data)
        if "email" not in data or "password" not in data:
            return {'error_code': "input your password or email"}, HTTPStatus.BAD_REQUEST

        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary =True)

        try:
            # Validate.
            valid = validate_email(data['email'])

        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return {'error_code':'not valid email'},HTTPStatus.BAD_REQUEST

        query = '''select id, password
                    from user
                    where email = %s;'''

        param = (data['email'],)

        cursor.execute(query, param)
        records = cursor.fetchall()
    
        if records == []:
            return {'error_code':'not exist email'}

        cursor.close()
        connection.close()
        
        # JWT를 이용해서 인증토큰을 생성해 준다. 
        

        password = check_passwd(data['password'],records[0]['password'])
        if password is True:

            user_id = records[0]['id']
            access_token = create_access_token(identity=user_id)

            return {'message': 'access login', 'token': access_token},HTTPStatus.OK
        else:
            return {'message': 'wrong password'},HTTPStatus.BAD_REQUEST

    # 회원정보 API
    @jwt_required()
    def get(self, user_id): 

        # 데이터 베이스에서 유저 아이디의 정보
        # /users/<int:user_id>/my => UserResource Get
        # id,email. username, is_active 이 3개 정보를 클라이언트에 응답
        
        # 토큰에서 유저아이디를 가져온다.
        token_user_id = get_jwt_identity()
        
        if user_id != token_user_id:
            return {'err_code':'Please login your ID'},HTTPStatus.UNAUTHORIZED
        
        # 데이터 베이스 연결
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary = True)
        # 쿼리문
        query = '''select id, email, username, is_active from user 
                where id = %s ;'''
        param =(user_id,)
        # 쿼리문 실행
        cursor.execute(query, param)
        records = cursor.fetchall()

        # 닫기 
        cursor.close()
        connection.close()

        # print(records)
        # 유저 정보 리턴
        if len(records) == 0:
            return {'err_code':1}, HTTPStatus.BAD_REQUEST
        else:
            return {"massage":records[0]},HTTPStatus.OK



# # 유저 확인 비번 입력(request)
#         data = request.get_json()
#         print(data)

#         # 유저 비밀번호 암호화
#         password = hash_passwd(data['password'])
#         # 데이터 베이스에서 유저 아이디의 정보
#         # /users/<int:user_id>/my => UserResource Get
#         # id,email. username, is_active 이 3개 정보를 클라이언트에 응답
#         # 데이터 베이스 연결
#         connection = get_mysql_connection()
#         cursor = connection.cursor(dictionary = True)
#         # 쿼리문
#         query = '''select id, email, username, is_active from user 
#                 where id = %s and password = %s;'''
#         param =(user_id, password)
#         # 쿼리문 실행
#         cursor.execute(query,param)
#         records = cursor.fetchall()

#         # 닫기 
#         cursor.close()
#         connection.close()

#         # 비번 확인

#         # 보여주기 

#         return {records},HTTPStatus.OK

#로그아웃 API 
class UserLogoutResource(Resource):
    @jwt_required()
    def post(self):
        # 로그아웃을 위한 레퍼런스를 따라하는 것
        jti = get_jwt()['jti']
        jwt_blocklist.add(jti)

        return {'message':'logout'},HTTPStatus.OK

