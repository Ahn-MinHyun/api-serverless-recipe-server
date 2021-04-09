from flask_restful import Resource
from flask import request
from http import HTTPStatus

from db.db import get_mysql_connection

## 토큰 사용하기 위한 import
from flask_jwt_extended import jwt_required, get_jwt_identity

'''
이 파일에서 작성하는 클래스는
플라스크 프레임워크에서, 경로랑 연결시킬 클래스
따라서, 클래서 명 뒤에 리소스 클래스를 상속받아야 한다.
플라스크 레퍼런스에 나옴
'''

class RecipeListResource(Resource) :
    # get 메소드로 연결시킬 함수 작성
    # 모든 레시피 정보를 가져온다.
    def get(self):        
        # 1. DB커넥션 가져오기 
        connection = get_mysql_connection()
        print('커넥트 성공')
        # 2. 커서 
        cursor = connection.cursor(dictionary =True)
        print('커서연결')
        # 3. 쿼리문
        query =""" select * from recipe; """
        # 4. sql 실행
        cursor.execute(query)

        # 5. 데이터를 페치한다.
        records = cursor.fetchall()

        print(records)


        ret = []
        for row in records :
            row['created_at'] = row['created_at'].isoformat()
            row['updated_at'] = row['updated_at'].isoformat()
            ret.append(row)

        # 6. 커서와 커넥션을 닫아 준다.
        cursor.close()
        connection.close()
        

        # 7. 클라이언트에 리스판스 한다.
        return {'test':'hello','count':len(ret), 'ret':ret}, HTTPStatus.OK

    # 레시피 생성 
    @jwt_required()
    def post(self):
        # 1. 클라이언트가 요청한 reuest의 바디에 있는 json데이터 가져오기
        data = request.get_json()
        # print(data)
        # 2. 필수항목 있는지 체크
        key = ['name', 'description', 'num_of_servings', 'cook_time', 'directions', 'is_publish']
        for i in key: 
            if i not in data : #예외 처리를 잘해야 꼼꼼한 코딩이다.
                return{'message' : ' {} input right message'.format(i)}, HTTPStatus.BAD_REQUEST 
        
        

        ## JWT 인증토큰에서 유저아이디를 뽑아낸다.
        user_id = get_jwt_identity()
        print('------------------------------------')
        print(user_id)

        # 3. 데이터 베이스 커넥션 연결
        connection = get_mysql_connection()
        # 4. 커서 가져오기
        cursor = connection.cursor(dictionary=True)
        # 5. 쿼리문 만들기
        query =""" insert into recipe(name, description, num_of_servings, cook_time, directions, is_publish, user_id)
                    values(%s,%s,%s,%s,%s,%s,%s);   """

        param = [data["name"],data['description'],data['num_of_servings'],data['cook_time'],data['directions'],data['is_publish'],user_id]
        
        # 6. 쿼리문 실행
        cursor.execute(query, param)
        connection.commit()
        # 7. 커서와 커넥션 닫기
        cursor.close()
        connection.close()
        # 8. 클라이언트에 리스판스
        return {'message':0}, HTTPStatus.OK

class RecipeResource(Resource):
    def get(self, recipe_id):
        # 1. 경로의 붙어있는 값을 가져와야한다.(레시피 아이디)
        # 위의 get 함수에 변수로 받아온다. 
        
        # 2. 디비 커넥션을 가져온다.
        connection = get_mysql_connection()
        # 3. 커서 가져온다 
        cursor = connection.cursor(dictionary= True)
        # 4. 쿼리문 만든다. 
        query = '''select *
                    from recipe
                    where id = %s; '''
        param = (recipe_id,)
        # 5. 쿼리 실행
        cursor.execute(query, param)

        records = cursor.fetchall()
        # 6. 자원해제 
        cursor.close()
        connection.close()
        # 7. 클라이언트에게 리스판스

        if len(records) == 0:
            return {'message': 'not exite'}, HTTPStatus.Error


        ret=[]
        for row in records:
            row['created_at'] = row['created_at'].isoformat()
            row['updated_at'] = row['updated_at'].isoformat()
            ret.append(row)

        return {'count':len(ret), 'ret':ret[0]}, HTTPStatus.OK

    #요리시간과 디렉션 업데이트
    @jwt_required()
    def put(self, recipe_id):
        data = request.get_json()
        print(data)

        if 'cook_time' not in data or 'directions' not in data:
            return {"err_code":"wrong parameter"},HTTPStatus.BAD_REQUEST

        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary= True)

        ## 유저 아이디가 이 레시피 만든 유저가 맞는지 확인해 봐야한다.
        user_id=get_jwt_identity() #헤더의 인증토큰을 가져온다.

        query = ''' select user_id from recipe 
                    where id = %s;'''

        param = (recipe_id,)

        cursor.execute(query, param)
        records = cursor.fetchall()
        if len(records) == 0:
            return {'err_code': "Not exist recipe."},HTTPStatus.BAD_REQUEST

        if user_id != records[0]['user_id']:
            return {'err_code':'바꿀 수 있는 권한이 없다.'},HTTPStatus.NOT_ACCEPTABLE 

        # 업데이트 쿼리
        query = '''update recipe 
                    set cook_time = %s, directions = %s
                    where id = %s;'''

        param = (data['cook_time'],data['directions'],recipe_id)
        cursor.execute(query,param)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return {"message":"success"}, HTTPStatus.OK
    
    #삭제하는 API    
    @jwt_required()
    def delete(self, recipe_id):
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary= True)


        ## 유저 아이디가 이 레시피 만든 유저가 맞는지 확인해 봐야한다.
        user_id=get_jwt_identity() #헤더의 인증토큰을 가져온다.

        query = ''' select user_id from recipe 
                    where id = %s;'''

        param = (recipe_id,)

        cursor.execute(query, param)
        records = cursor.fetchall()
        
        if len(records) == 0:
            return {'err_code': "Not exist recipe."},HTTPStatus.BAD_REQUEST

        if user_id != records[0]['user_id']:
            return {'err_code':'지울 수 있는 권한이 없다.'},HTTPStatus.NOT_ACCEPTABLE 

        query = '''delete from recipe
                    where id = %s;'''
        param = (recipe_id,)
        cursor.execute(query, param) 
        connection.commit()

        cursor.close()
        connection.close()

        return {'message':'success remove'}, HTTPStatus.OK       

        
class RecipePublishResource(Resource):

    # is_publish를 1로 변경
    def put(self, recipe_id):
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary= True)
        query = '''update recipe 
                    set is_publish = 1
                    where id = %s;'''

        param = (recipe_id, )
        cursor.execute(query,param)
        connection.commit()
        
        cursor.close()
        connection.close()

        return {}, HTTPStatus.OK
    
    # is_publish를 0으로 변경
    def delete(self, recipe_id):
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary= True)
        query = '''update recipe 
                    set is_publish = 0
                    where id = %s;'''
        param = (recipe_id,)
        cursor.execute(query, param) 
        connection.commit()

        cursor.close()
        connection.close()
        
        return {}, HTTPStatus.OK


# 실습. 레시피 삭제 API에 , 인증 토큰 적용해서 
# 레세피를 작성한 유저만, 레시피를 삭제할 수 있게 변경