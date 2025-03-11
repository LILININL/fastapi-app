from datetime import date, datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import mysql.connector
from typing import List, Optional

app = FastAPI()


def get_db_connection():
    cnx = mysql.connector.connect(
        host='000.00.00.00',
        user='00',
        password='00000',
        database='00'
    )
    return cnx

class Vehicles(BaseModel):
    vehicle_id: Optional[int] = None  
    province: str
    license_plate_img: str
    vehicle_img: str
    resident_id: int
    license_plate: str
    vehicle_type: str
    color: str
    brand: str

class Visitor(BaseModel):
    visitor_id: Optional[int] = None
    name: str
    phone: str
    purpose: str
    vehicle_id: Optional[int] = None
    resident_id: Optional[int] = None

# Resident Model
class Resident(BaseModel):
    resident_id: Optional[int] = None
    user_id: int  
    name: str
    address: Optional[str]
    phone: Optional[str]
    prefix: Optional[str]
    lastname: Optional[str]
    citizen_id: str  

# User Model
class User(BaseModel):
    user_id: Optional[int] = None
    email: EmailStr
    username: str
    password: Optional[str] = None  
    role: str
    created_at: datetime
    
class AccessPermission(BaseModel):
    permission_id: Optional[int] = None
    vehicle_id: int
    resident_id: int
    allowed_gate_id: int
    start_date: date  
    end_date: date  

class IncidentReport(BaseModel):
    incident_id: Optional[int] = None
    description: str
    incident_time: Optional[datetime] = None
    vehicle_id: Optional[int] = None
    security_staff_id: Optional[int] = None
    gate_id: Optional[int] = None
    
class SecurityStaff(BaseModel):
    staff_id: Optional[int] = None
    name: str
    shift_time: str
    phone: str
    gate_id: int

class Gate(BaseModel):
    gate_id: Optional[int] = None
    location: str
    gate_type: str  # 'เข้า' หรือ 'ออก'

class EntryExitLog(BaseModel):
    log_id: Optional[int] = None
    vehicle_id: int
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    gate_id: int

@app.get('/vehicle', response_model=List[Vehicles], tags=["Vehicle"], summary="Fetch All Vehicles Limit 10")
@app.get('/vehicle/{vehicle_id}', response_model=Optional[Vehicles], tags=["Vehicle"], summary="Fetch Vehicle by ID")
def fetch_vehicles(vehicle_id: Optional[int] = None):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    if vehicle_id:
        query = 'SELECT vehicle_id, province, license_plate_img, vehicle_img, resident_id, license_plate, vehicle_type, color, brand FROM Vehicle WHERE vehicle_id = %s'
        cursor.execute(query, (vehicle_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            cnx.close()
            raise HTTPException(status_code=404, detail="Vehicle not found")
        vehicle = {
            'vehicle_id': row[0],
            'province': row[1],
            'license_plate_img': row[2],
            'vehicle_img': row[3],
            'resident_id': row[4],
            'license_plate': row[5],
            'vehicle_type': row[6],
            'color': row[7],
            'brand': row[8]
        }
        cursor.close()
        cnx.close()
        return vehicle
    else:
        query = 'SELECT vehicle_id, province, license_plate_img, vehicle_img, resident_id, license_plate, vehicle_type, color, brand FROM Vehicle LIMIT 10'
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()
        
        vehicles_list = []
        for row in rows:
            vehicles_list.append({
                'vehicle_id': row[0],
                'province': row[1],
                'license_plate_img': row[2],
                'vehicle_img': row[3],
                'resident_id': row[4],
                'license_plate': row[5],
                'vehicle_type': row[6],
                'color': row[7],
                'brand': row[8]
            })
        
        return vehicles_list
    
@app.post('/vehicle', response_model=Vehicles, tags=["Vehicle"], summary="Create a New Vehicle")
def create_vehicle(vehicle: Vehicles):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    if vehicle.vehicle_id:
        query = '''
        INSERT INTO Vehicle (vehicle_id, province, license_plate_img, vehicle_img, resident_id, license_plate, vehicle_type, color, brand)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        values = (
            vehicle.vehicle_id,
            vehicle.province,
            vehicle.license_plate_img,
            vehicle.vehicle_img,
            vehicle.resident_id,
            vehicle.license_plate,
            vehicle.vehicle_type,
            vehicle.color,
            vehicle.brand
        )
    else:
        query = '''
        INSERT INTO Vehicle (province, license_plate_img, vehicle_img, resident_id, license_plate, vehicle_type, color, brand)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        values = (
            vehicle.province,
            vehicle.license_plate_img,
            vehicle.vehicle_img,
            vehicle.resident_id,
            vehicle.license_plate,
            vehicle.vehicle_type,
            vehicle.color,
            vehicle.brand
        )

    try:
        cursor.execute(query, values)
        cnx.commit()  
        if not vehicle.vehicle_id:
            vehicle_id = cursor.lastrowid  
        else:
            vehicle_id = vehicle.vehicle_id
    except mysql.connector.Error as e:
        cnx.rollback()  
        cursor.close()
        cnx.close()
        raise HTTPException(status_code=400, detail=f"Failed to insert vehicle: {str(e)}")

    cursor.close()
    cnx.close()
    
    return {**vehicle.dict(), "vehicle_id": vehicle_id}

@app.put('/vehicle/{vehicle_id}', response_model=Vehicles, tags=["Vehicle"], summary="Update Vehicle Information")
def update_vehicle(vehicle_id: int, vehicle: Vehicles):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    UPDATE Vehicle
    SET province = %s, license_plate_img = %s, vehicle_img = %s, resident_id = %s,
        license_plate = %s, vehicle_type = %s, color = %s, brand = %s
    WHERE vehicle_id = %s
    '''
    
    values = (
        vehicle.province,
        vehicle.license_plate_img,
        vehicle.vehicle_img,
        vehicle.resident_id,
        vehicle.license_plate,
        vehicle.vehicle_type,
        vehicle.color,
        vehicle.brand,
        vehicle_id
    )
    
    cursor.execute(query, values)
    cnx.commit()  
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="Vehicle not found")

    cursor.close()
    cnx.close()

    return {**vehicle.dict(), "vehicle_id": vehicle_id}

@app.delete('/vehicle/{vehicle_id}', tags=["Vehicle"], summary="Delete Vehicle by ID")
def delete_vehicle(vehicle_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'DELETE FROM Vehicle WHERE vehicle_id = %s'
    cursor.execute(query, (vehicle_id,))
    
    cnx.commit()  
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    cursor.close()
    cnx.close()
    
    return {"message": f"Vehicle with id {vehicle_id} has been deleted."}

# Visitor Endpoints
@app.get('/visitor', response_model=List[Visitor], tags=["Visitor"], summary="Fetch All Visitors Limit 10")
@app.get('/visitor/{visitor_id}', response_model=Optional[Visitor], tags=["Visitor"], summary="Fetch Visitor by ID")
def fetch_visitors(visitor_id: Optional[int] = None):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    if visitor_id:
        query = 'SELECT visitor_id, name, phone, purpose, vehicle_id, resident_id FROM Visitor WHERE visitor_id = %s'
        cursor.execute(query, (visitor_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            cnx.close()
            raise HTTPException(status_code=404, detail="Visitor not found")
        visitor = {
            'visitor_id': row[0],
            'name': row[1],
            'phone': row[2],
            'purpose': row[3],
            'vehicle_id': row[4],
            'resident_id': row[5]
        }
        cursor.close()
        cnx.close()
        return visitor
    else:
        query = 'SELECT visitor_id, name, phone, purpose, vehicle_id, resident_id FROM Visitor LIMIT 10'
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()
        
        visitors = []
        for row in rows:
            visitors.append({
                'visitor_id': row[0],
                'name': row[1],
                'phone': row[2],
                'purpose': row[3],
                'vehicle_id': row[4],
                'resident_id': row[5]
            })
        
        return visitors

@app.post('/visitor', response_model=Visitor, tags=["Visitor"], summary="Create a New Visitor")
def create_visitor(visitor: Visitor):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    INSERT INTO Visitor (name, phone, purpose, vehicle_id, resident_id)
    VALUES (%s, %s, %s, %s, %s)
    '''
    
    values = (
        visitor.name,
        visitor.phone,
        visitor.purpose,
        visitor.vehicle_id,
        visitor.resident_id
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    visitor_id = cursor.lastrowid
    cursor.close()
    cnx.close()
    
    return {**visitor.dict(), "visitor_id": visitor_id}

@app.put('/visitor/{visitor_id}', response_model=Visitor, tags=["Visitor"], summary="Update Visitor Information")
def update_visitor(visitor_id: int, visitor: Visitor):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    UPDATE Visitor
    SET name = %s, phone = %s, purpose = %s, vehicle_id = %s, resident_id = %s
    WHERE visitor_id = %s
    '''
    
    values = (
        visitor.name,
        visitor.phone,
        visitor.purpose,
        visitor.vehicle_id,
        visitor.resident_id,
        visitor_id
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบผู้เยี่ยมเยียน")
    
    cursor.close()
    cnx.close()
    
    return {**visitor.dict(), "visitor_id": visitor_id}

@app.delete('/visitor/{visitor_id}', tags=["Visitor"], summary="Delete Visitor by ID")
def delete_visitor(visitor_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'DELETE FROM Visitor WHERE visitor_id = %s'
    cursor.execute(query, (visitor_id,))
    
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบผู้เยี่ยมเยียน")
    
    cursor.close()
    cnx.close()
    
    return {"message": f"ผู้เยี่ยมเยียนที่มี ID {visitor_id} ถูกลบแล้ว"}

# ---------------------- Resident Endpoints ----------------------

@app.get("/resident", response_model=List[Resident], tags=["Resident"], summary="Fetch All Residents Limit 10")
def fetch_residents():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'SELECT resident_id, user_id, name, address, phone, prefix, lastname, citizen_id FROM Resident LIMIT 10'
    cursor.execute(query)
    rows = cursor.fetchall()

    residents = []
    for row in rows:
        residents.append({
            'resident_id': row[0],
            'user_id': row[1],
            'name': row[2],
            'address': row[3],
            'phone': row[4],
            'prefix': row[5],
            'lastname': row[6],
            'citizen_id': row[7]
        })

    cursor.close()
    cnx.close()
    return residents

@app.get("/resident/{resident_id}", response_model=Resident, tags=["Resident"], summary="Fetch Resident by ID")
def get_resident(resident_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'SELECT resident_id, user_id, name, address, phone, prefix, lastname, citizen_id FROM Resident WHERE resident_id = %s'
    cursor.execute(query, (resident_id,))
    row = cursor.fetchone()

    if not row:
        cursor.close()
        cnx.close()
        raise HTTPException(status_code=404, detail="Resident not found")

    resident = {
        'resident_id': row[0],
        'user_id': row[1],
        'name': row[2],
        'address': row[3],
        'phone': row[4],
        'prefix': row[5],
        'lastname': row[6],
        'citizen_id': row[7]
    }

    cursor.close()
    cnx.close()
    return resident

@app.post("/resident", response_model=Resident, tags=["Resident"], summary="Create a New Resident")
def create_resident(resident: Resident):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    # Inserting the new resident with user_id as a foreign key
    query = '''
    INSERT INTO Resident (user_id, name, address, phone, prefix, lastname, citizen_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    values = (
        resident.user_id, 
        resident.name, 
        resident.address, 
        resident.phone, 
        resident.prefix, 
        resident.lastname, 
        resident.citizen_id
    )

    try:
        cursor.execute(query, values)
        cnx.commit()
        resident_id = cursor.lastrowid
    except mysql.connector.Error as e:
        cnx.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating resident: {str(e)}")
    finally:
        cursor.close()
        cnx.close()

    return {**resident.dict(), "resident_id": resident_id}

@app.put("/resident/{resident_id}", response_model=Resident, tags=["Resident"], summary="Update Resident Information")
def update_resident(resident_id: int, resident: Resident):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    UPDATE Resident
    SET user_id = %s, name = %s, address = %s, phone = %s, prefix = %s, lastname = %s, citizen_id = %s
    WHERE resident_id = %s
    '''
    values = (
        resident.user_id,
        resident.name,
        resident.address,
        resident.phone,
        resident.prefix,
        resident.lastname,
        resident.citizen_id,
        resident_id
    )

    cursor.execute(query, values)
    cnx.commit()

    if cursor.rowcount == 0:
        cursor.close()
        cnx.close()
        raise HTTPException(status_code=404, detail="Resident not found")

    cursor.close()
    cnx.close()

    return {**resident.dict(), "resident_id": resident_id}

@app.delete("/resident/{resident_id}", tags=["Resident"], summary="Delete Resident by ID")
def delete_resident(resident_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'DELETE FROM Resident WHERE resident_id = %s'
    cursor.execute(query, (resident_id,))
    cnx.commit()

    if cursor.rowcount == 0:
        cursor.close()
        cnx.close()
        raise HTTPException(status_code=404, detail="Resident not found")

    cursor.close()
    cnx.close()
    return {"message": f"Resident with ID {resident_id} has been deleted."}

# ---------------------- User Endpoints ----------------------
@app.get("/user", response_model=List[User], tags=["User"], summary="Fetch All Users Limit 10")
def fetch_users():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'SELECT user_id, email, username, password, role, created_at FROM User LIMIT 10'
    cursor.execute(query)
    rows = cursor.fetchall()

    users = []
    for row in rows:
        users.append({
            'user_id': row[0],
            'email': row[1],
            'username': row[2],
            'password': row[3],  
            'role': row[4],
            'created_at': row[5]
        })

    cursor.close()
    cnx.close()
    return users

@app.get("/user/{user_id}", response_model=User, tags=["User"], summary="Fetch User by ID")
def get_user(user_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'SELECT user_id, email, username, password, role, created_at FROM User WHERE user_id = %s'
    cursor.execute(query, (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.close()
        cnx.close()
        raise HTTPException(status_code=404, detail="User not found")

    user = {
        'user_id': row[0],
        'email': row[1],
        'username': row[2],
        'password': row[3],  
        'role': row[4],
        'created_at': row[5]
    }

    cursor.close()
    cnx.close()
    return user

@app.post("/user", response_model=User, tags=["User"], summary="Create a New User")
def create_user(user: User):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    # Inserting the new user
    query = '''
    INSERT INTO User (username, password, role, email, created_at)
    VALUES (%s, %s, %s, %s, NOW())
    '''
    values = (user.username, user.password, user.role, user.email)

    try:
        cursor.execute(query, values)
        cnx.commit()
        user_id = cursor.lastrowid
    except mysql.connector.Error as e:
        cnx.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")
    finally:
        cursor.close()
        cnx.close()

    return {**user.dict(), "user_id": user_id}

from datetime import datetime

@app.put("/user/{user_id}", response_model=User, tags=["User"], summary="Update User Information")
def update_user(user_id: int, user: User):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    try:
        # ตรวจสอบว่ามี username ซ้ำหรือไม่
        query_check_username = '''
        SELECT user_id FROM User WHERE username = %s AND user_id != %s
        '''
        cursor.execute(query_check_username, (user.username, user_id))
        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username is already in use by another user")

        # SQL query สำหรับการอัปเดตข้อมูลผู้ใช้ โดยอัปเดต created_at เป็นเวลาปัจจุบัน
        query = '''
        UPDATE User
        SET username = %s, password = %s, role = %s, email = %s, created_at = %s
        WHERE user_id = %s
        '''
        
        # ดึงเวลาปัจจุบัน
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        values = (user.username, user.password, user.role, user.email, current_time, user_id)

        cursor.execute(query, values)
        cnx.commit()

        # ตรวจสอบว่ามีการอัปเดตแถวหรือไม่
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

    except mysql.connector.Error as e:
        cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cursor.close()
        cnx.close()

    # คืนค่า response โดยอัปเดต created_at เป็นเวลาล่าสุด
    return {**user.dict(), "user_id": user_id, "created_at": current_time}



@app.delete("/user/{user_id}", tags=["User"], summary="Delete User by ID")
def delete_user(user_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'DELETE FROM User WHERE user_id = %s'
    cursor.execute(query, (user_id,))
    cnx.commit()

    if cursor.rowcount == 0:
        cursor.close()
        cnx.close()
        raise HTTPException(status_code=404, detail="User not found")

    cursor.close()
    cnx.close()
    return {"message": f"User with ID {user_id} has been deleted."}

# AccessPermission Endpoints
@app.get('/accesspermission', response_model=List[AccessPermission], tags=["AccessPermission"], summary="Fetch All Access Permissions Limit 10")
@app.get('/accesspermission/{permission_id}', response_model=Optional[AccessPermission], tags=["AccessPermission"], summary="Fetch Access Permission by ID")
def fetch_access_permissions(permission_id: Optional[int] = None):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    if permission_id:
        query = 'SELECT permission_id, vehicle_id, resident_id, allowed_gate_id, start_date, end_date FROM AccessPermission WHERE permission_id = %s'
        cursor.execute(query, (permission_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            cnx.close()
            raise HTTPException(status_code=404, detail="Access Permission not found")
        access_permission = {
            'permission_id': row[0],
            'vehicle_id': row[1],
            'resident_id': row[2],
            'allowed_gate_id': row[3],
            'start_date': row[4].strftime('%Y-%m-%d'),
            'end_date': row[5].strftime('%Y-%m-%d')
        }
        cursor.close()
        cnx.close()
        return access_permission
    else:
        query = 'SELECT permission_id, vehicle_id, resident_id, allowed_gate_id, start_date, end_date FROM AccessPermission LIMIT 10'
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()
        
        access_permissions = []
        for row in rows:
            access_permissions.append({
                'permission_id': row[0],
                'vehicle_id': row[1],
                'resident_id': row[2],
                'allowed_gate_id': row[3],
                'start_date': row[4].strftime('%Y-%m-%d'),
                'end_date': row[5].strftime('%Y-%m-%d')
            })
        
        return access_permissions

# POST - สร้าง Access Permission ใหม่
@app.post('/accesspermission', response_model=AccessPermission, tags=["AccessPermission"], summary="Create a New Access Permission")
def create_access_permission(access_permission: AccessPermission):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    INSERT INTO AccessPermission (vehicle_id, resident_id, allowed_gate_id, start_date, end_date)
    VALUES (%s, %s, %s, %s, %s)
    '''
    
    values = (
        access_permission.vehicle_id,
        access_permission.resident_id,
        access_permission.allowed_gate_id,
        access_permission.start_date,  # รับค่าเป็น date ตรงๆ
        access_permission.end_date  # รับค่าเป็น date ตรงๆ
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    permission_id = cursor.lastrowid
    cursor.close()
    cnx.close()
    
    return {**access_permission.dict(), "permission_id": permission_id}

# PUT - อัปเดตข้อมูล Access Permission
@app.put('/accesspermission/{permission_id}', response_model=AccessPermission, tags=["AccessPermission"], summary="Update Access Permission Information")
def update_access_permission(permission_id: int, access_permission: AccessPermission):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    UPDATE AccessPermission
    SET vehicle_id = %s, resident_id = %s, allowed_gate_id = %s, start_date = %s, end_date = %s
    WHERE permission_id = %s
    '''
    
    values = (
        access_permission.vehicle_id,
        access_permission.resident_id,
        access_permission.allowed_gate_id,
        access_permission.start_date,  # รับค่าเป็น date ตรงๆ
        access_permission.end_date,  # รับค่าเป็น date ตรงๆ
        permission_id
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบ Access Permission")
    
    cursor.close()
    cnx.close()
    
    return {**access_permission.dict(), "permission_id": permission_id}

# DELETE - ลบ Access Permission โดยใช้ permission_id
@app.delete('/accesspermission/{permission_id}', tags=["AccessPermission"], summary="Delete Access Permission by ID")
def delete_access_permission(permission_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'DELETE FROM AccessPermission WHERE permission_id = %s'
    cursor.execute(query, (permission_id,))
    
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบ Access Permission")
    
    cursor.close()
    cnx.close()
    
    return {"message": f"Access Permission ที่มี ID {permission_id} ถูกลบแล้ว"}

# IncidentReport Endpoints
@app.get('/incidentreport', response_model=List[IncidentReport], tags=["IncidentReport"], summary="Fetch All Incident Reports Limit 10")
@app.get('/incidentreport/{incident_id}', response_model=Optional[IncidentReport], tags=["IncidentReport"], summary="Fetch Incident Report by ID")
def fetch_incident_reports(incident_id: Optional[int] = None):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    if incident_id:
        query = 'SELECT incident_id, description, incident_time, vehicle_id, security_staff_id, gate_id FROM IncidentReport WHERE incident_id = %s'
        cursor.execute(query, (incident_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            cnx.close()
            raise HTTPException(status_code=404, detail="Incident Report not found")
        incident_report = {
            'incident_id': row[0],
            'description': row[1],
            'incident_time': row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None,
            'vehicle_id': row[3],
            'security_staff_id': row[4],
            'gate_id': row[5]
        }
        cursor.close()
        cnx.close()
        return incident_report
    else:
        query = 'SELECT incident_id, description, incident_time, vehicle_id, security_staff_id, gate_id FROM IncidentReport LIMIT 10'
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()
        
        incident_reports = []
        for row in rows:
            incident_reports.append({
                'incident_id': row[0],
                'description': row[1],
                'incident_time': row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None,
                'vehicle_id': row[3],
                'security_staff_id': row[4],
                'gate_id': row[5]
            })
        
        return incident_reports

# POST - สร้าง Incident Report ใหม่
@app.post('/incidentreport', response_model=IncidentReport, tags=["IncidentReport"], summary="Create a New Incident Report")
def create_incident_report(incident_report: IncidentReport):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    INSERT INTO IncidentReport (description, incident_time, vehicle_id, security_staff_id, gate_id)
    VALUES (%s, %s, %s, %s, %s)
    '''
    
    values = (
        incident_report.description,
        incident_report.incident_time if incident_report.incident_time else datetime.now(),  
        incident_report.vehicle_id,
        incident_report.security_staff_id,
        incident_report.gate_id
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    incident_id = cursor.lastrowid
    cursor.close()
    cnx.close()
    
    return {**incident_report.dict(), "incident_id": incident_id}

# PUT - อัปเดตข้อมูล Incident Report
@app.put('/incidentreport/{incident_id}', response_model=IncidentReport, tags=["IncidentReport"], summary="Update Incident Report Information")
def update_incident_report(incident_id: int, incident_report: IncidentReport):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    UPDATE IncidentReport
    SET description = %s, incident_time = %s, vehicle_id = %s, security_staff_id = %s, gate_id = %s
    WHERE incident_id = %s
    '''
    
    values = (
        incident_report.description,
        incident_report.incident_time,
        incident_report.vehicle_id,
        incident_report.security_staff_id,
        incident_report.gate_id,
        incident_id
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบ Incident Report")
    
    cursor.close()
    cnx.close()
    
    return {**incident_report.dict(), "incident_id": incident_id}

# DELETE - ลบ Incident Report โดยใช้ incident_id
@app.delete('/incidentreport/{incident_id}', tags=["IncidentReport"], summary="Delete Incident Report by ID")
def delete_incident_report(incident_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'DELETE FROM IncidentReport WHERE incident_id = %s'
    cursor.execute(query, (incident_id,))
    
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบ Incident Report")
    
    cursor.close()
    cnx.close()
    
    return {"message": f"Incident Report ที่มี ID {incident_id} ถูกลบแล้ว"}

@app.get('/securitystaff', response_model=List[SecurityStaff], tags=["SecurityStaff"], summary="Fetch All Security Staff Limit 10")
@app.get('/securitystaff/{staff_id}', response_model=Optional[SecurityStaff], tags=["SecurityStaff"], summary="Fetch Security Staff by ID")
def fetch_security_staffs(staff_id: Optional[int] = None):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    if staff_id:
        query = 'SELECT staff_id, name, shift_time, phone, gate_id FROM SecurityStaff WHERE staff_id = %s'
        cursor.execute(query, (staff_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            cnx.close()
            raise HTTPException(status_code=404, detail="Security Staff not found")
        security_staff = {
            'staff_id': row[0],
            'name': row[1],
            'shift_time': row[2],
            'phone': row[3],
            'gate_id': row[4]
        }
        cursor.close()
        cnx.close()
        return security_staff
    else:
        query = 'SELECT staff_id, name, shift_time, phone, gate_id FROM SecurityStaff LIMIT 10'
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()
        
        security_staffs = []
        for row in rows:
            security_staffs.append({
                'staff_id': row[0],
                'name': row[1],
                'shift_time': row[2],
                'phone': row[3],
                'gate_id': row[4]
            })
        
        return security_staffs

# POST - สร้าง Security Staff ใหม่
@app.post('/securitystaff', response_model=SecurityStaff, tags=["SecurityStaff"], summary="Create a New Security Staff")
def create_security_staff(security_staff: SecurityStaff):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    INSERT INTO SecurityStaff (name, shift_time, phone, gate_id)
    VALUES (%s, %s, %s, %s)
    '''
    
    values = (
        security_staff.name,
        security_staff.shift_time,
        security_staff.phone,
        security_staff.gate_id
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    staff_id = cursor.lastrowid
    cursor.close()
    cnx.close()
    
    return {**security_staff.dict(), "staff_id": staff_id}

# PUT - อัปเดตข้อมูล Security Staff
@app.put('/securitystaff/{staff_id}', response_model=SecurityStaff, tags=["SecurityStaff"], summary="Update Security Staff Information")
def update_security_staff(staff_id: int, security_staff: SecurityStaff):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    UPDATE SecurityStaff
    SET name = %s, shift_time = %s, phone = %s, gate_id = %s
    WHERE staff_id = %s
    '''
    
    values = (
        security_staff.name,
        security_staff.shift_time,
        security_staff.phone,
        security_staff.gate_id,
        staff_id
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบ Security Staff")
    
    cursor.close()
    cnx.close()
    
    return {**security_staff.dict(), "staff_id": staff_id}

# DELETE - ลบ Security Staff โดยใช้ staff_id
@app.delete('/securitystaff/{staff_id}', tags=["SecurityStaff"], summary="Delete Security Staff by ID")
def delete_security_staff(staff_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'DELETE FROM SecurityStaff WHERE staff_id = %s'
    cursor.execute(query, (staff_id,))
    
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบ Security Staff")
    
    cursor.close()
    cnx.close()
    
    return {"message": f"Security Staff ที่มี ID {staff_id} ถูกลบแล้ว"}

@app.get('/gate', response_model=List[Gate], tags=["Gate"], summary="Fetch All Gates or Gate by ID")
@app.get('/gate/{gate_id}', response_model=Optional[Gate], tags=["Gate"], summary="Fetch Gate by ID")
def fetch_gates(gate_id: Optional[int] = None):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    if gate_id:
        query = 'SELECT gate_id, location, gate_type FROM Gate WHERE gate_id = %s'
        cursor.execute(query, (gate_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            cnx.close()
            raise HTTPException(status_code=404, detail="Gate not found")
        gate = {
            'gate_id': row[0],
            'location': row[1],
            'gate_type': row[2]
        }
        cursor.close()
        cnx.close()
        return gate
    else:
        query = 'SELECT gate_id, location, gate_type FROM Gate LIMIT 10'
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()
        
        gates = []
        for row in rows:
            gates.append({
                'gate_id': row[0],
                'location': row[1],
                'gate_type': row[2]
            })
        
        return gates

# POST - สร้าง Gate ใหม่
@app.post('/gate', response_model=Gate, tags=["Gate"], summary="Create a New Gate")
def create_gate(gate: Gate):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    INSERT INTO Gate (location, gate_type)
    VALUES (%s, %s)
    '''
    
    values = (
        gate.location,
        gate.gate_type
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    gate_id = cursor.lastrowid
    cursor.close()
    cnx.close()
    
    return {**gate.dict(), "gate_id": gate_id}

# PUT - อัปเดตข้อมูล Gate
@app.put('/gate/{gate_id}', response_model=Gate, tags=["Gate"], summary="Update Gate Information")
def update_gate(gate_id: int, gate: Gate):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    UPDATE Gate
    SET location = %s, gate_type = %s
    WHERE gate_id = %s
    '''
    
    values = (
        gate.location,
        gate.gate_type,
        gate_id
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบ Gate")
    
    cursor.close()
    cnx.close()
    
    return {**gate.dict(), "gate_id": gate_id}

# DELETE - ลบ Gate โดยใช้ gate_id
@app.delete('/gate/{gate_id}', tags=["Gate"], summary="Delete Gate by ID")
def delete_gate(gate_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'DELETE FROM Gate WHERE gate_id = %s'
    cursor.execute(query, (gate_id,))
    
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบ Gate")
    
    cursor.close()
    cnx.close()
    
    return {"message": f"Gate ที่มี ID {gate_id} ถูกลบแล้ว"}

# GET - Fetch all Entry Exit Logs or fetch by specific ID
@app.get('/entryexitlog', response_model=List[EntryExitLog], tags=["EntryExitLog"], summary="Fetch All  Exit Logs Limit 10")
@app.get('/entryexitlog/{log_id}', response_model=Optional[EntryExitLog], tags=["EntryExitLog"], summary="Fetch Exit Log by ID")
def fetch_entry_exit_logs(log_id: Optional[int] = None):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    if log_id:
        # Fetch log by specific log_id
        query = 'SELECT log_id, vehicle_id, entry_time, exit_time, gate_id FROM EntryExitLog WHERE log_id = %s'
        cursor.execute(query, (log_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            cnx.close()
            raise HTTPException(status_code=404, detail="Entry Exit Log not found")
        entry_exit_log = {
            'log_id': row[0],
            'vehicle_id': row[1],
            'entry_time': row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None,
            'exit_time': row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None,
            'gate_id': row[4]
        }
        cursor.close()
        cnx.close()
        return entry_exit_log
    else:
        # Fetch all logs with a limit of 10
        query = 'SELECT log_id, vehicle_id, entry_time, exit_time, gate_id FROM EntryExitLog LIMIT 10'
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()
        
        entry_exit_logs = []
        for row in rows:
            entry_exit_logs.append({
                'log_id': row[0],
                'vehicle_id': row[1],
                'entry_time': row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None,
                'exit_time': row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None,
                'gate_id': row[4]
            })
        
        return entry_exit_logs
    
# POST - สร้าง EntryExitLog ใหม่
@app.post('/entryexitlog', response_model=EntryExitLog, tags=["EntryExitLog"], summary="Create a New Entry Exit Log")
def create_entry_exit_log(entry_exit_log: EntryExitLog):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    INSERT INTO EntryExitLog (vehicle_id, entry_time, exit_time, gate_id)
    VALUES (%s, %s, %s, %s)
    '''
    
    values = (
        entry_exit_log.vehicle_id,
        entry_exit_log.entry_time if entry_exit_log.entry_time else datetime.now(),  # ใช้เวลาปัจจุบันถ้าไม่ระบุ entry_time
        entry_exit_log.exit_time,
        entry_exit_log.gate_id
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    log_id = cursor.lastrowid
    cursor.close()
    cnx.close()
    
    return {**entry_exit_log.dict(), "log_id": log_id}

# PUT - อัปเดตข้อมูล EntryExitLog
@app.put('/entryexitlog/{log_id}', response_model=EntryExitLog, tags=["EntryExitLog"], summary="Update Entry Exit Log Information")
def update_entry_exit_log(log_id: int, entry_exit_log: EntryExitLog):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = '''
    UPDATE EntryExitLog
    SET vehicle_id = %s, entry_time = %s, exit_time = %s, gate_id = %s
    WHERE log_id = %s
    '''
    
    values = (
        entry_exit_log.vehicle_id,
        entry_exit_log.entry_time,
        entry_exit_log.exit_time,
        entry_exit_log.gate_id,
        log_id
    )
    
    cursor.execute(query, values)
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบ Entry Exit Log")
    
    cursor.close()
    cnx.close()
    
    return {**entry_exit_log.dict(), "log_id": log_id}

# DELETE - ลบ EntryExitLog โดยใช้ log_id
@app.delete('/entryexitlog/{log_id}', tags=["EntryExitLog"], summary="Delete Entry Exit Log by ID")
def delete_entry_exit_log(log_id: int):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = 'DELETE FROM EntryExitLog WHERE log_id = %s'
    cursor.execute(query, (log_id,))
    
    cnx.commit()
    
    if cursor.rowcount == 0:
        cnx.close()
        raise HTTPException(status_code=404, detail="ไม่พบ Entry Exit Log")
    
    cursor.close()
    cnx.close()
    
    return {"message": f"Entry Exit Log ที่มี ID {log_id} ถูกลบแล้ว"}

