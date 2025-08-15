from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

app = FastAPI(title="Employee Management API", version="1.0.0")

# Custom middleware for logging and filtering invalid requests
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        print(f"Incoming request: {request.method} {request.url} from {client_ip}")
        
        # Filter out invalid or suspicious requests
        if not request.headers.get("user-agent") or "bot" in request.headers.get("user-agent", "").lower():
            print(f"Blocked suspicious request from {client_ip}")
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid or suspicious request detected"}
            )
        
        try:
            response = await call_next(request)
        except Exception as e:
            print(f"Error processing request from {client_ip}: {str(e)}")
            raise
        return response

app.add_middleware(LoggingMiddleware)

# CORS middleware setup for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://preview--salom-panel-35.lovable.app",
        "http://185.217.131.245:9008",
        "http://localhost:9008"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Access-Control-Allow-Origin"],
)

# Data file paths
DATA_DIR = "data"
DISTRICTS_FILE = os.path.join(DATA_DIR, "districts.json")
DEPARTMENTS_FILE = os.path.join(DATA_DIR, "departments.json")
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")
ATTENDANCE_FILE = os.path.join(DATA_DIR, "attendance.json")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Pydantic models
class District(BaseModel):
    id: Optional[str] = None
    name: str
    code: str
    description: Optional[str] = ""
    createdAt: Optional[str] = None

class Department(BaseModel):
    id: Optional[str] = None
    name: str
    departmentNumber: str
    districtId: str
    districtName: Optional[str] = ""
    manager: str
    employeeCount: Optional[int] = 0
    description: Optional[str] = ""
    createdAt: Optional[str] = None

class Employee(BaseModel):
    id: Optional[str] = None
    name: str
    phone: str
    photo: Optional[str] = ""
    position: str
    departmentId: str
    departmentName: Optional[str] = ""
    departmentNumber: Optional[str] = ""
    districtName: Optional[str] = ""
    email: Optional[str] = ""
    status: str = "active"
    createdAt: Optional[str] = None

class AttendanceRecord(BaseModel):
    id: Optional[str] = None
    employeeName: str
    employeeId: Optional[str] = ""
    department: str
    date: str
    checkIn: Optional[str] = None
    checkOut: Optional[str] = None
    status: str = "absent"
    workHours: Optional[str] = "0:00"
    location: Optional[Dict] = None

class AttendanceCreate(BaseModel):
    employeeId: str
    date: str
    checkIn: Optional[str] = None
    checkOut: Optional[str] = None
    status: str
    location: Optional[Dict] = None

# Utility functions
def load_json_data(file_path: str) -> List[Dict]:
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {file_path}: {str(e)}")
        return []

def save_json_data(file_path: str, data: List[Dict]):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {str(e)}")

def generate_id() -> str:
    return str(uuid.uuid4())

def get_current_datetime() -> str:
    return datetime.now().isoformat()

# Initialize sample data
def initialize_sample_data():
    if not os.path.exists(DISTRICTS_FILE):
        sample_districts = [
            {
                "id": "1",
                "name": "Toshkent tumani",
                "code": "TSH001",
                "description": "Markaziy ofis joylashgan tuman",
                "createdAt": "2024-01-15T10:00:00"
            },
            {
                "id": "2",
                "name": "Samarqand tumani",
                "code": "SMQ001",
                "description": "Ikkinchi filial joylashgan tuman",
                "createdAt": "2024-01-20T10:00:00"
            }
        ]
        save_json_data(DISTRICTS_FILE, sample_districts)

    if not os.path.exists(DEPARTMENTS_FILE):
        sample_departments = [
            {
                "id": "1",
                "name": "IT bo'limi",
                "departmentNumber": "IT-001",
                "districtId": "1",
                "districtName": "Toshkent tumani",
                "manager": "Karimov Sardor",
                "employeeCount": 3,
                "description": "Dasturlash va texnik yordam",
                "createdAt": "2024-02-01T10:00:00"
            },
            {
                "id": "2",
                "name": "Moliya bo'limi",
                "departmentNumber": "FIN-001",
                "districtId": "1",
                "districtName": "Toshkent tumani",
                "manager": "Abdullayeva Nilufar",
                "employeeCount": 2,
                "description": "Moliyaviy operatsiyalar",
                "createdAt": "2024-02-05T10:00:00"
            },
            {
                "id": "3",
                "name": "Marketing bo'limi",
                "departmentNumber": "MKT-001",
                "districtId": "2",
                "districtName": "Samarqand tumani",
                "manager": "Nazarova Dilshoda",
                "employeeCount": 2,
                "description": "Reklama va savdo",
                "createdAt": "2024-02-10T10:00:00"
            }
        ]
        save_json_data(DEPARTMENTS_FILE, sample_departments)

    if not os.path.exists(EMPLOYEES_FILE):
        sample_employees = [
            {
                "id": "1",
                "name": "Karimov Sardor",
                "phone": "+998901234567",
                "photo": "",
                "position": "IT menejer",
                "departmentId": "1",
                "departmentName": "IT bo'limi",
                "departmentNumber": "IT-001",
                "districtName": "Toshkent tumani",
                "email": "sardor@company.uz",
                "status": "active",
                "createdAt": "2024-02-15T10:00:00"
            },
            {
                "id": "2",
                "name": "Abdullayeva Nilufar",
                "phone": "+998901234568",
                "photo": "",
                "position": "Moliya menejer",
                "departmentId": "2",
                "departmentName": "Moliya bo'limi",
                "departmentNumber": "FIN-001",
                "districtName": "Toshkent tumani",
                "email": "nilufar@company.uz",
                "status": "active",
                "createdAt": "2024-02-16T10:00:00"
            },
            {
                "id": "3",
                "name": "Nazarova Dilshoda",
                "phone": "+998901234570",
                "photo": "",
                "position": "Marketing mutaxassis",
                "departmentId": "3",
                "departmentName": "Marketing bo'limi",
                "departmentNumber": "MKT-001",
                "districtName": "Samarqand tumani",
                "email": "dilshoda@company.uz",
                "status": "active",
                "createdAt": "2024-02-17T10:00:00"
            },
            {
                "id": "4",
                "name": "Toshmatov Oybek",
                "phone": "+998901234569",
                "photo": "",
                "position": "IT dasturchi",
                "departmentId": "1",
                "departmentName": "IT bo'limi",
                "departmentNumber": "IT-001",
                "districtName": "Toshkent tumani",
                "email": "oybek@company.uz",
                "status": "active",
                "createdAt": "2024-02-18T10:00:00"
            },
            {
                "id": "5",
                "name": "Aliyev Vali",
                "phone": "+998901234571",
                "photo": "",
                "position": "Moliya hisobchisi",
                "departmentId": "2",
                "departmentName": "Moliya bo'limi",
                "departmentNumber": "FIN-001",
                "districtName": "Toshkent tumani",
                "email": "vali@company.uz",
                "status": "active",
                "createdAt": "2024-02-19T10:00:00"
            },
            {
                "id": "6",
                "name": "Rahimova Madina",
                "phone": "+998901234572",
                "photo": "",
                "position": "Marketing dizayner",
                "departmentId": "3",
                "departmentName": "Marketing bo'limi",
                "departmentNumber": "MKT-001",
                "districtName": "Samarqand tumani",
                "email": "madina@company.uz",
                "status": "active",
                "createdAt": "2024-02-20T10:00:00"
            },
            {
                "id": "7",
                "name": "Ergashev Jasur",
                "phone": "+998901234573",
                "photo": "",
                "position": "IT tizim administratori",
                "departmentId": "1",
                "departmentName": "IT bo'limi",
                "departmentNumber": "IT-001",
                "districtName": "Toshkent tumani",
                "email": "jasur@company.uz",
                "status": "active",
                "createdAt": "2024-02-21T10:00:00"
            }
        ]
        save_json_data(EMPLOYEES_FILE, sample_employees)

    if not os.path.exists(ATTENDANCE_FILE):
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        sample_attendance = [
            {
                "id": "1",
                "employeeName": "Karimov Sardor",
                "employeeId": "1",
                "department": "IT bo'limi",
                "date": today,
                "checkIn": "09:00",
                "checkOut": "18:00",
                "status": "present",
                "workHours": "8:00",
                "location": {"latitude": 41.2995, "longitude": 69.2401, "address": "Toshkent"}
            },
            {
                "id": "2",
                "employeeName": "Abdullayeva Nilufar",
                "employeeId": "2",
                "department": "Moliya bo'limi",
                "date": today,
                "checkIn": "09:15",
                "checkOut": "18:00",
                "status": "late",
                "workHours": "7:45",
                "location": {"latitude": 41.2995, "longitude": 69.2401, "address": "Toshkent"}
            },
            {
                "id": "3",
                "employeeName": "Nazarova Dilshoda",
                "employeeId": "3",
                "department": "Marketing bo'limi",
                "date": today,
                "checkIn": "08:55",
                "checkOut": "17:30",
                "status": "early-leave",
                "workHours": "7:35",
                "location": {"latitude": 39.6270, "longitude": 66.9750, "address": "Samarqand"}
            },
            {
                "id": "4",
                "employeeName": "Toshmatov Oybek",
                "employeeId": "4",
                "department": "IT bo'limi",
                "date": today,
                "checkIn": None,
                "checkOut": None,
                "status": "absent",
                "workHours": "0:00",
                "location": None
            },
            {
                "id": "5",
                "employeeName": "Aliyev Vali",
                "employeeId": "5",
                "department": "Moliya bo'limi",
                "date": today,
                "checkIn": "09:00",
                "checkOut": "18:00",
                "status": "present",
                "workHours": "8:00",
                "location": {"latitude": 41.2995, "longitude": 69.2401, "address": "Toshkent"}
            },
            {
                "id": "6",
                "employeeName": "Karimov Sardor",
                "employeeId": "1",
                "department": "IT bo'limi",
                "date": yesterday,
                "checkIn": "08:55",
                "checkOut": "18:10",
                "status": "present",
                "workHours": "8:15",
                "location": {"latitude": 41.2995, "longitude": 69.2401, "address": "Toshkent"}
            },
            {
                "id": "7",
                "employeeName": "Abdullayeva Nilufar",
                "employeeId": "2",
                "department": "Moliya bo'limi",
                "date": yesterday,
                "checkIn": "09:00",
                "checkOut": "18:00",
                "status": "present",
                "workHours": "8:00",
                "location": {"latitude": 41.2995, "longitude": 69.2401, "address": "Toshkent"}
            }
        ]
        save_json_data(ATTENDANCE_FILE, sample_attendance)

initialize_sample_data()

class APIResponse(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None

@app.get("/districts")
async def get_districts():
    districts = load_json_data(DISTRICTS_FILE)
    return APIResponse(success=True, data=districts)

@app.post("/districts")
async def create_district(district: District):
    districts = load_json_data(DISTRICTS_FILE)
    if any(d['code'] == district.code for d in districts):
        raise HTTPException(status_code=400, detail="Bu kod allaqachon mavjud")
    new_district = district.model_dump()
    new_district['id'] = generate_id()
    new_district['createdAt'] = get_current_datetime()
    districts.append(new_district)
    save_json_data(DISTRICTS_FILE, districts)
    return APIResponse(success=True, data=new_district, message="Tuman muvaffaqiyatli qo'shildi")

@app.put("/districts/{district_id}")
async def update_district(district_id: str, district_data: Dict):
    districts = load_json_data(DISTRICTS_FILE)
    for i, d in enumerate(districts):
        if d['id'] == district_id:
            districts[i].update(district_data)
            save_json_data(DISTRICTS_FILE, districts)
            return APIResponse(success=True, data=districts[i], message="Tuman yangilandi")
    raise HTTPException(status_code=404, detail="Tuman topilmadi")

@app.delete("/districts/{district_id}")
async def delete_district(district_id: str):
    districts = load_json_data(DISTRICTS_FILE)
    departments = load_json_data(DEPARTMENTS_FILE)
    if any(dept['districtId'] == district_id for dept in departments):
        raise HTTPException(status_code=400, detail="Bu tumanda bo'limlar mavjud")
    districts = [d for d in districts if d['id'] != district_id]
    save_json_data(DISTRICTS_FILE, districts)
    return APIResponse(success=True, data=None, message="Tuman o'chirildi")

@app.get("/departments")
async def get_departments():
    departments = load_json_data(DEPARTMENTS_FILE)
    return APIResponse(success=True, data=departments)

@app.post("/departments")
async def create_department(department: Department):
    departments = load_json_data(DEPARTMENTS_FILE)
    districts = load_json_data(DISTRICTS_FILE)
    if any(d['departmentNumber'] == department.departmentNumber and d['districtId'] == department.districtId for d in departments):
        raise HTTPException(status_code=400, detail="Bu bo'lim raqami allaqachon mavjud")
    district = next((d for d in districts if d['id'] == department.districtId), None)
    if not district:
        raise HTTPException(status_code=404, detail="Tuman topilmadi")
    new_department = department.model_dump()
    new_department['id'] = generate_id()
    new_department['districtName'] = district['name']
    new_department['createdAt'] = get_current_datetime()
    departments.append(new_department)
    save_json_data(DEPARTMENTS_FILE, departments)
    return APIResponse(success=True, data=new_department, message="Bo'lim muvaffaqiyatli qo'shildi")

@app.put("/departments/{department_id}")
async def update_department(department_id: str, department_data: Dict):
    departments = load_json_data(DEPARTMENTS_FILE)
    for i, d in enumerate(departments):
        if d['id'] == department_id:
            departments[i].update(department_data)
            save_json_data(DEPARTMENTS_FILE, departments)
            return APIResponse(success=True, data=departments[i], message="Bo'lim yangilandi")
    raise HTTPException(status_code=404, detail="Bo'lim topilmadi")

@app.delete("/departments/{department_id}")
async def delete_department(department_id: str):
    departments = load_json_data(DEPARTMENTS_FILE)
    employees = load_json_data(EMPLOYEES_FILE)
    if any(emp['departmentId'] == department_id for emp in employees):
        raise HTTPException(status_code=400, detail="Bu bo'limda ishchilar mavjud")
    departments = [d for d in departments if d['id'] != department_id]
    save_json_data(DEPARTMENTS_FILE, departments)
    return APIResponse(success=True, data=None, message="Bo'lim o'chirildi")

@app.get("/employees")
async def get_employees():
    employees = load_json_data(EMPLOYEES_FILE)
    return APIResponse(success=True, data=employees)

@app.post("/employees")
async def create_employee(employee: Employee):
    employees = load_json_data(EMPLOYEES_FILE)
    departments = load_json_data(DEPARTMENTS_FILE)
    if any(emp['phone'] == employee.phone for emp in employees):
        raise HTTPException(status_code=400, detail="Bu telefon raqami allaqachon mavjud")
    department = next((d for d in departments if d['id'] == employee.departmentId), None)
    if not department:
        raise HTTPException(status_code=404, detail="Bo'lim topilmadi")
    new_employee = employee.model_dump()
    new_employee['id'] = generate_id()
    new_employee['departmentName'] = department['name']
    new_employee['departmentNumber'] = department['departmentNumber']
    new_employee['districtName'] = department['districtName']
    new_employee['createdAt'] = get_current_datetime()
    employees.append(new_employee)
    save_json_data(EMPLOYEES_FILE, employees)
    departments = load_json_data(DEPARTMENTS_FILE)
    for i, d in enumerate(departments):
        if d['id'] == employee.departmentId:
            departments[i]['employeeCount'] = departments[i].get('employeeCount', 0) + 1
            break
    save_json_data(DEPARTMENTS_FILE, departments)
    return APIResponse(success=True, data=new_employee, message="Ishchi muvaffaqiyatli qo'shildi")

@app.put("/employees/{employee_id}")
async def update_employee(employee_id: str, employee_data: Dict):
    employees = load_json_data(EMPLOYEES_FILE)
    for i, emp in enumerate(employees):
        if emp['id'] == employee_id:
            employees[i].update(employee_data)
            save_json_data(EMPLOYEES_FILE, employees)
            return APIResponse(success=True, data=employees[i], message="Ishchi ma'lumotlari yangilandi")
    raise HTTPException(status_code=404, detail="Ishchi topilmadi")

@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    employees = load_json_data(EMPLOYEES_FILE)
    departments = load_json_data(DEPARTMENTS_FILE)
    employee = next((emp for emp in employees if emp['id'] == employee_id), None)
    if not employee:
        raise HTTPException(status_code=404, detail="Ishchi topilmadi")
    employees = [emp for emp in employees if emp['id'] != employee_id]
    save_json_data(EMPLOYEES_FILE, employees)
    for i, d in enumerate(departments):
        if d['id'] == employee['departmentId']:
            departments[i]['employeeCount'] = max(0, departments[i].get('employeeCount', 1) - 1)
            break
    save_json_data(DEPARTMENTS_FILE, departments)
    return APIResponse(success=True, data=None, message="Ishchi o'chirildi")

@app.get("/attendance")
async def get_attendance(date: str = Query(..., description="Sana YYYY-MM-DD formatida")):
    attendance_records = load_json_data(ATTENDANCE_FILE)
    filtered_records = [record for record in attendance_records if record['date'] == date]
    return APIResponse(success=True, data=filtered_records)

@app.post("/attendance")
async def mark_attendance(attendance: AttendanceCreate):
    attendance_records = load_json_data(ATTENDANCE_FILE)
    employees = load_json_data(EMPLOYEES_FILE)
    employee = next((emp for emp in employees if emp['id'] == attendance.employeeId), None)
    if not employee:
        raise HTTPException(status_code=404, detail="Ishchi topilmadi")
    existing_record = next((record for record in attendance_records
                           if record['employeeId'] == attendance.employeeId and record['date'] == attendance.date), None)
    if existing_record:
        for i, record in enumerate(attendance_records):
            if record['id'] == existing_record['id']:
                attendance_records[i].update({
                    'checkIn': attendance.checkIn,
                    'checkOut': attendance.checkOut,
                    'status': attendance.status,
                    'location': attendance.location,
                    'workHours': calculate_work_hours(attendance.checkIn, attendance.checkOut)
                })
                break
    else:
        new_record = {
            'id': generate_id(),
            'employeeName': employee['name'],
            'employeeId': attendance.employeeId,
            'department': employee['departmentName'],
            'date': attendance.date,
            'checkIn': attendance.checkIn,
            'checkOut': attendance.checkOut,
            'status': attendance.status,
            'workHours': calculate_work_hours(attendance.checkIn, attendance.checkOut),
            'location': attendance.location
        }
        attendance_records.append(new_record)
    save_json_data(ATTENDANCE_FILE, attendance_records)
    return APIResponse(success=True, data=None, message="Davomat belgilandi")

def calculate_work_hours(check_in: Optional[str], check_out: Optional[str]) -> str:
    if not check_in or not check_out:
        return "0:00"
    try:
        check_in_time = datetime.strptime(check_in, "%H:%M")
        check_out_time = datetime.strptime(check_out, "%H:%M")
        if check_out_time > check_in_time:
            diff = check_out_time - check_in_time
            if diff.seconds > 6 * 3600:
                diff = diff - timedelta(hours=1)
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            return f"{hours}:{minutes:02d}"
    except ValueError:
        return "0:00"
    return "0:00"

@app.get("/statistics")
async def get_statistics(period: Optional[str] = Query("monthly", description="Davr: daily, weekly, monthly, yearly")):
    employees = load_json_data(EMPLOYEES_FILE)
    departments = load_json_data(DEPARTMENTS_FILE)
    districts = load_json_data(DISTRICTS_FILE)
    attendance_records = load_json_data(ATTENDANCE_FILE)
    total_employees = len(employees)
    active_employees = len([emp for emp in employees if emp['status'] == 'active'])
    total_departments = len(departments)
    total_districts = len(districts)
    today = datetime.now().strftime('%Y-%m-%d')
    today_attendance = [record for record in attendance_records if record['date'] == today]
    present_today = len([record for record in today_attendance if record['status'] == 'present'])
    late_today = len([record for record in today_attendance if record['status'] == 'late'])
    absent_today = len([record for record in today_attendance if record['status'] == 'absent'])
    attendance_percentage = (present_today + late_today) / max(total_employees, 1) * 100 if total_employees > 0 else 0
    late_percentage = late_today / max(total_employees, 1) * 100 if total_employees > 0 else 0
    attendance_chart_data = [
        {"name": "Dushanba", "present": 45, "absent": 5, "late": 3},
        {"name": "Seshanba", "present": 47, "absent": 3, "late": 2},
        {"name": "Chorshanba", "present": 48, "absent": 2, "late": 2},
        {"name": "Payshanba", "present": 46, "absent": 4, "late": 3},
        {"name": "Juma", "present": 44, "absent": 6, "late": 3},
    ]
    department_chart_data = []
    colors = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5a2b']
    for i, dept in enumerate(departments):
        department_chart_data.append({
            "name": dept['name'],
            "value": dept.get('employeeCount', 0),
            "color": colors[i % len(colors)],
            "districtId": dept['districtId']
        })
    performance_chart_data = [
        {"month": "Yanvar", "efficiency": 88, "satisfaction": 92},
        {"month": "Fevral", "efficiency": 90, "satisfaction": 89},
        {"month": "Mart", "efficiency": 94, "satisfaction": 95},
        {"month": "Aprel", "efficiency": 91, "satisfaction": 93},
        {"month": "May", "efficiency": 96, "satisfaction": 97},
        {"month": "Iyun", "efficiency": 93, "satisfaction": 94},
    ]
    statistics_data = {
        "overview": {
            "totalEmployees": total_employees,
            "activeEmployees": active_employees,
            "totalDepartments": total_departments,
            "totalDistricts": total_districts
        },
        "attendance": {
            "total": total_employees,
            "present": present_today,
            "absent": absent_today,
            "late": late_today,
            "percentage": round(attendance_percentage, 1)
        },
        "trends": {
            "attendance": {"current": round(attendance_percentage, 1), "change": 2.1},
            "late": {"current": round(late_percentage, 1), "change": -1.5},
            "efficiency": {"current": 94.8, "change": 3.2},
            "satisfaction": {"current": 96.1, "change": 1.8}
        },
        "attendanceData": attendance_chart_data,
        "departmentData": department_chart_data,
        "performanceData": performance_chart_data,
        "insights": [
            {
                "type": "positive",
                "title": "Ijobiy tendentsiya",
                "description": "IT bo'limi samaradorligi 15% oshdi"
            },
            {
                "type": "warning",
                "title": "E'tibor talab qiladi",
                "description": "Marketing bo'limida kechikishlar ko'paydi"
            },
            {
                "type": "info",
                "title": "Tavsiya",
                "description": "Moslashuvchan ish vaqtini ko'rib chiqing"
            }
        ]
    }
    return APIResponse(success=True, data=statistics_data)

@app.get("/")
async def health_check():
    return {"message": "Employee Management API ishlayapti", "status": "OK", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Employee Management API ishga tushmoqda...")
    print("📊 API dokumentatsiya: https://185.217.131.245:9092/docs")
    print("🌐 API URL: https://185.217.131.245:9092")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9092,
        timeout_keep_alive=0,
        log_level="debug",
        ssl_keyfile="/etc/letsencrypt/live/185.217.131.245/privkey.pem",
        ssl_certfile="/etc/letsencrypt/live/185.217.131.245/fullchain.pem"
    )
