from http import client
from sqlalchemy import or_
from fastapi import FastAPI, HTTPException,Request,Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import requests
from sqlalchemy import null

from database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import Boolean
from fastapi.middleware.cors import CORSMiddleware
import random
import models
from datetime import datetime, timedelta  # Import 'datetime' directly
import shutil
import uuid
import vonage
from typing import Dict
import os
import datetime
from config import ACCESS_TOKEN_EXPIRE_MINUTES,create_access_token,get_current_user,decode_token
from api import api_key,url,auth_token,account_SID,brevo_url,api_secret,brevo_api_key

app=FastAPI(max_request_size=100 * 1024 * 1024)
MessageContent = Dict[str, str]

origins = [
    "http://127.0.0.1:5501",
     "http://127.0.0.1",
    "http://localhost", 
     "http://127.0.0.1:5500",   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    
    finally:
        db.close()


# For getting OTP
@app.post("/getotp")
async def getotp(request: Request, db: Session = Depends(get_db)):
    print(str(request))
    try:
        data = await request.json()
        email = data.get('email')
        print(email)
        placement_email=db.query(models.placement_coordinator).filter(models.placement_coordinator.email==email).filter(models.placement_coordinator.status=="Active").first()
        registered_email = db.query(models.Registeration).filter(models.Registeration.email == email).filter(models.Registeration.status=="Active").first()
        staff_email=db.query(models.staff_coordinator).filter(models.staff_coordinator.email==email).filter(models.staff_coordinator.status=="Active").first()
        signup_email=db.query(models.Signup).filter(models.Signup.email==email).filter(models.Signup.status=="Active").first()
        placement_user=db.query(models.Placement_signup).filter(models.Placement_signup.email==email).filter(models.Placement_signup.status=="Active").first()
        staff_user=db.query(models.Staff_signup).filter(models.Staff_signup.email==email).filter(models.Staff_signup.status=="Active").first()
        hod_mail = db.query(models.HOD).filter(models.HOD.email==email).filter(models.HOD.status=="Active").first()
        master_mail = db.query(models.Master).filter(models.Master.email==email).filter(models.Master.status=="Active").first()
        existing_email = db.query(models.Signup_Otp).filter(models.Signup_Otp.email == email).filter(models.Signup_Otp.status=="Active").first()

        if placement_email or registered_email or staff_email or hod_mail or master_mail:
            return JSONResponse(content={"message": "You have already completed the registration"}, status_code=303)
 
        elif signup_email:
             return JSONResponse(content={"message":"Redirect to registeration page","profile":"Student"},status_code=303)
        
        elif placement_user or staff_user:
            return JSONResponse(content={"message":"Redirect to registeration page","profile":"Placement or Staff"},status_code=303)

        else:
            otp = random.randint(1000, 9999)
            expiration_time = datetime.datetime.now() + timedelta(minutes=1)
            print(expiration_time)
            email_data = {
                "sender": {"name": "NEC Placement", "email": "2015053@nec.edu.in"},
                "to": [{"email": email}],
                "subject": "OTP Verification",
                "htmlContent": f"""<html><body>
                    <p>Dear user,</p>
                    <p>OTP for your Email account is <strong>{otp}</strong>.</p>
                    <p>Need help, or have questions? Just reply to this email; we would be happy to help you.</p>
                    <p>Best regards,<br>
                    NEC Placement</p>
                    </body></html>"""
            }

            headers = {
                'Content-Type': 'application/json',
                'api-key': api_key
            }

            if existing_email:
                db.query(models.Signup_Otp).filter(models.Signup_Otp.email == email).update({"otp": otp})
                db.commit()
                response = requests.post(url, headers=headers, json=email_data)
                if response.status_code == 201:
                    body = models.Signup_Otp(email=email, otp=otp, status="Active")
                    db.add(body)
                    db.commit()
                    print("Email sent successfully!")
                    return JSONResponse(content={"message": "Email Sent Successfully"}, status_code=200)
                else:
                    print(f"Failed to send email. Status code: {response.status_code}")
                    print(response.text)
                    return JSONResponse(content={"message": "Due to network issues, the email was not sent successfully"},status_code=503)
                

            response = requests.post(url, headers=headers, json=email_data)  # Use 'json' parameter here

            if response.status_code == 201:
                body = models.Signup_Otp(email=email, otp=otp, status="Active",expiration_time=expiration_time)
                db.add(body)
                db.commit()
                print("Email sent successfully!")
                return JSONResponse(content={"message": "Email Sent Successfully"}, status_code=200)
            else:
                print(f"Failed to send email. Status code: {response.status_code}")
                print(response.text)
                return JSONResponse(content={"error": "Due to network issues, the email was not sent successfully"},status_code=503)

     
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
    


# verify the user otp and stored otp are same or not

@app.post("/otpverification")
async def otpVerification(request:Request,db:Session=Depends(get_db)):
    try:
        data=await request.json()
        print(data)
        email=data.get('email')
        otp=data.get('otp')
        time=datetime.datetime.now()
        if email and otp:
                check=db.query(models.Signup_Otp).filter(models.Signup_Otp.email==email).filter(models.Signup_Otp.otp==otp).filter(models.Signup_Otp.status=="Active").first();
                if check:
                    return JSONResponse(content={"message":"Success"},status_code=200)
                else:
                    return JSONResponse(content={"message":"Wrong OTP for the account"},status_code=401)
        else:
                return JSONResponse(content={"message":"Incorrect of data"},status_code=400)
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# for getting email and password
@app.post("/signup")
async def signup(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        print(data)
        email = data.get('email')
        password = data.get('password')

        if email and password:

            if "principal" in email.lower() or "director" in email.lower() or email.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
                Master_name = ""
                priority=""
                if "principal" in email.lower():
                    print("Master_Principal")
                    Master_name = "PRINCIPAL"
                    priority="VIEW"

                elif "director" in email.lower():
                    print("Master_Director")
                    Master_name = "DIRECTOR"
                    priority="VIEW"

            
                elif  email.lower() in "kgs@nec.edu.in":
                     print("Master_DEAN")
                     Master_name = "DEAN/TPC"
                     priority="ALL"

                
                else:
                    print("Master_PLACEMENT_CONVENER")
                    Master_name = "PLACEMENT CONVENER"
                    priority="ALL"

                new_user =  models.Master(email=email, password=password, priority=priority,profile=Master_name,status="Active")
                db.add(new_user)
                db.commit()

                return JSONResponse(content={"message": "Signup successful","profile":Master_name}, status_code=200)
            
            elif "hod" in email.lower():
                dep_name = email.split("hod")[1]
                dep_name = (dep_name.split('@')[0]).upper()
                new_user = models.HOD(email=email, password=password, depname = dep_name,profile="HOD",status="Active")
                db.add(new_user)
                db.commit()
                return JSONResponse(content={"message": "Signup successful","profile":"HOD_%s"%(dep_name) }, status_code=200)

            elif "placement" in email.lower() and  email.lower() not in "placement@nec.edu.in":
                new_user = models.Placement_signup(email=email, password=password,profile="Placement",status="Active")
                db.add(new_user)
                print("Placement")
                db.commit()
                return JSONResponse(content={"message": "Signup successful","profile":"Placement"}, status_code=200)
            
            elif not any(char.isdigit() for char in email):
                new_user=models.Staff_signup(email=email,password=password,profile="Staff",status="Active")
                print("Staff")
                db.add(new_user)
                db.commit()
                return JSONResponse(content={"message": "Signup successful","profile":"Staff"}, status_code=200)
            
            else:
                new_user = models.Signup(email=email, password=password,profile="Student",status="Active")
                print(new_user)
                db.add(new_user)
                db.commit()
                return JSONResponse(content={"message": "Signup successful","profile":"Student"}, status_code=200)
        else:
            return JSONResponse(content={"error":"Request data is not fullfilled"}, status_code=400)
         
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
    


# Student registeration data and create access page
# If the tutor accepts only it move to the registeration table otherwise it kept left in this table
@app.post("/registeration")
async def registeration(request:Request,db:Session=Depends(get_db)):
    try:
        data=await request.form()
        regno=data.get('regno')
        name=data.get('name')
        department=data.get('department')
        email=data.get('email')
        phone_Number=data.get('phone_Number')
        pan_No=data.get('pan_No')
        Aadhar_No=data.get('Aadhar_No')
        Gender=data.get('Gender')
        DOB=data.get('DOB')
        personal_Email=data.get('personal_Email')
        caste=data.get('caste')
        religion=data.get('religion')
        marital_Status=data.get('marital_Status')
        Father_Name=data.get('Father_Name')
        Mother_Name=data.get('Mother_Name')
        Father_Occupation=data.get('Father_Occupation')
        Mother_Occupation=data.get('Mother_Occupation')
        Father_Phone_no=data.get('Father_Phone_no')
        Mother_Phone_no=data.get('Mother_Phone_no')
        address=data.get('address')
        permant_address=data.get('permant_address')
        SSLC_school_Name=data.get('SSLC_school_Name')
        SSLC_board_Of_Studies=data.get('SSLC_board_Of_Studies')
        SSLC_Mark=data.get('SSLC_Mark')
        SSLC_Percentage=data.get('SSLC_Percentage')
        SSLC_YOP=data.get('SSLC_YOP')
        HSC_school_Name=data.get('HSC_school_Name')
        HSC_board_Of_Studies=data.get('HSC_board_Of_Studies')
        HSC_Mark=data.get('HSC_Mark')
        HSC_Percentage=data.get('HSC_Percentage')
        HSC_YOP=data.get('HSC_YOP')
        tutor_name=data.get('tutor_name')
        diploma_college_name=data.get('diploma_college_name')
        diploma_Mark=data.get('diploma_Mark')
        diploma_Percentage=data.get('diploma_Percentage')
        diploma_YOP=data.get('diploma_YOP')
        college_CGPA=data.get('college_CGPA')
        College_YOP=data.get('College_YOP')
        history_Of_Arrears=data.get('history_Of_Arrears')
        no_Of_History_of_Arrears=data.get('no_Of_History_of_Arrears')
        standing_Arrears=data.get('standing_Arrears')
        no_Of_Standing_arrears=data.get('no_Of_Standing_arrears')
        types_Of_companies=data.get('types_Of_companies')
        aadhar_Card=data.get('aadhar_Card')
        placement_status=data.get('placement_status')
        pan_Card=data.get('pan_Card')
        photo=data.get('photo')
        certificates=data.get('certificates')
        resume=data.get('resume')
        tutor_email=data.get('tutor_email')
        passport=data.get('passport')
        pancard_name=data.get('pancard_name')
        aadharcard_name=data.get('aadharcard_name')
        photo_name=data.get('photo_name')
        resume_name=data.get('resume_name')
        certificates_name=data.get('certificates_name')
        passport_name=data.get('passport_name')
        extention1 = pancard_name.split('.')[-1]
        print(extention1)
        extention2 = aadharcard_name.split('.')[-1]
        extention3 = photo_name.split('.')[-1]
        extention4 = resume_name.split('.')[-1]
        extention5 = certificates_name.split('.')[-1]
        extention6=passport_name.split('.')[-1]
        upload_aadhar_folder = "./aadhar_Card"
        upload_pan_folder="./pan_Card"
        upload_photo_folder="./photo"
        upload_certificates_folder="./certificates"
        upload_resume_folder="./resume"
        upload_passport_folder="./passport"
        if not os.path.exists(upload_aadhar_folder):
            os.makedirs(upload_aadhar_folder)    
        if not os.path.exists(upload_pan_folder):
            os.makedirs(upload_pan_folder)
        if not os.path.exists(upload_photo_folder):
            os.makedirs(upload_photo_folder)
        if not os.path.exists(upload_certificates_folder):
            os.makedirs(upload_certificates_folder)
        if not os.path.exists(upload_resume_folder):
            os.makedirs(upload_resume_folder) 
        if not os.path.exists(upload_passport_folder):
            os.makedirs(upload_passport_folder) 
        print(extention1)
        token_image1 = str(uuid.uuid4()) + '.' + str(extention1)
        token_image2 = str(uuid.uuid4()) + '.' + str(extention2)
        token_image3 = str(uuid.uuid4()) + '.' + str(extention3)
        token_image4 = str(uuid.uuid4()) + '.' + str(extention4)
        token_image5 = str(uuid.uuid4()) + '.' + str(extention5)
        token_image6=str(uuid.uuid4()) + '.' + str(extention6)
        file_location1 =  f"{upload_aadhar_folder}/{token_image1}"
        file_location2 =  f"{upload_pan_folder}/{token_image2}"
        file_location3 =  f"{upload_photo_folder}/{token_image3}"
        file_location4 =  f"{upload_certificates_folder}/{token_image4}"
        file_location5 =  f"{upload_resume_folder}/{token_image5}"
        file_location6 =  f"{upload_passport_folder}/{token_image6}"
        with open(file_location1, 'wb+') as file_object:
                shutil.copyfileobj(aadhar_Card.file, file_object)
        with open(file_location2, 'wb+') as file_object:
                shutil.copyfileobj(pan_Card.file, file_object)
        with open(file_location3, 'wb+') as file_object:
                shutil.copyfileobj(photo.file, file_object)
        with open(file_location4, 'wb+') as file_object:
                shutil.copyfileobj(certificates.file, file_object)
        with open(file_location5, 'wb+') as file_object:
                shutil.copyfileobj(resume.file, file_object)
        with open(file_location6, 'wb+') as file_object:
                shutil.copyfileobj(passport.file, file_object)
        existing_data=db.query(models.Registeration).filter(models.Registeration.email==email).first()
        if existing_data:
                return JSONResponse(content={"message":"Already used college Email"},status_code=303)
                
        newbody=models.Accessedit(name=name,email=email,department=department,status="Active")
        body=models.ApprovalRegisteration(
                    regno=regno,
                    name=name,
                    department=department,
                    email=email,
                    phone_Number=phone_Number,
                    pan_No=pan_No,
                    Aadhar_No=Aadhar_No,
                    Gender=Gender,
                    DOB=DOB,
                    tutor_name=tutor_name,
                    personal_Email=personal_Email,
                    caste=caste,
                    tutor_email=tutor_email,
                    religion=religion,
                    marital_Status=marital_Status,
                    Father_Name=Father_Name,
                    Mother_Name=Mother_Name,
                    Father_Occupation=Father_Occupation,
                    Mother_Occupation=Mother_Occupation,
                    Father_Phone_no=Father_Phone_no,
                    Mother_Phone_no=Mother_Phone_no,
                    address=address,
                    placement_status=placement_status,
                    permant_address=permant_address,
                    SSLC_school_Name=SSLC_school_Name,
                    SSLC_board_Of_Studies=SSLC_board_Of_Studies,
                    SSLC_Mark=SSLC_Mark,
                    SSLC_Percentage=SSLC_Percentage,
                    SSLC_YOP=SSLC_YOP,
                    HSC_school_Name=HSC_school_Name,
                    HSC_board_Of_Studies=HSC_board_Of_Studies,
                    HSC_Mark=HSC_Mark,
                    HSC_Percentage=HSC_Percentage,
                    HSC_YOP=HSC_YOP,
                    diploma_college_name=diploma_college_name,
                    diploma_Mark=diploma_Mark,
                    diploma_YOP=diploma_YOP,
                    diploma_Percentage=diploma_Percentage,
                    college_CGPA=college_CGPA,
                    College_YOP=College_YOP,
                    history_Of_Arrears=history_Of_Arrears,
                    no_Of_History_of_Arrears=no_Of_History_of_Arrears,
                    standing_Arrears=standing_Arrears,
                    no_Of_Standing_arrears=no_Of_Standing_arrears,
                    types_Of_companies=types_Of_companies,
                    aadhar_Card=token_image1,
                    pan_Card=token_image2,
                    photo=token_image3,
                    certificates=token_image4,
                    resume=token_image5,
                    passport=token_image6,
                    status="Active"
                    )
        db.add(newbody)
        db.add(body)
        db.commit()
        return JSONResponse(content={"message":"Datas are Registered successfully"},status_code=200)

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# adding placement placement_coordinator details

@app.post('/placement_coordinator')
async def placement_coordinator(request:Request,db:Session=Depends(get_db)):
    try:
        data=await request.json()
        name=data.get('name')
        department=data.get('department')
        email=data.get('email')
        phone=data.get('phone')
        address=data.get('address')
        if "placement" in email.lower():
            placement=models.placement_coordinator(name=name,department=department,email=email,phone=phone,address=address,status="Active")
            db.add(placement)
            db.commit()
            return JSONResponse(content={"message":"Registered Successfully"},status_code=200)
        
        else:
            placement=models.staff_coordinator(name=name,department=department,email=email,phone=phone,address=address,status="Active")
            db.add(placement)
            db.commit()
            return JSONResponse(content={"message":"Registered Successfully"},status_code=200)
       
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)



# This route also update it divided into four route

#getting the approval from the approvalRegisteration and access page
@app.get('/getAccessApproval')
async def approvals(request:Request,db:Session=Depends(get_db),current_user: str = Depends(get_current_user)):
    try:
            print(current_user)
            email = current_user.lower()
            if "principal" in email.lower() or "director" in email.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
                checkPriority=db.query(models.Master.priority).filter(models.Master.email==email).filter(models.Master.status=="ACTIVE").first()
                if checkPriority=="view":
                   return JSONResponse(content={"Error":"Account does not have the privilege"},status_code=400)
                else:
                   users = db.query(models.Getaccess).filter(models.Getaccess.access==" ").filter(models.Getaccess.status=='ACTIVE').all()
                   users_json=jsonable_encoder(users)
                   return JSONResponse(content={"Users":users_json},status_code=200)
            
            elif('placement' in email.lower() and email != 'placement@nec.edu.in'):
                
                placement = db.query(models.placement_coordinator).filter(models.placement_coordinator.email == email).first()
                if placement:
                    users = db.query(models.Getaccess).filter(models.Getaccess.access.is_(None)).filter(models.Getaccess.placement_email == email).filter(models.Getaccess.status == 'ACTIVE').all()    
                    if users:
                        users=jsonable_encoder(users)
                        return JSONResponse(content={"Users":users},status_code=200)
                    else:
                        return JSONResponse(content={"Message":"No request is Available"},status_code=200)
                else:
                    return JSONResponse(content={"error":"User is Not Available"},status_code=400)

            else:
                return JSONResponse(content={"error":"User does not have the privilege"},status_code=400)

    except HTTPException as e:
        print(e.status_code)
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# Status changed in the Get Access Page
# It can be modified only by the master table and placement coordinator

@app.patch('/getAccessApproval/{id}/{status}')
async def updateStudentStatus(id: int, status: str, request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        if "principal" in current_user.lower() or "director" in current_user.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
            checkPriority = db.query(models.Master.priority).filter(models.Master.email == current_user).filter(models.Master.status == "ACTIVE").first()
            if checkPriority[0] == "view":
                return JSONResponse(content={"Error": "Account does not have the privilege"}, status_code=400)
            else:
                student = db.query(models.Getaccess).filter(models.Getaccess.id == id).filter(models.Getaccess.access.is_(None)).filter(models.Getaccess.status=='ACTIVE').first()
                if student:
                    if status=="ACCEPT":
                        db.query(models.Getaccess).filter(models.Getaccess.id == id).update({"access": status == "ACCEPT"})  # Convert status to boolean
                        db.commit()
                        return JSONResponse(content={"message": "Access changed successfully"}, status_code=200)
                    else:
                        db.delete(student)
                        db.commit()
                        return JSONResponse(content={"message": "ACCESS DENIED FROM THE Coordinator"}, status_code=200)
                else:
                    return JSONResponse(content={"error": "Student not found"}, status_code=404)
        
        elif 'placement' in current_user.lower() and current_user != 'placement@nec.edu.in':
            data = db.query(models.placement_coordinator).filter(models.placement_coordinator.email == current_user).filter(models.placement_coordinator.status == "ACTIVE").first()
            if data:
                student = db.query(models.Getaccess).filter(models.Getaccess.id == id).filter(models.Getaccess.access.is_(None)).filter(models.Getaccess.status=='ACTIVE').first()
                if student:
                    if status=="ACCEPT":
                        db.query(models.Getaccess).filter(models.Getaccess.id == id).update({"access": status == "ACCEPT"})  # Convert status to boolean
                        db.commit()
                        return JSONResponse(content={"message": "Access changed successfully"}, status_code=200)
                    else:
                        db.delete(student)
                        db.commit()
                        return JSONResponse(content={"message": "ACCESS DENIED FROM THE Coordinator"}, status_code=200)
                else:
                    return JSONResponse(content={"error": "Student not found"}, status_code=404)
            else:
                return JSONResponse(content={"error": "No user Found"}, status_code=400)
        else:
            return JSONResponse(content={"error": "User does not have the privilege"}, status_code=400)

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)

    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)





# Return the data from the Approval registeration for only their students getStudentData
     
@app.get('/tutorApproval')
async def approvals(request:Request,db:Session=Depends(get_db),current_user: str = Depends(get_current_user)):
    try:
            email = current_user.lower()
            print(email)
            if email and not any(char.isdigit() for char in email) and not ("principal" in email or "director" in email or email in ["kgs@nec.edu.in", "placement@nec.edu.in"]) and not "placement" in email:
                staff = db.query(models.staff_coordinator.department,models.staff_coordinator.name).filter(models.staff_coordinator.email==email).filter(models.staff_coordinator.status=='Active').first()
                if staff:
                    users = db.query(models.ApprovalRegisteration).filter(models.ApprovalRegisteration.department==staff[0]).filter(models.ApprovalRegisteration.tutor_email==email).filter(models.ApprovalRegisteration.status=='ACTIVE').all()
                    if users:
                        # staff=jsonable_encoder(staff)
                        users=jsonable_encoder(users)
                        return JSONResponse(content={"Users":users},status_code=200)
                    else:
                        return JSONResponse(content={"message":"No Request in the list"},status_code=200)            
            else:
                return JSONResponse(content={"error":"User does not have the privilege"},status_code=400)
            

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# Status changed in the Tutor Approval Page
# It can be modified only by the Tutor only

@app.patch('/tutorApproval/{id}/{status}')
async def updateStudentStatus(id: int, status: str, request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        email = current_user.lower()
        if email and not any(char.isdigit() for char in email) and not ("principal" in email or "director" in email or email in ["kgs@nec.edu.in", "placement@nec.edu.in"]) and not "placement" in email:
            staff = db.query(models.staff_coordinator).filter(models.staff_coordinator.email==email).filter(models.staff_coordinator.status=='Active').first()
            if staff:
                user = db.query(models.ApprovalRegisteration).filter(models.ApprovalRegisteration.id==id).filter(models.ApprovalRegisteration.status=='ACTIVE').first()
                if user:
                    if status == "ACCEPT":
                        registration = models.Registeration(
                            regno=user.regno,
                            name=user.name,
                            department=user.department,
                            email=user.email,
                            phone_Number=user.phone_Number,
                            pan_No=user.pan_No,
                            Aadhar_No=user.Aadhar_No,
                            Gender=user.Gender,
                            DOB=user.DOB,
                            placement_status=user.placement_status,
                            tutor_name=user.tutor_name,
                            personal_Email=user.personal_Email,
                            caste=user.caste,
                            tutor_email=user.tutor_email,
                            religion=user.religion,
                            marital_Status=user.marital_Status,
                            Father_Name=user.Father_Name,
                            Mother_Name=user.Mother_Name,
                            Father_Occupation=user.Father_Occupation,
                            Mother_Occupation=user.Mother_Occupation,
                            Father_Phone_no=user.Father_Phone_no,
                            Mother_Phone_no=user.Mother_Phone_no,
                            address=user.address,
                            permant_address=user.permant_address,
                            SSLC_school_Name=user.SSLC_school_Name,
                            SSLC_board_Of_Studies=user.SSLC_board_Of_Studies,
                            SSLC_Mark=user.SSLC_Mark,
                            SSLC_Percentage=user.SSLC_Percentage,
                            SSLC_YOP=user.SSLC_YOP,
                            HSC_school_Name=user.HSC_school_Name,
                            HSC_board_Of_Studies=user.HSC_board_Of_Studies,
                            HSC_Mark=user.HSC_Mark,
                            HSC_Percentage=user.HSC_Percentage,
                            HSC_YOP=user.HSC_YOP,
                            diploma_college_name=user.diploma_college_name,
                            diploma_Mark=user.diploma_Mark,
                            diploma_YOP=user.diploma_YOP,
                            diploma_Percentage=user.diploma_Percentage,
                            college_CGPA=user.college_CGPA,
                            College_YOP=user.College_YOP,
                            history_Of_Arrears=user.history_Of_Arrears,
                            no_Of_History_of_Arrears=user.no_Of_History_of_Arrears,
                            standing_Arrears=user.standing_Arrears,
                            no_Of_Standing_arrears=user.no_Of_Standing_arrears,
                            types_Of_companies=user.types_Of_companies,
                            aadhar_Card=user.aadhar_Card,
                            pan_Card=user.pan_Card,
                            photo=user.photo,
                            certificates=user.certificates,
                            resume=user.resume,
                            passport=user.passport,
                            approvedby=staff.name,
                            status="Active"
                        )
                        db.add(registration)
                        db.delete(user)
                        db.commit()
                        return JSONResponse(content={"message": "Accepted Data Stored in the Registeration"}, status_code=200)
                    else:
                        db.delete(user)
                        db.commit()
                        return JSONResponse(content={"message": "Data Deleted from ApprovalRegisteration"}, status_code=200)
                else:
                    return JSONResponse(content={"message": "No Request found with the given id"}, status_code=404)
            else:
                return JSONResponse(content={"error": "User does not have the privilege"}, status_code=400)
        else:
            return JSONResponse(content={"error": "User does not have the privilege"}, status_code=400)
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)



# It return the student placed data it is used to convert the data into the documented oriented

@app.get('/getPlacedData')
async def getPlacedData(request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        if "principal" in current_user.lower() or "director" in current_user.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
            checkPriority = db.query(models.Master.priority).filter(models.Master.email == current_user).filter(models.Master.status == "ACTIVE").first()
            if checkPriority[0] == "view":
                return JSONResponse(content={"Error": "Account does not have the privilege"}, status_code=400)
            else:
                placed_student = db.query(models.Placeddata).filter(models.Placeddata.status=='ACTIVE').all()
                if placed_student:
                    placed_student=jsonable_encoder(placed_student)
                    return JSONResponse(content={"data": placed_student}, status_code=200)
                else:
                    return JSONResponse(content={"Message": "No Placed Students List is present"}, status_code=404)
                
        elif 'hod' in current_user.lower():
            data = db.query(models.HOD).filter(models.HOD.email == current_user).filter(models.HOD.status == "ACTIVE").first()
            if data:
                placed_student = db.query(models.Placeddata).filter(models.Placeddata.department==data.depname).filter(models.Placeddata.status=='ACTIVE').all()
                if placed_student:
                    placed_student=jsonable_encoder(placed_student)
                    return JSONResponse(content={"data": placed_student}, status_code=200)
                else:
                    return JSONResponse(content={"Message": "No Placed Students List is present"}, status_code=404)
            else:
                return JSONResponse(content={"error": "No user Found"}, status_code=400)

        
        elif 'placement' in current_user.lower() and current_user != 'placement@nec.edu.in':
            data = db.query(models.placement_coordinator).filter(models.placement_coordinator.email == current_user).filter(models.placement_coordinator.status == "ACTIVE").first()
            if data:
                placed_student = db.query(models.Placeddata).filter(models.Placeddata.department==data.department).filter(models.Placeddata.status=='ACTIVE').all()
                if placed_student:
                    placed_student=jsonable_encoder(placed_student)
                    return JSONResponse(content={"data": placed_student}, status_code=200)
                else:
                    return JSONResponse(content={"Message": "No Placed Students List is present"}, status_code=404)
            else:
                return JSONResponse(content={"error": "No user Found"}, status_code=400)
        else:
            return JSONResponse(content={"error": "User does not have the privilege"}, status_code=400)

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)

    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)



@app.post('/hrData')
async def getHRData(request: Request, db : Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        data = await request.json()
        print(data)
        email = data.get('email')
        if "principal" in current_user.lower() or "director" in current_user.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
            checkPriority = db.query(models.Master.priority).filter(models.Master.email == current_user).filter(models.Master.status == "ACTIVE").first()
            if checkPriority[0] == "view":
                return JSONResponse(content={"Error": "Account does not have the privilege"}, status_code=400)
            else:
                existing_mail = db.query(models.HRData).filter(models.HRData.email==email).filter(models.HRData.status=="ACTIVE").first()
                if not existing_mail:
                    name = data.get('name')
                    c_name = data.get('c_name')
                    phoneno = data.get('phoneno')
                    core = data.get('core')
                    Location=data.get("Location")
                    new_user = models.HRData(name = name, email=email,Location=Location,company_name = c_name, phoneno = phoneno,core = core,status="ACTIVE")
                    db.add(new_user)
                    db.commit()
                    return JSONResponse(content={"message": "Signup successful","profile":"HR"}, status_code=200)
                else:
                    return JSONResponse(content={"error":"email already exists"}, status_code=400)

        else:
            return JSONResponse(content={"Message": "Account does not have the privilege"}, status_code=404)
     
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
         

@app.get('/getHRData')
async def getHRData(request: Request, db : Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        if "principal" in current_user.lower() or "director" in current_user.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
            checkPriority = db.query(models.Master.priority).filter(models.Master.email == current_user).filter(models.Master.status == "ACTIVE").first()
            if checkPriority[0] == "view":
                return JSONResponse(content={"Error": "Account does not have the privilege"}, status_code=400)
            else:
                existing_mail = db.query(models.HRData).filter(models.HRData.status=="ACTIVE").all()
                if existing_mail:
                    existing_mail=jsonable_encoder(existing_mail)
                    return JSONResponse(content={"Hr Data": existing_mail}, status_code=200)
                else:
                    return JSONResponse(content={"error":"No Data Found"}, status_code=200)

        else:
            return JSONResponse(content={"Message": "Account does not have the privilege"}, status_code=404)
     
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


@app.patch('/update_HRData/{id}')
async def updateHRData(id: int, request: Request, db : Session = Depends(get_db)):
    try:

        data = await request.json()
        user = db.query(models.HRData).filter(models.HRData.id == id).filter(models.HRData.status=="ACTIVE").first()
        print(user)
        if user:
            if 'email' in data:
                 return JSONResponse(content={"error": "Email cannot be changed"}, status_code=400)
            
            else:
                print(data)
                user.name = data.get('name') if 'name' in data else user.name
                user.phoneno = data.get('phoneno') if 'phoneno' in data else user.phoneno
                user.core = data.get('core') if 'core' in data else user.core
                user.company_name = data.get('company_name') if 'company_name' in data else user.company_name
                user.Location = data.get('Location') if 'Location' in data else user.Location
                db.commit()
                return JSONResponse(content={"message": "Update Successful"}, status_code=200)

        else:
            return JSONResponse(content={"message": "User not found!"}, status_code=404)

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)



# for login of Students
@app.post('/login')
async def login(request:Request,db:Session=Depends(get_db)):
    try:
        data=await request.json()
        print(data)
        email=data.get('email')
        password=data.get('password')

        if email and password:

            if "hod" in email.lower():
                body=db.query(models.HOD).filter(models.HOD.email==email).filter(models.HOD.password==password).filter(models.HOD.status=="Active").first()
                
                if body:
                    dep_name = body.depname
                    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={"sub": email}, expires_delta=access_token_expires
                    )
                    return JSONResponse(content={"bearer": access_token,"Profile":"HOD_%s"%(dep_name)},status_code=200)
                else:
                    return JSONResponse(content={"Error":"Redirect to registeration page"},status_code=403)

            elif "principal" in email.lower() or "director" in email.lower() or email.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:

                body = db.query(models.Master).filter(models.Master.email==email).filter(models.Master.password==password).filter(models.Master.status=="Active").first()
                if body:
                    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={"sub": email}, expires_delta=access_token_expires
                    )
                    return JSONResponse(content={"bearer": access_token,"Profile":"Master"},status_code=200)
                else:
                    return JSONResponse(content={"Error":"Create your account first"},status_code=403)



            elif "placement" in email.lower() :
                body=db.query(models.Placement_signup).filter(models.Placement_signup.email==email).filter(models.Placement_signup.password==password).filter(models.Placement_signup.status=="Active").first()
                if body:
                    user_data=db.query(models.placement_coordinator).filter(models.placement_coordinator.email==email).filter(models.placement_coordinator.status=="Active").first()
                    if user_data:
                        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                        access_token = create_access_token(
                            data={"sub": email}, expires_delta=access_token_expires
                        )
                        return JSONResponse(content={"bearer": access_token,"Profile":"Placement"},status_code=200)
                    else:
                        return JSONResponse(content={"Redirect":"Complete the registeration process"},status_code=303)
                else:
                    return JSONResponse(content={"Error":"Redirect to registeration page"},status_code=403)
            
            
            elif not any(char.isdigit() for char in email):
                body=db.query(models.Staff_signup).filter(models.Staff_signup.email==email).filter(models.Staff_signup.password==password).filter(models.Placement_signup.status=="Active").first()
                user_data=db.query()
                if body:
                    user_data=db.query(models.staff_coordinator).filter(models.staff_coordinator.email==email).filter(models.staff_coordinator.status=="Active").first()
                    # print(user_data)
                    if user_data:
                        access_token_expires = timedelta(hours=1)
                        access_token = create_access_token(
                            data={"sub": email}, expires_delta=access_token_expires
                        )
                        return JSONResponse(content= {"bearer": access_token,"Profile":"Staff"},status_code=200)
                    else:
                        return JSONResponse(content={"Redirect":"Complete the registeration process"},status_code=303)
                else:
                    return JSONResponse(content={"Error":"Redirect to registeration page"},status_code=403)
            
            else:
                body=db.query(models.Signup).filter(models.Signup.email==email).filter(models.Signup.password==password).filter(models.Signup.status=="Active").first()
                print(body)
                if body:
                    user_data=db.query(models.ApprovalRegisteration).filter(models.ApprovalRegisteration.email==email).filter(models.ApprovalRegisteration.status=="Active").first();
                    user_data1=db.query(models.Registeration).filter(models.Registeration.email==email).filter(models.Registeration.status=="Active").first();

                    # user_data=db.query(models.Registeration).filter(models.Registeration.email==email).filter(models.Registeration.status=="Active").first();
                    # print(user_data)
                    if user_data or user_data1:
                        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                        access_token = create_access_token(
                                data={"sub": email}, expires_delta=access_token_expires
                            )
                        return JSONResponse(content= {"bearer": access_token,"Profile":"Student"},status_code=200)
                    else:
                        return JSONResponse(content={"Redirect":"Redirect to registeration page"},status_code=303)
                else:
                    return JSONResponse(content={"Error":"Create your account first"},status_code=403)
        else:
            return JSONResponse(content={"Error":"Request data are not fullfilled"},status_code=400)
        
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
    


# Getting home Datas
    
@app.get('/home')
async def home(request:Request,db:Session=Depends(get_db),current_user: str = Depends(get_current_user)):
    try:
           company_data=db.query(models.Addcompany).filter(models.Addcompany.status=="Active").all()
           company_data=jsonable_encoder(company_data)
           return JSONResponse(content={"companyData":company_data},status_code=200)
    
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


#adding upcoming company in the home page
    
@app.post('/addcompany')
async def addcompany(request:Request,db:Session=Depends(get_db),current_user: str = Depends(get_current_user)):
    try: 
            data=await request.json()
            image_url=data.get('image_url')
            company_url=data.get('company_url')
            if "principal" in current_user.lower() or "director" in current_user.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
                checkPriority=db.query(models.Master.priority).filter(models.Master.email==current_user).filter(models.Master.status=="ACTIVE").first()
                if checkPriority=="view":
                   return JSONResponse(content={"Error":"Account does not have the privilege"},status_code=400)
                else:
                   body=models.Addcompany(image_url=image_url,company_url=company_url,created_by=current_user,status="Active")
                   db.add(body)
                   db.commit()
                   return JSONResponse(content={"message":"Upcoming Company added successfully"},status_code=200)
            
            elif 'placement' in current_user.lower():    
                data=db.query(models.placement_coordinator).filter(models.placement_coordinator.email==current_user).filter(models.placement_coordinator.status=="ACTIVE").first()
                if data:
                    body=models.Addcompany(image_url=image_url,company_url=company_url,created_by=current_user,status="Active")
                    db.add(body)
                    db.commit()
                    return JSONResponse(content={"message":"Upcoming Company added successfully"},status_code=200)
                else:
                    return JSONResponse(content={"error":"User Datas are not found"},status_code=400)
            
            else:
                return JSONResponse(content={"Error":"Account does not have the privilege"},status_code=400) 
    
    
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
    


# adding placement information to the db
@app.post('/placementinfo')
async def placementinfo(request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
                data=await request.json()
                companyName = data.get('companyName')
                driveDate = data.get('driveDate')
                sslc = data.get('SSLC', ' ')
                hsc = data.get("HSC", ' ')
                CGPA = data.get('CGPA', ' ')
                rounds = data.get('rounds', [])
                first_round = rounds[0] if rounds else ' ' 
                second_round = rounds[1]  if len(rounds) > 1 else ' ' 
                third_round = rounds[2]  if len(rounds) > 2 else ' ' 
                fourth_round = rounds[3]  if len(rounds) > 3 else ' ' 
                fifth_round = rounds[4]   if len(rounds) > 4 else ' ' 
                sixth_round = rounds[5]  if len(rounds) > 5 else ' ' 
                ctcPackage = data.get('ctcPackage')
                venue = data.get('venue')
                stream = data.get('stream')
                if "principal" in current_user.lower() or "director" in current_user.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
                        checkPriority=db.query(models.Master.priority).filter(models.Master.email==current_user).filter(models.Master.status=="ACTIVE").first()
                        if checkPriority=="view":
                              return JSONResponse(content={"Error":"Account does not have the privilege"},status_code=400)
                        else:
                                data = models.Placementinfo(
                                companyName=companyName,
                                driveDate=driveDate,
                                ctcPackage=ctcPackage,
                                venue=venue,
                                stream=stream,
                                SSLC=sslc,
                                HSC=hsc,
                                CGPA=CGPA,
                                round1=first_round,
                                round2=second_round,
                                round3=third_round,
                                round4=fourth_round,
                                round5=fifth_round,
                                round6=sixth_round,
                                status="Active",
                                created_by=current_user
                            )
                                db.add(data)
                                db.commit()
                                return JSONResponse(content={"message":"Upcoming Company added successfully"},status_code=200)
        
                elif 'placement' in current_user.lower():    
                        data=db.query(models.placement_coordinator).filter(models.placement_coordinator.email==current_user).filter(models.placement_coordinator.status=="ACTIVE").first()
                        if data:
                                data = models.Placementinfo(
                                    companyName=companyName,
                                    driveDate=driveDate,
                                    ctcPackage=ctcPackage,
                                    venue=venue,
                                    stream=stream,
                                    SSLC=sslc,
                                    HSC=hsc,
                                    CGPA=CGPA,
                                    round1=first_round,
                                    round2=second_round,
                                    round3=third_round,
                                    round4=fourth_round,
                                    round5=fifth_round,
                                    round6=sixth_round,
                                    status="Active",
                                    created_by=current_user
                                )
                                db.add(data)
                                db.commit()
                                return JSONResponse(content={"message":"Upcoming Company added successfully"},status_code=200)
                        else:
                            return JSONResponse(content={"error":"User Datas are not found"},status_code=400)

                else:
                    return JSONResponse(content={"Error":"Account does not have the privilege"},status_code=400) 
        
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)



# sending placement information to the recipientant

@app.post('/placementemail')
async def placementemail(request:Request,db:Session=Depends(get_db),current_user:str=Depends(get_current_user)):
    try:
                    data=await request.json()
                    recipientEmail = data.get('to')
                    companyName = data.get('companyName')
                    driveDate = data.get('driveDate')
                    sslc = data.get('SSLC', None)
                    hsc = data.get("HSC", None)
                    CGPA = data.get('CGPA', None)
                    rounds = data.get('rounds', [])
                    ctcPackage = data.get('ctcPackage')
                    venue = data.get('venue')
                    stream = data.get('stream')
                    recipient_emails_list = recipientEmail.split(',')
                    to_list = [{"email": email.strip()} for email in recipient_emails_list]
                    to_list = list(to_list)
                    print(to_list)

                    rounds_content = ""
                    if rounds:
                        rounds_content += "<h2 style='color: #0263c2; font-size: 24px;'>Rounds</h2>"
                        for i, round_data in enumerate(rounds, 1):
                            rounds_content += f"<p style='font-size: 18px;'>Round {i}: {round_data}</p>"

                    sslc_content = "NO SSLC mark is needed" if not sslc else f"SSLC: {sslc}"
                    hsc_content = "NO HSC mark is needed" if not hsc else f"HSC: {hsc}"
                    CGPA_content = "No CGPA is specified" if not CGPA else f"CGPA: {CGPA}"

                    email_data = {
                        "sender": {"name": "NEC Placement", "email": "2015053@nec.edu.in"},
                        "to": [{"email": email_dict['email']} for email_dict in to_list],
                        "subject": f"Unleash Your Potential with {companyName}: Exclusive Recruitment Drive on {driveDate}!",
                        "htmlContent": f"""<html><body style="font-family: 'Arial', sans-serif;font">
                            <h2 style="color: #0263c2; font-size: 24px;">Dear Sir/mam,</h2>
                            <p style="font-size: 18px;">
                                Prepare to embark on an exhilarating career journey with {companyName} as we unveil our highly anticipated recruitment drive scheduled for <strong>{driveDate}</strong>!
                            </p>

                            <p style="font-size: 18px;">
                                Calling all talented individuals from the {stream} stream! This is your golden opportunity to join a dynamic team at {companyName}, where innovation and excellence converge.
                            </p>

                            <p style="font-size: 18px;">
                                We are on the lookout for ambitious candidates who meet the eligibility criteria of {sslc_content}, {hsc_content}, and {CGPA_content} to showcase their skills and be part of our success story. Seize the chance to interact with our esteemed hiring team and demonstrate your capabilities at the recruitment event hosted at {venue}, providing the perfect backdrop for your career aspirations.
                            </p>

                            {rounds_content}

                            <p style="font-size: 18px;">
                                At {companyName}, we believe in rewarding talent, and successful candidates stand to benefit from an attractive CTC package of <strong>{ctcPackage}</strong>. This is your moment to elevate your career and make a significant impact.
                            </p>

                            <p style="font-size: 18px;">
                                Don't miss out on this incredible opportunity to shape your future with {companyName}. Mark your calendars for <strong>{driveDate}</strong> and take the first step towards a fulfilling and rewarding career!
                            </p>

                            <p style="font-weight: bold;font-size: 18px;">Best Regards,</p>
                            <p>NEC Placement</p>
                            </body></html>"""
                    }
                    headers = {
                            'Content-Type': 'application/json',
                            'api-key': api_key
                    }
                    if "principal" in current_user.lower() or "director" in current_user.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
                            checkPriority=db.query(models.Master.priority).filter(models.Master.email==current_user).filter(models.Master.status=="ACTIVE").first()
                            if checkPriority=="view":
                                return JSONResponse(content={"Error":"Account does not have the privilege"},status_code=400)
                            else:
                                response = requests.post(url, headers=headers, json=email_data)
                                if(response.status_code==201):
                                    return JSONResponse(content={"message": "Email Sent Successfully"}, status_code=200)
                                
                                else:
                                    print(response.content)
                                    return JSONResponse(content={"error": "Due to network issues, the email was not sent successfully"},status_code=503)
              
                    elif 'placement' in current_user.lower():    
                        data=db.query(models.placement_coordinator).filter(models.placement_coordinator.email==current_user).filter(models.placement_coordinator.status=="ACTIVE").first()
                        if data:
                                response = requests.post(url, headers=headers, json=email_data)
                                if(response.status_code==201):
                                    return JSONResponse(content={"message": "Email Sent Successfully"}, status_code=200)
                                
                                else:
                                    print(response.content)
                                    return JSONResponse(content={"error": "Due to network issues, the email was not sent successfully"},status_code=503)

                    else:
                        return JSONResponse(content={"Error":"Account does not have the privilege"},status_code=400) 

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
    



# Get the student data in student filter page
@app.get('/studentdata')
async def studentdata(request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        if "principal" in current_user.lower() or "director" in current_user.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
                checkPriority=db.query(models.Master.priority).filter(models.Master.email==current_user).filter(models.Master.status=="ACTIVE").first()
                if checkPriority=="view":
                   return JSONResponse(content={"Error":"Account does not have the privilege"},status_code=400)
                else:
                    student_data = db.query(models.Registeration).filter(models.Registeration.placement_status=="").filter(models.Registeration.status == "Active").all()
                    if student_data:    
                        student_data=jsonable_encoder(student_data)
                        return JSONResponse(content={"Student Datas":student_data},status_code=200)
                    else:
                        return JSONResponse(content={"error":"No Data Found"},status_code=200)
            
        elif 'placement' in current_user.lower():    
                data=db.query(models.placement_coordinator).filter(models.placement_coordinator.email==current_user).filter(models.placement_coordinator.status=="ACTIVE").first()
                if data:
                    student_data = db.query(models.Registeration).filter(models.Registeration.placement_status=="").filter(models.Registeration.status == "Active").all()
                    student_data=jsonable_encoder(student_data)
                    return JSONResponse(content={"Student Datas":student_data},status_code=200)
                else:
                    return JSONResponse(content={"error":"No Data Found"},status_code=400)

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# updateStudentStatus
@app.post('/updateStudentStatus/{id}/{status}')
async def updateStudentStatus(id: int, status: str, request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        if "principal" in current_user.lower() or "director" in current_user.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
                checkPriority=db.query(models.Master.priority).filter(models.Master.email==current_user).filter(models.Master.status=="ACTIVE").first()
                if checkPriority=="view":
                   return JSONResponse(content={"Error":"Account does not have the privilege"},status_code=400)
                else:
                    student = db.query(models.Registeration).filter(models.Registeration.id == id).first()
                    if student:
                        db.query(models.Registeration).filter(models.Registeration.id == id).update({"status": status})
                        db.commit()
                        return JSONResponse(content={"message": "Status changed successfully"}, status_code=200)
                    else:
                        return JSONResponse(content={"error": "Student not found"}, status_code=404)
            
        elif 'placement' in current_user.lower():    
                data=db.query(models.placement_coordinator).filter(models.placement_coordinator.email==current_user).filter(models.placement_coordinator.status=="ACTIVE").first()
                if data:
                   student = db.query(models.Registeration).filter(models.Registeration.id == id).first()
                   if student:
                        db.query(models.Registeration).filter(models.Registeration.id == id).update({"status": status})
                        db.commit()
                        return JSONResponse(content={"message": "Status changed successfully"}, status_code=200)
                   else:
                        return JSONResponse(content={"error": "Student not found"}, status_code=404)
                else:
                    return JSONResponse(content={"error":"No Data Found"},status_code=400)

        # Check if the current user is authorized
        body = db.query(models.Placement_signup).filter(models.Placement_signup.email == current_user, models.Placement_signup.status == "Active").first()
        if body:
            student = db.query(models.Registeration).filter(models.Registeration.id == id).first()
            if student:
                db.query(models.Registeration).filter(models.Registeration.id == id).update({"status": status})
                db.commit()
                return JSONResponse(content={"message": "Status changed successfully"}, status_code=200)
            else:
                return JSONResponse(content={"error": "Student not found"}, status_code=404)
        else:
            return JSONResponse(content={"error": "Unauthorized access"}, status_code=403)

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
     

# User Profile page for both staffs and user
# get the user profile
    
@app.get('/getprofile')
async def getprofile(request:Request,db:Session=Depends(get_db),current_user:str=Depends(get_current_user)):
    
    try:
            if "principal" in current_user.lower() or "director" in current_user.lower() or current_user.lower() in ["kgs@nec.edu.in", "placement@nec.edu.in"]:
                # user_data=db.query(models.Registeration).filter(models.Registeration.email==current_user).filter(models.Registeration.status=="Active").first()
                company_info=db.query(models.Placementinfo).filter(models.Placementinfo.status=="Active").all()
                # return JSONResponse(content={'user_data':user_data,'company_info':company_info,},status_code=200)
                company_info=jsonable_encoder(company_info)
                return JSONResponse(content={'company_info':company_info},status_code=200)
            elif 'placement' in current_user.lower():
                body=db.query(models.Placement_signup).filter(models.Placement_signup.email==current_user).filter(models.Placement_signup.status=="Active").first()
                if body:
                    user_data=db.query(models.placement_coordinator).filter(models.placement_coordinator.email==current_user).filter(models.placement_coordinator.status=="Active").first()
                    user_data=jsonable_encoder(user_data)
                    return JSONResponse(content={'user_data':user_data},status_code=200)
                else:
                    return JSONResponse(content={"error":"No data Found"},status_code=403)

            
            elif  not any(char.isdigit() for char in current_user):
                body=db.query(models.Staff_signup).filter(models.Staff_signup.email==current_user).filter(models.Staff_signup.status=="Active").first()
                if body:
                    user_data=db.query(models.staff_coordinator).filter(models.staff_coordinator.email==current_user).filter(models.staff_coordinator.status=="Active").first()
                    user_data=jsonable_encoder(user_data)
                    return JSONResponse(content={'user_data':user_data},status_code=200)
                else:
                    return JSONResponse(content={"error":"No data Found"},status_code=403)    
                            
            
            else:
                body=db.query(models.Signup).filter(models.Signup.email==current_user).filter(models.Signup.status=="Active").first()
                if body:
                    user_data=db.query(models.Registeration).filter(models.Registeration.email==current_user).filter(models.Registeration.status=="Active").first()
                    company_info=db.query(models.Placementinfo).filter(models.Placementinfo.status=="Active").all()
                    # programmingportals=db.query(models.ProgrammingPortals).filter(models.ProgrammingPortals.status=="Active").all()
                    # 'programmingportals':programmingportals
                    return JSONResponse(content={'user_data':user_data,'company_info':company_info},status_code=200)
                else:
                    return JSONResponse(content={"error":"No data Found"},status_code=403)
    
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# updateprofile for all the students and staffs
    

@app.post('/updateprofile')
async def updateprofile(request:Request,db:Session=Depends(get_db),current_user:str=Depends(get_current_user)):
    try:
        if 'placement' in current_user.lower():
            data=await request.json()
            body=db.query(models.Placement_signup).filter(models.Placement_signup.email==current_user).filter(models.Placement_signup.status=="Active").first()
            if body:
               name=data.get('name')
               department=data.get('department')
               phone=data.get('phoone')
               db.query(models.placement_coordinator).filter(models.placement_coordinator.email==current_user).filter(models.placement_coordinator.status=="Active").update({"name":name,"department":department,"phone":phone})
               db.commit()
            else:
                return JSONResponse(content={"error":"Unauthorised access"},status_code=403)
        else:
            data=await request.form()
            body=db.query(models.Signup).filter(models.Signup.email==current_user).filter(models.Signup.status=="Active").first()
            if body:
                        regno=data.get('regno')
                        name=data.get('name')
                        department=data.get('department')
                        email=data.get('email')
                        phone_Number=data.get('phone_Number')
                        pan_No=data.get('pan_No')
                        Aadhar_No=data.get('Aadhar_No')
                        Gender=data.get('Gender')
                        DOB=data.get('DOB')
                        personal_Email=data.get('personal_Email')
                        caste=data.get('caste')
                        religion=data.get('religion')
                        marital_Status=data.get('marital_Status')
                        Father_Name=data.get('Father_Name')
                        Mother_Name=data.get('Mother_Name')
                        Father_Occupation=data.get('Father_Occupation')
                        Mother_Occupation=data.get('Mother_Occupation')
                        Father_Phone_no=data.get('Father_Phone_no')
                        Mother_Phone_no=data.get('Mother_Phone_no')
                        address=data.get('address')
                        permant_address=data.get('permant_address')
                        SSLC_school_Name=data.get('SSLC_school_Name')
                        SSLC_board_Of_Studies=data.get('SSLC_board_Of_Studies')
                        SSLC_Mark=data.get('SSLC_Mark')
                        SSLC_Percentage=data.get('SSLC_Percentage')
                        SSLC_YOP=data.get('SSLC_YOP')
                        HSC_school_Name=data.get('HSC_school_Name')
                        HSC_board_Of_Studies=data.get('HSC_board_Of_Studies')
                        HSC_Mark=data.get('HSC_Mark')
                        HSC_Percentage=data.get('HSC_Percentage')
                        HSC_YOP=data.get('HSC_YOP')
                        tutor_name=data.get('tutor_name')
                        diploma_college_name=data.get('diploma_college_name')
                        diploma_Mark=data.get('diploma_Mark')
                        diploma_Percentage=data.get('diploma_Percentage')
                        diploma_YOP=data.get('diploma_YOP')
                        college_CGPA=data.get('college_CGPA')
                        College_YOP=data.get('College_YOP')
                        history_Of_Arrears=data.get('history_Of_Arrears')
                        no_Of_History_of_Arrears=data.get('no_Of_History_of_Arrears')
                        standing_Arrears=data.get('standing_Arrears')
                        no_Of_Standing_arrears=data.get('no_Of_Standing_arrears')
                        types_Of_companies=data.get('types_Of_companies')
                        aadhar_Card=data.get('aadhar_Card')
                        pan_Card=data.get('pan_Card')
                        photo=data.get('photo')
                        certificates=data.get('certificates')
                        resume=data.get('resume')
                        tutor_email=data.get('tutor_email')
                        passport=data.get('passport')
                        pancard_name=data.get('pancard_name')
                        aadharcard_name=data.get('aadharcard_name')
                        photo_name=data.get('photo_name')
                        resume_name=data.get('resume_name')
                        certificates_name=data.get('certificates_name')
                        passport_name=data.get('passport_name')
                        extention1 = pancard_name.split('.')[-1]
                        extention2 = aadharcard_name.split('.')[-1]
                        extention3 = photo_name.split('.')[-1]
                        extention4 = resume_name.split('.')[-1]
                        extention5 = certificates_name.split('.')[-1]
                        extention6=passport_name.split('.')[-1]
                        upload_aadhar_folder = "./aadhar_Card"
                        upload_pan_folder="./pan_Card"
                        upload_photo_folder="./photo"
                        upload_certificates_folder="./certificates"
                        upload_resume_folder="./resume"
                        upload_passport_folder="./passport"
                        if not os.path.exists(upload_aadhar_folder):
                            os.makedirs(upload_aadhar_folder)    
                        if not os.path.exists(upload_pan_folder):
                            os.makedirs(upload_pan_folder)
                        if not os.path.exists(upload_photo_folder):
                            os.makedirs(upload_photo_folder)
                        if not os.path.exists(upload_certificates_folder):
                            os.makedirs(upload_certificates_folder)
                        if not os.path.exists(upload_resume_folder):
                            os.makedirs(upload_resume_folder) 
                        if not os.path.exists(upload_passport_folder):
                            os.makedirs(upload_passport_folder) 
                        print(extention1)
                        token_image1 = str(uuid.uuid4()) + '.' + str(extention1)
                        token_image2 = str(uuid.uuid4()) + '.' + str(extention2)
                        token_image3 = str(uuid.uuid4()) + '.' + str(extention3)
                        token_image4 = str(uuid.uuid4()) + '.' + str(extention4)
                        token_image5 = str(uuid.uuid4()) + '.' + str(extention5)
                        token_image6=str(uuid.uuid4()) + '.' + str(extention6)
                        file_location1 =  f"{upload_aadhar_folder}/{token_image1}"
                        file_location2 =  f"{upload_pan_folder}/{token_image2}"
                        file_location3 =  f"{upload_photo_folder}/{token_image3}"
                        file_location4 =  f"{upload_certificates_folder}/{token_image4}"
                        file_location5 =  f"{upload_resume_folder}/{token_image5}"
                        file_location6 =  f"{upload_passport_folder}/{token_image6}"
                        with open(file_location1, 'wb+') as file_object:
                                shutil.copyfileobj(aadhar_Card.file, file_object)
                        with open(file_location2, 'wb+') as file_object:
                                shutil.copyfileobj(pan_Card.file, file_object)
                        with open(file_location3, 'wb+') as file_object:
                                shutil.copyfileobj(photo.file, file_object)
                        with open(file_location4, 'wb+') as file_object:
                                shutil.copyfileobj(certificates.file, file_object)
                        with open(file_location5, 'wb+') as file_object:
                                shutil.copyfileobj(resume.file, file_object)
                        with open(file_location6, 'wb+') as file_object:
                                shutil.copyfileobj(passport.file, file_object)
                        db.query(models.Registeration).filter(models.Registeration.email==current_user).filter(models.Registeration.status=="Active").update({
                            "regno":regno,
                            "name":name,
                            "department":department,
                            "email":email,
                            "phone_Number":phone_Number,
                            "pan_No":pan_No,
                            "Aadhar_No":Aadhar_No,
                            "Gender":Gender,
                            "DOB":DOB,
                            "tutor_email":tutor_email,
                            "tutor_name":tutor_name,
                            "personal_Email":personal_Email,
                            "caste":caste,
                            "religion":religion,
                            "marital_Status":marital_Status,
                            "Father_Name":Father_Name,
                            "Mother_Name":Mother_Name,
                            "Father_Occupation":Father_Occupation,
                            "Mother_Occupation":Mother_Occupation,
                            "Father_Phone_no":Father_Phone_no,
                            "Mother_Phone_no":Mother_Phone_no,
                            "address":address,
                            "permant_address":permant_address,
                            "SSLC_school_Name":SSLC_school_Name,
                            "SSLC_board_Of_Studies":SSLC_board_Of_Studies,
                            "SSLC_Mark":SSLC_Mark,
                            "SSLC_Percentage":SSLC_Percentage,
                            "SSLC_YOP":SSLC_YOP,
                            "HSC_school_Name":HSC_school_Name,
                            "HSC_board_Of_Studies":HSC_board_Of_Studies,
                            "HSC_Mark":HSC_Mark,
                            "HSC_Percentage":HSC_Percentage,
                            "HSC_YOP":HSC_YOP,
                            "diploma_college_name":diploma_college_name,
                            "diploma_Mark":diploma_Mark,
                            "diploma_YOP":diploma_YOP,
                            "diploma_Percentage":diploma_Percentage,
                            "college_CGPA":college_CGPA,
                            "College_YOP":College_YOP,
                            "history_Of_Arrears":history_Of_Arrears,
                            "no_Of_History_of_Arrears":no_Of_History_of_Arrears,
                            "standing_Arrears":standing_Arrears,
                            "no_Of_Standing_arrears":no_Of_Standing_arrears,
                            "types_Of_companies":types_Of_companies,
                            "aadhar_Card":token_image1,
                            "pan_Card":token_image2,
                            "photo":token_image3,
                            "certificates":token_image4,
                            "resume":token_image5,
                            "passport":token_image6,
                        })
                        db.commit()
                        return JSONResponse(content={"message":"Profile updated successfully"},status_code=200)    
            else:
                return JSONResponse(content={"Error":"Extension is Not in the correct format"},status_code=400)

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# This datas are used for getting access form
# return the specific user data

@app.get('/getaccess')
async def getaccess(request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        body = db.query(models.Registeration.email, models.Registeration.department).filter(models.Registeration.email == current_user, models.Registeration.status == "Active").first()
        if body:
            department = db.query(models.placement_coordinator.email).join(models.Registeration, models.Registeration.department == models.placement_coordinator.department).filter(models.Registeration.email == current_user, models.placement_coordinator.status == "Active").first()
            user_data=jsonable_encoder(body)
            placement_data=jsonable_encoder(department)
            return JSONResponse(content={"user": user_data, "placement": placement_data}, status_code=200)
        else:
            return JSONResponse(content={"error": "No user Found"}, status_code=400)
    
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# submitting the Getting access data


@app.post('/getaccessdata')
async def getaccessdata(request:Request,db:Session=Depends(get_db),current_user:str=Depends(get_current_user)):
    try:
      data=await request.json()
      email=data.get('email')
      department=data.get('department')
      placement_email=data.get('adminemail')
      subject=data.get('subject')
      if email and department and placement_email and subject:
          body=models.Getaccess(email=email,department=department,placement_email=placement_email,subject=subject,status="Active")
          db.add(body)
          db.commit()
          return JSONResponse(content={"message":"Data are stored successfully"},status_code=200)
      else:
          return JSONResponse(content={"message":"Datas are incomplete"},status_code=400)
    
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)



# Not Use because we created masters table

# @app.get('/getaccessapproval')
# async def getaccess(request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
#     try:
#         body = db.query(models.\).filter(models.placement_coordinator.email == current_user).filter(models.placement_coordinator.status == "Active").first()
#         print(body)
#         if body:
#             requestData = db.query(models.Getaccess).filter(models.Getaccess.placement_email==current_user).filter(models.Getaccess.status == "Active").all()
#             # requestData_json=jsonable_encoder(requestData)
#             return JSONResponse(content={"Approval Request": requestData}, status_code=200)
#         else:
#             return JSONResponse(content={"error": "No user Found"}, status_code=400)
    
#     except HTTPException as e:
#         return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
#     except Exception as e:
#         print(e)
#         return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)

# getdata for placed students
# Find out the Route where Used



@app.post('/getdata')
async def getdata(request:Request,db:Session=Depends(get_db),current_user:str=Depends(get_current_user)):
    try:
        data=await request.json()
        print(data)
        email=data.get('email')
        body=db.query(models.Registeration).filter(models.Registeration.email==email).filter(models.Registeration.status=="Active").first()
        # body=db.query(models.ApprovalRegisteration).filter(models.ApprovalRegisteration.email==email).filter(models.ApprovalRegisteration.status=="Active").first()
        print(body)
        if body:
             return body
        else:
            return JSONResponse(content={"Error":"User Not found"},status_code=400)

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
    

# Before submit the form Fetch the Datas from the user

@app.get('/getuserplacedData')
async def getuserplacedData(request:Request,db:Session=Depends(get_db),current_user:str=Depends(get_current_user)):
    try:
        if current_user.lower() in "placement@nec.edu.in":  
            data=await request.json()
            email=data.get('email')
            body=db.query(models.Registeration).filter(models.Registeration.email==email).filter(models.Registeration.status=="Active").first()
            if body:
                 body=jsonable_encoder(body)
                 return JSONResponse(content={"user":body},status_code=200)
            else:
                return JSONResponse(content={"Error":"User Not found"},status_code=400)  

        else:    
            body=db.query(models.Registeration).filter(models.Registeration.email==current_user).filter(models.Registeration.status=="Active").first()
            if body:
                    return body
            else:
                return JSONResponse(content={"Error":"User Not found"},status_code=400)   
    
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)



# placed data stored route
    
@app.post('/placeddata')
async def placeddata(request:Request,db:Session=Depends(get_db),current_user:str=Depends(get_current_user)):
    try:
       data=await request.form()
       email=data.get('email')
       content_type=request.headers.get('content_type')
       body=db.query(models.Registeration).filter(models.Registeration.email==email).filter(models.Registeration.status=="Active").first()
       if body:
            email=data.get('email')
            name=data.get('name')
            department=data.get('department')
            phoneno=data.get('phoneno')
            dob=data.get('dob')
            address=data.get('address')
            companyname=data.get('companyname')
            modeofhiring=data.get('modeofhiring')
            package=data.get('package')
            location=data.get('location')
            # Files
            declaration=data.get('declaration')
            declaration_name=data.get('declaration_name')
            offerletter=data.get('offerletter')
            offerletter_name=data.get('offerletter_name')
            internletter=data.get('internletter')
            internletter_name=data.get('internletter_name')
            feedback=data.get('feedback')
            feedback_name=data.get('feedback_name')
            extention1 = declaration_name.split('/')[-1]
            extention2 = offerletter_name.split('/')[-1]
            extention3 = internletter_name.split('/')[-1]
            extention4 = feedback_name.split('/')[-1]
            upload_declaration_folder = "./declaration"
            upload_offerletter_folder="./offerletter"
            upload_internletter_folder="./internletter"
            upload_feedback_folder="./feedback"
            if not os.path.exists(upload_declaration_folder):
                    os.makedirs(upload_declaration_folder)    
            if not os.path.exists(upload_offerletter_folder):
                    os.makedirs(upload_offerletter_folder)
            if not os.path.exists(upload_internletter_folder):
                    os.makedirs(upload_internletter_folder)
            if not os.path.exists(upload_feedback_folder):
                    os.makedirs(upload_feedback_folder)
            if extention1 != 'application/octet-stream' and extention2 != 'application/octet-stream' and extention3 != 'application/octet-stream' and extention4 != 'application/octet-stream':
                token_image1 = str(uuid.uuid4()) + '.' + str(extention1)
                token_image2 = str(uuid.uuid4()) + '.' + str(extention2)
                token_image3 = str(uuid.uuid4()) + '.' + str(extention3)
                token_image4 = str(uuid.uuid4()) + '.' + str(extention4)
                file_location1 =  f"{upload_declaration_folder}/{token_image1}"
                file_location2 =  f"{upload_offerletter_folder}/{token_image2}"
                file_location3 =  f"{upload_internletter_folder}/{token_image3}"
                file_location4 =  f"{upload_feedback_folder}/{token_image4}"
                with open(file_location1, 'wb+') as file_object:
                            shutil.copyfileobj(declaration.file, file_object)
                with open(file_location2, 'wb+') as file_object:
                            shutil.copyfileobj(offerletter.file, file_object)
                with open(file_location3, 'wb+') as file_object:
                            shutil.copyfileobj(internletter.file, file_object)
                with open(file_location4, 'wb+') as file_object:
                            shutil.copyfileobj(feedback.file, file_object)

                placeddata=models.Placeddata(email=email,name=name,department=department,phoneno=phoneno,dob=dob,address=address,companyname=companyname,modeofhiring=modeofhiring,package=package,location=location,declaration=token_image1,offerletter=token_image2,internletter=token_image3,feedback=token_image4,created_by=current_user,status="Active")
                db.query(models.Registeration).filter(models.Registeration.email == email).filter(models.Registeration.status=="Active").update({"placement_status": "Placed"})
                db.add(placeddata)
                db.commit()
                return JSONResponse(content={"message":"Datas are submitted successfully"},status_code=200)          
            
            else:
                 return JSONResponse(content={"Error":"Extension is Not in the correct format"},status_code=400)
       else:
            return JSONResponse(content={"Error":"User Not found"},status_code=400)

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
    


# get their department student data and get their ward student list and get the masters user view the all the students data
    #incomplete
@app.get('/getStudentData')
async def getStudentData(request: Request, db: Session = Depends(get_db),current_user:str=Depends(get_current_user)):
    try:
            if current_user.lower() in ["principal", "director", "kgs@nec.edu.in", "placement@nec.edu.in"]:
                body=db.query(models.Registeration).filter(models.Registeration.status=="ACTIVE").all()
                if body:
                    return JSONResponse(content={"studentsList":body,"count":len(body)},status_code=200)
                else:
                    return JSONResponse(content={"message":"No Data Found"},status_code=100)

            elif "hod" in current_user.lower() or "placement" in current_user.lower():
                print(current_user)
                body=db.query(models.HOD.depname).filter(models.HOD.email==current_user).filter(models.HOD.status=="ACTIVE").first()
                body1=db.query(models.placement_coordinator.department).filter(models.placement_coordinator.email==current_user).filter(models.placement_coordinator.status=="ACTIVE").first()
                if body:
                    newbody=db.query(models.Registeration).filter(models.Registeration.department==body).filter(models.Registeration.status=="ACTIVE").all()
                    if newbody:
                        return JSONResponse(content={"studentsList":newbody,"count":len(newbody)},status_code=200)
                    else:
                        return JSONResponse(content={"message":"No Data Found"},status_code=100)
                elif body1:
                    newbody1=db.query(models.Registeration).filter(models.Registeration.department==body1).filter(models.Registeration.status=="ACTIVE").all()
                    if newbody1:
                        return JSONResponse(content={"studentsList":newbody1,"count":len(newbody1)},status_code=200)
                    else:
                        return JSONResponse(content={"message":"No Data Found"},status_code=200)
                else:
                    return JSONResponse(content={"error":"No details found for the user"},status_code=400)

            else:
                body=db.query(models.staff_coordinator.department).filter(models.staff_coordinator.email==current_user).filter(models.staff_coordinator.status=="ACTIVE").first()
                if body:
                    newbody=db.query(models.Registeration).filter(models.Registeration.department==body[0]).filter(models.Registeration.status=="ACTIVE").all()
                    if newbody:
                        return JSONResponse(content={"studentsList":newbody,"count":len(newbody)},status_code=200)
                    else:
                        return JSONResponse(content={"message":"No Data Found"},status_code=200)          
       
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)     


# Function where HOD sees students data
@app.get('/get_department_students')
async def get_department_students(request: Request, db: Session = Depends(get_db), user_data: str = Depends(decode_token)):
    try:
        department = user_data['department']
        student_data = db.query(models.Registeration).filter(models.Registeration.department == department).all()
        serialized_data = [jsonable_encoder(student) for student in student_data]
        return JSONResponse(content={"data": serialized_data},status_code=200)
   
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
    

# Show companies list to dean
@app.get('/get_company_list')
async def get_company_details(request:Request, db: Session = Depends(get_db), current_user: str = Depends(decode_token)):
    try:
        company_list = db.query(models.Placementinfo).all()
        serialized_data = [jsonable_encoder(company) for company in company_list]
        return  JSONResponse(content={"company_data": serialized_data},status_code=200)
    
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
    
# Show companies round details

@app.get('/get_company_details/{id}')
async def get_company_details(id :int,request:Request,db:Session=Depends(get_db),current_user:str=Depends(decode_token)):
    try:
        company_data = db.query(models.Placementinfo).filter(models.Placementinfo.id == id ).all()
        serialized_data = [jsonable_encoder(company) for company in company_data]
        return  JSONResponse(content={"company_data": serialized_data},status_code=200)
    
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
    
# Show passes students data in a  round
    
@app.get('/get_passed_students/{id}/{round_name}')
async def get_passed_students(id: int, round_name: str, request: Request, db: Session = Depends(get_db), current_user: str = Depends(decode_token)):
    try:
        company_data = db.query(models.RoundCompletionData).filter(models.RoundCompletionData.company_id == id, models.RoundCompletionData.round_name == round_name,models.RoundCompletionData.round_status == "Passed").all()
        student_ids = [data.student_id for data in company_data]
        students = db.query(models.Registeration).filter(models.Registeration.id.in_(student_ids)).all()
        students_data = [{"name": student.name,"department": student.department,"email": student.email,"phone_Number": student.phone_Number,"regno": student.regno} for student in students]
        return JSONResponse(content={"students_data": students_data},status_code=200) 
    
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# Parent Mobile application Signup
@app.post("/parentsignup")
async def parentsignup(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        print(data)
        username=data.get('username')
        phoneno = data.get('phoneno')
        password = data.get('password')

        if username and phoneno and password:
            body=db.query(models.parentSignup).filter(models.parentSignup.phoneNo==phoneno).filter(models.parentSignup.username==username).filter(models.parentSignup.status=="ACTIVE").first()
            newBody=db.query(models.parentSignup).filter(models.parentSignup.username==username).filter(models.parentSignup.status=="ACTIVE").first()
            if body:
                return JSONResponse(content={"error":"Already have an account!!Redirect to Login"},status_code=303)
            elif newBody:
                return JSONResponse(content={"error":"username already used"},status_code=400)
            else:
                parentName=db.query(models.Registeration.Father_Name).filter(models.Registeration.Father_Phone_no==phoneno).filter(models.Registeration.status=="ACTIVE").first()
                print(parentName)
                data=models.parentSignup(username=username,parent_Name=parentName,phoneNo=phoneno,password=password,status="ACTIVE")
                db.add(data)
                db.commit()
                return JSONResponse(content={"message":"Datas are submitted successfully"},status_code=200)          
        else:
            return JSONResponse(content={"error":"Request data is not fullfilled"}, status_code=400)
         
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# parent mobile application login
@app.post("/parentlogin")
async def parentsignup(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        print(data)
        username = data.get('username')
        password = data.get('password')
        if username and password:
            body=db.query(models.parentSignup).filter(models.parentSignup.username==username).filter(models.parentSignup.status=="ACTIVE").first()
            if body:
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                        data={"sub": username}, expires_delta=access_token_expires
                )
                return JSONResponse(content={"message":"Login Successfully","bearer": access_token},status_code=200)
            else:
                return JSONResponse(content={"error":"Create your account first"},status_code=303)          

        else:
            return JSONResponse(content={"error":"Request data is not fullfilled"}, status_code=400)
         
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# parents getting their son/daughter profile of data
@app.get('/getParentProfile')
async def getParentProfile(request:Request,db:Session=Depends(get_db),current_user:str=Depends(get_current_user)):
    
    try:
            body=db.query(models.parentSignup).filter(models.parentSignup.username==current_user).filter(models.parentSignup.status=="Active").first()
            parentPhone=db.query(models.parentSignup.phoneNo).filter(models.parentSignup.username==current_user).filter(models.parentSignup.status=="Active").first()
            # print(parentPhone)
            if body:
            #    print(current_user) 
                parent_phone_number = parentPhone[0] if parentPhone else None
                user_data = db.query(models.Registeration) \
                        .filter(or_(models.Registeration.Father_Phone_no == parent_phone_number,
                                    models.Registeration.Mother_Phone_no == parent_phone_number)) \
                        .filter(models.Registeration.status == "Active") \
                        .first()
            #    company_info=db.query(models.Companies_info).filter(models.Companies_info.status=="Active").all()
            #    programmingportals=db.query(models.ProgrammingPortals).filter(models.ProgrammingPortals.status=="Active").all()
                if user_data:
                    return user_data
                else:
                  return JSONResponse(content={"Message":"No Data Found"},status_code=100)
            #    return {'user_data':user_data,'company_info':company_info,'programmingportals':programmingportals}

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)