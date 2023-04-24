from sqlalchemy import Column, TEXT, INT, BIGINT, DATE
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

Base = declarative_base()

pwd_content = CryptContext(schemes=["bcrypt"], deprecated="auto")


# bycrpt : 해쉬함수를 설정하는 기능

class Userinfo(Base):
    __tablename__ = "Userinfo"

    id = Column(BIGINT, nullable=False, autoincrement=True, primary_key=True)
    username = Column(TEXT, nullable=False)
    password = Column(TEXT, nullable=False)
    name = Column(TEXT, nullable=False)
    phonenumber = Column(TEXT, nullable=False)
    email = Column(TEXT, nullable=False)
    birth = Column(TEXT, nullable=False)


    def verify_password(self, password):
        return pwd_content.verify(password, self.password)



# String을 고정된 길이의 해쉬로 전환 ex) 안 -> 3e1wr35qerw5
# 길이가 달라지면 해쉬 값이 완전히 달라짐.
# 암호화