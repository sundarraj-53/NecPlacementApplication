from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer
from database import base,db_engine
from datetime import datetime
from datetime import datetime, timedelta
from sqlalchemy import Boolean, Column, ForeignKey,  String, DateTime, LargeBinary,func


class Parents_otp(base):
    __tablename__="Parents_otp"

    id=Column(Integer,primary_key=True, index=True)
    phone_no=Column(String(255),nullable=False,index=True)
    otp=Column(Integer,nullable=False,index=True)
    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    expiration_time = Column(DateTime, nullable=False,index=True) 




base.metadata.create_all(bind=db_engine)
