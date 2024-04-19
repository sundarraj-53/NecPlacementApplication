from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer
from database import base,db_engine
from datetime import datetime
from datetime import datetime, timedelta
from sqlalchemy import Boolean, Column, ForeignKey,  String, DateTime, LargeBinary,func


class Signup_Otp(base):
    __tablename__="Signup_Otp"

    id=Column(Integer,primary_key=True, index=True)
    email=Column(String(255),nullable=False,index=True)
    otp=Column(Integer,nullable=False,index=True)
    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    expiration_time = Column(DateTime, nullable=False,index=True) 



class Signup(base):
    __tablename__="Signup"
    id=Column(Integer,primary_key=True, index=True)
    email=Column(String(255),nullable=False,index=True)
    password=Column(String(255),nullable=False, index=True)
    profile=Column(String(255),nullable=False,index=True)
    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Placement_signup(base):
    __tablename__="Placement_signup"
    id=Column(Integer,primary_key=True, index=True)
    email=Column(String(255),nullable=False,index=True)
    password=Column(String(255),nullable=False, index=True)
    profile=Column(String(255),nullable=False,index=True)
    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class parentSignup(base):
    __tablename__="Parent_Signup"
    id=Column(Integer,primary_key=True, index=True)
    username=Column(String(255),nullable=False,index=True)
    parent_Name=Column(String(255),nullable=False,index=True)
    phoneNo=Column(String(255),nullable=False,index=True)
    password=Column(String(255),nullable=False, index=True)

    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())



class HOD(base):
    __tablename__ = "HOD"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String(255), nullable=False, index=True)
    password = Column(String(255), nullable=False, index=True)
    depname = Column(String(255), nullable=False, index=True)
    profile=Column(String(255),nullable=False,index=True)
    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Master(base):
    __tablename__ = "Master"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String(255), nullable=False, index=True)
    password = Column(String(255), nullable=False, index=True)
    priority = Column(String(255), nullable=False, index=True)
    profile=Column(String(255),nullable=False,index=True)

    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())



class Staff_signup(base):
        __tablename__="Staff_signup"
        id=Column(Integer,primary_key=True, index=True)
        email=Column(String(255),nullable=False,index=True)
        password=Column(String(255),nullable=False, index=True)
        profile=Column(String(255),nullable=False,index=True)
        # common for all the tables
        status = Column(String(255), nullable=False, index=True)
        created_at = Column(DateTime, server_default=func.now())
        updated_at = Column(DateTime, onupdate=func.now())

class Registeration(base):
    __tablename__="registeration"
    id=Column(Integer, primary_key=True,index=True)
    regno=Column(String(255), nullable=False, index=True)
    name=Column(String(255), nullable=False, index=True)
    department=Column(String(255), nullable=False, index=True)
    email=Column(String(255), nullable=False, index=True)
    phone_Number=Column(String(255), nullable=False, index=True)
    pan_No=Column(String(255), nullable=False, index=True)
    Aadhar_No=Column(String(255), nullable=False, index=True)
    Gender=Column(String(255), nullable=False, index=True)
    DOB=Column(String(255), nullable=False, index=True)
    personal_Email=Column(String(255), nullable=True, index=True)
    caste=Column(String(255), nullable=False, index=True)
    religion=Column(String(255), nullable=False, index=True)
    marital_Status=Column(String(255), nullable=False, index=True)
    Father_Name=Column(String(255), nullable=False, index=True)
    Mother_Name=Column(String(255), nullable=False, index=True)
    Father_Occupation=Column(String(255), nullable=False, index=True)
    Mother_Occupation=Column(String(255), nullable=False, index=True)
    Father_Phone_no=Column(String(255), nullable=False, index=True)
    Mother_Phone_no=Column(String(255), nullable=False, index=True)
    address=Column(String(255), nullable=False, index=True)
    permant_address=Column(String(255), nullable=False, index=True)
    SSLC_school_Name=Column(String(255), nullable=False, index=True)
    SSLC_board_Of_Studies=Column(String(255), nullable=False, index=True)
    SSLC_Mark=Column(String(255), nullable=False, index=True)
    SSLC_Percentage=Column(String(255), nullable=False, index=True)
    SSLC_YOP=Column(String(255), nullable=False, index=True)
    HSC_school_Name=Column(String(255), nullable=True, index=True)
    HSC_board_Of_Studies=Column(String(255), nullable=True, index=True)
    HSC_Mark=Column(String(255), nullable=True, index=True)
    HSC_Percentage=Column(String(255), nullable=True, index=True)
    HSC_YOP=Column(String(255), nullable=True, index=True)
    diploma_college_name=Column(String(255), nullable=True, index=True)
    diploma_Mark=Column(String(255), nullable=True, index=True)
    diploma_Percentage=Column(String(255), nullable=True, index=True)
    diploma_YOP=Column(String(255), nullable=True, index=True)
    college_CGPA=Column(String(255), nullable=True, index=True)
    history_Of_Arrears=Column(String(255), nullable=False, index=True)
    College_YOP=Column(String(255), nullable=False, index=True)
    tutor_name=Column(String(255), nullable=False, index=True)
    tutor_email=Column(String(255), nullable=False, index=True)
    no_Of_History_of_Arrears=Column(String(255), nullable=True, index=True)
    standing_Arrears=Column(String(255), nullable=False, index=True)
    no_Of_Standing_arrears=Column(String(255), nullable=True, index=True)
    types_Of_companies=Column(String(255), nullable=False, index=True)
    aadhar_Card=Column(String(255), nullable=False, index=True)
    pan_Card=Column(String(255), nullable=False, index=True)
    photo=Column(String(255), nullable=False, index=True)
    certificates=Column(String(255), nullable=False, index=True)
    resume=Column(String(255), nullable=False, index=True)
    passport=Column(String(255), nullable=False, index=True)
    placement_status=Column(String(255), nullable=False, index=True)
    
    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    approvedby=Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class ApprovalRegisteration(base):
    __tablename__="ApprovalRegisteration"
    id=Column(Integer, primary_key=True,index=True)
    regno=Column(String(255), nullable=False, index=True)
    name=Column(String(255), nullable=False, index=True)
    department=Column(String(255), nullable=False, index=True)
    email=Column(String(255), nullable=False, index=True)
    phone_Number=Column(String(255), nullable=False, index=True)
    pan_No=Column(String(255), nullable=False, index=True)
    Aadhar_No=Column(String(255), nullable=False, index=True)
    Gender=Column(String(255), nullable=False, index=True)
    DOB=Column(String(255), nullable=False, index=True)
    personal_Email=Column(String(255), nullable=True, index=True)
    caste=Column(String(255), nullable=False, index=True)
    religion=Column(String(255), nullable=False, index=True)
    marital_Status=Column(String(255), nullable=False, index=True)
    Father_Name=Column(String(255), nullable=False, index=True)
    Mother_Name=Column(String(255), nullable=False, index=True)
    Father_Occupation=Column(String(255), nullable=False, index=True)
    Mother_Occupation=Column(String(255), nullable=False, index=True)
    Father_Phone_no=Column(String(255), nullable=False, index=True)
    Mother_Phone_no=Column(String(255), nullable=False, index=True)
    address=Column(String(255), nullable=False, index=True)
    permant_address=Column(String(255), nullable=False, index=True)
    SSLC_school_Name=Column(String(255), nullable=False, index=True)
    SSLC_board_Of_Studies=Column(String(255), nullable=False, index=True)
    SSLC_Mark=Column(String(255), nullable=False, index=True)
    SSLC_Percentage=Column(String(255), nullable=False, index=True)
    SSLC_YOP=Column(String(255), nullable=False, index=True)
    HSC_school_Name=Column(String(255), nullable=True, index=True)
    HSC_board_Of_Studies=Column(String(255), nullable=True, index=True)
    HSC_Mark=Column(String(255), nullable=True, index=True)
    HSC_Percentage=Column(String(255), nullable=True, index=True)
    HSC_YOP=Column(String(255), nullable=True, index=True)
    diploma_college_name=Column(String(255), nullable=True, index=True)
    diploma_Mark=Column(String(255), nullable=True, index=True)
    diploma_Percentage=Column(String(255), nullable=True, index=True)
    diploma_YOP=Column(String(255), nullable=True, index=True)
    college_CGPA=Column(String(255), nullable=True, index=True)
    history_Of_Arrears=Column(String(255), nullable=False, index=True)
    College_YOP=Column(String(255), nullable=False, index=True)
    tutor_name=Column(String(255), nullable=False, index=True)
    tutor_email=Column(String(255), nullable=False, index=True)
    no_Of_History_of_Arrears=Column(String(255), nullable=True, index=True)
    standing_Arrears=Column(String(255), nullable=False, index=True)
    no_Of_Standing_arrears=Column(String(255), nullable=True, index=True)
    types_Of_companies=Column(String(255), nullable=False, index=True)
    aadhar_Card=Column(String(255), nullable=False, index=True)
    pan_Card=Column(String(255), nullable=False, index=True)
    photo=Column(String(255), nullable=False, index=True)
    certificates=Column(String(255), nullable=False, index=True)
    resume=Column(String(255), nullable=False, index=True)
    passport=Column(String(255), nullable=False, index=True)
    placement_status=Column(String(255), nullable=True, index=True)
    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class placement_coordinator(base):
    __tablename__="placement_coordinator"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    department = Column(String(255), nullable=False, index=True)
    email= Column(String(255), nullable=False, index=True)
    phone=Column(String(255),nullable=False,index=True)
    address=Column(String(255),nullable=False,index=True)

    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now()) 

class staff_coordinator(base):
    __tablename__="staff_coordinator"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    department = Column(String(255), nullable=False, index=True)
    email= Column(String(255), nullable=False, index=True)
    phone=Column(String(255),nullable=False,index=True)
    address=Column(String(255),nullable=False,index=True)

    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now()) 

# class Staff_registeration(base):
#      __tablename__="Staff_registeration"

#      id = Column(Integer, primary_key=True, index=True)
#      name = Column(String(255), nullable=False, index=True)
#      department = Column(String(255), nullable=False, index=True)
#      email= Column(String(255), nullable=False, index=True)
#      phone=Column(String(255),nullable=False,index=True)
#      address=Column(String(255),nullable=False,index=True)

#     # common for all the tables
#      status = Column(String(255), nullable=False, index=True)
#      created_at = Column(DateTime, server_default=func.now())
#      updated_at = Column(DateTime, onupdate=func.now()) 


class Login(base):
    __tablename__ = "login"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, index=True)
    password = Column(String(255), nullable=False, index=True)

     # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())  


# Santhosh Page
class RoundCompletionData(base):
    __tablename__ = "roundCompletionData"
    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    company_id=Column(Integer,nullable=False)
    round_number = Column(Integer, nullable=False)
    round_name = Column(String(255), nullable=False)
    batch = Column(String(255), nullable=False)
    student_id = Column(Integer, nullable=False)
    # Passed/Failed
    round_status = Column(String(255), nullable=False)
    
    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())



class Addcompany(base):
    __tablename__="addcompany"

    id=Column(Integer,primary_key=True,index=True)
    image_url=Column(String(255), nullable=False, index=True)
    company_url=Column(String(255), nullable=False, index=True)
    created_by=Column(String(255),nullable=False,index=True)

    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())  



class HRData(base):
    
    __tablename__="HRData"

    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    email=Column(String(255), nullable=False, index=True)
    phoneno=Column(String(255), nullable=False, index=True)
    core=Column(String(255), nullable=False, index=True)
    Location=Column(String(255), nullable=False, index=True)
    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Placementinfo(base):
    __tablename__="placementinfo"

    id=Column(Integer,primary_key=True,index=True)
    companyName=Column(String(255), nullable=False, index=True)
    driveDate=Column(String(255), nullable=False, index=True)
    ctcPackage=Column(String(255), nullable=False, index=True)
    venue=Column(String(255), nullable=False, index=True)
    stream=Column(String(255), nullable=False, index=True)
    SSLC=Column(String(255),nullable=True,index=True)
    HSC=Column(String(255),nullable=True,index=True)
    CGPA=Column(String(255),nullable=True,index=True)
    round1=Column(String(255),nullable=True,index=True)
    round2=Column(String(255),nullable=True,index=True)
    round3=Column(String(255),nullable=True,index=True)
    round4=Column(String(255),nullable=True,index=True)
    round5=Column(String(255),nullable=True,index=True)
    round6=Column(String(255),nullable=True,index=True)

    created_by=Column(String(255),nullable=False,index=True)

    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())  


class Getaccess(base):
    
    __tablename__="Getaccess"

    id=Column(Integer,primary_key=True,index=True)
    email=Column(String(255), nullable=False, index=True)
    department=Column(String(255), nullable=False, index=True)
    placement_email=Column(String(255), nullable=False, index=True)
    subject=Column(String(255), nullable=False, index=True)
    access=Column(Boolean, nullable=True, index=True)

    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Accessedit(base):
    __tablename__="Accessedit"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(255), nullable=False, index=True)
    email=Column(String(255), nullable=False, index=True)
    department=Column(String(255),nullable=False, index=True)
    accessemail=Column(Boolean,nullable=True,index=True)
    accesssslcmark=Column(Boolean,nullable=True,index=True)
    accesssslcpercentage=Column(Boolean,nullable=True,index=True)
    accesshscmark=Column(Boolean,nullable=True,index=True)
    accesshscpercentage=Column(Boolean,nullable=True,index=True)
    accessdiplomapercentage=Column(Boolean,nullable=True,index=True)
    accesscgpa=Column(Boolean,nullable=True,index=True)

    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Placeddata(base):
    __tablename__="Placeddata"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String(255), nullable=False, index=True)
    name=Column(String(255), nullable=False, index=True)
    department=Column(String(255), nullable=False, index=True)
    phoneno=Column(String(255), nullable=False, index=True)
    dob=Column(String(255), nullable=False, index=True)
    address =Column(String(255), nullable=False, index=True)
    companyname=Column(String(255), nullable=False, index=True)
    modeofhiring=Column(String(255), nullable=False, index=True)
    package=Column(String(255), nullable=False, index=True)
    location=Column(String(255), nullable=False, index=True)
    declaration=Column(String(255), nullable=False, index=True)
    offerletter =Column(String(255), nullable=False, index=True)
    internletter=Column(String(255), nullable=False, index=True)
    feedback=Column(String(255), nullable=False, index=True)
    created_by=Column(String(255), nullable=False, index=True)
    
    
    # common for all the tables
    status = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

base.metadata.create_all(bind=db_engine)