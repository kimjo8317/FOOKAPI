from datetime import datetime

from fastapi import FastAPI, Depends, Path, HTTPException, File, UploadFile
from pydantic import BaseModel
from database import engineconn
from models import Userinfo
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from fastapi.middleware.cors import CORSMiddleware
# cors = 웹 브라우저에서 실행되는 자바스크립트에서 다른 출처의 자원에 접근할 때 발생하는 보안상의 제약을 우회할 때 사용
app = FastAPI()

engine = engineconn()
session = engine.sessionmaker()

origins = [
    "http://localhost",
    "http://localhost:3000"
]
# 프론트의 react 주소를 알려줌.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

pwd_content = CryptContext(schemes=["bcrypt"], deprecated="auto")

# fastapi 기본설정


class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    phonenumber: str
    email: str
    birth: str


class User(UserCreate):
    name: str

    class Config:
        orm_mode = True


#######################################
def get_db():  # 호출이 되면 db에 세션을 붙임 , yield (return과 유사하나 결과값을 준 후 메모리에 들고 있음.)
    try:
        db = session
        yield db

    finally:
        db.close()  # db를 닫아주지 않으면 병목현상이 생김 (fastapi에는 thread를 20개를 가지고 있으며 그 이상의 작업을 요청시 병목현상 발생.)


@app.post("/signup/", tags=['login'])
async def create_user(user: User, db: session = Depends(get_db)):
    if db.query(exists().where(Userinfo.username == user.username)).scalar():  # scalar = column의 값만 들고옴.(boolean형태)
        # query문을 보기 쉽게 구성가능.
        raise HTTPException(status_code=400,
                            detail="Username already registered")  # 400 에러 = 클라이언트 쪽에서 잘못된 요청을 한 경우 발생.
    hashed_password = pwd_content.hash(user.password)  # 에러가 발생하지 않았을 때 패스워드 해쉬 실행.
    db_user = Userinfo(username=user.username, password=hashed_password, name=user.name, phonenumber=user.phonenumber,email=user.email,birth=user.birth)  # 위에서 처리된 내용을 db에 mapping.
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # db의 종료된 자원들을 refresh , thread 1개를 풀어주는 것.
    return {"username": db_user.username}


@app.post("/login/", tags=['login'])
async def login(user: UserCreate, db: session = Depends(get_db)):
    db_user = db.query(Userinfo).filter(
        Userinfo.username == user.username).first()  # first() -> filter에서 걸러진 데이터의 행을 가져옴. db에서 username,password를 다 가져옴.
    if not db_user:
        raise HTTPException(status_code=400, detail="incorrect username or password")  # db에 유저의 데이터가 없을 때.
    if not db_user.verify_password(user.password):
        raise HTTPException(status_code=400, detail="incorrect password")
    return {"username": db_user.username, "name": db_user.name}


# db에 접근한다는 것은 데이터를 저장한다는 용도

# app에 전부 작성하는 것은 좋은 코딩이 아님 , router를 짜서 app에서 import하여 작성하는 것이 좋음.

@app.get("/users/{username}", tags=['login'])
async def read_user(username: str, db: Session = Depends(get_db)):  # 값의 종류가 적을땐 파라미터로써 가져오는게 관리면에서 편하다.
    db_user = db.query(Userinfo).filter(Userinfo.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.name


@app.delete("/users/{username}", tags=['login'])
async def delete_user(username: str, db: Session = Depends(get_db)):
    db_user = db.query(Userinfo).filter(Userinfo.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    db.delete(db_user)
    db.commit()
    return {"Message : User succesfully deleted"}


@app.put("/users/{username}", tags=['login'])
async def update_user(username: str, name: str, db: Session = Depends(get_db)):
    db_user = db.query(Userinfo).filter(Userinfo.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    db_user.name = name
    db.commit()
    db.refresh(db_user)
    return {"Message : Username sucesfully updated"}


