from flask import Flask
from flask_restful import Api
from db.db import get_mysql_connection
from config.config import Config
from resources.Racipe import RecipeListResource, RecipeResource, RecipePublishResource
from resources.user import User_List, UserResource, jwt_blocklist, UserLogoutResource

##JWT용 라이브러리
from flask_jwt_extended import JWTManager

import mysql.connector 



app = Flask(__name__)


get_mysql_connection()
# 1. 환경변수 설정
app.config.from_object(Config)
## 1-1. JWT 환경 설정
jwt = JWTManager(app) 

## 로그인/로그아웃 관리를 위한 jwt설정
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blocklist


# 2. API설정
api = Api(app)

# 3. 경로(Path)랑 리소스(resource)를 연결한다. 
# /recipe
api.add_resource(RecipeListResource,'/recipes')
api.add_resource(RecipeResource,'/recipes/<int:recipe_id>') #경로의 변수 처리 
api.add_resource(RecipePublishResource,'/recipes/<int:recipe_id>/publish') #경로의 변수 처리 

api.add_resource(User_List,'/user')

api.add_resource(UserResource,'/user/login','/user/<int:user_id>/my')# 이런식으로 했을 때 유지보수가 헷깔리는 경우가 많기 때문에 클래스를 바꾸는 것이 현명하다.

api.add_resource(UserLogoutResource,'/user/logout')

#내정보 가져오는 API개발
# /users/<int:user_id>/my => UserResource Get
# id,email. username, is_active 이 3개 정보를 클라이언트에 응답


if __name__=="__main__":

    app.run(port=5003)

