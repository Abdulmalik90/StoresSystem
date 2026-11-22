from fastapi import APIRouter, Depends, HTTPException, status
import pymysql
from database import get_db
from schemas.employee import EmployeeCreate, EmployeeUpdate
import uuid
router = APIRouter(prefix="/employees", tags=["Employees"])

# 1. Create: adding new employee
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            eid = str(uuid.uuid4())
            sql = """
                INSERT INTO employee (eid, ename, google_sub, email, erole, mobile_number)
                    values (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (eid, employee.ename, employee.google_sub, employee.email, employee.erole, employee.mobile_number))
            conn.commit()
            return {
                "message": "Employee Created Successfully",
                "eid": eid
            }
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Duplicate entry or constraint violation (e.g., email already exists)."

        )
    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Database error: {str(e)}")

# 2. Search for Employee or list all of them
@router.get("/")
def get_employees(search: str | None = None, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            if search:
                sql = """
                    Select eid, ename, erole, email, mobile_number, joinDate
                    from employee
                    where ename like %s or mobile_number like %s or joinDate like %s or erole like %s or email like %s or eid like %s
                """
                pattern = f"%{search}%"
                cursor.execute(sql, (pattern, pattern, pattern, pattern, pattern, pattern))
            else:
                sql = """
                      Select eid, ename, erole, email, mobile_number, joinDate
                      from employee
                      """
                cursor.execute(sql)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# 3. Read Single Employee: get a specific log for filling the edit form in the ui
@router.get("/{eid}")
def get_an_employee(eid : str, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                select * from employee
                where eid = %s
            """
            cursor.execute(sql, (eid,))
            author = cursor.fetchone()

            if not author:
                raise HTTPException(status_code=404, detail="Employee not found")
            return author
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# 4. Update an Employee
@router.put("/{eid}")
def update_employee(eid: str, employee: EmployeeUpdate, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                update employee
                set ename = %s, email = %s, erole = %s, mobile_number = %s
                where eid = %s
            """
            cursor.execute(sql, (employee.ename, employee.email, employee.erole, employee.mobile_number, eid))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Employee not found")

            conn.commit()
            return {"message": "Employee update successfully"}
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Data violates database constraints.")
    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# 4. Delete:
@router.delete("/{eid}")
def delete_employee(eid: int, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM employee WHERE eid = %s"
            cursor.execute(sql, (eid,))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="employee not found")

            conn.commit()
            return {"message": "employee deleted successfully"}

    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete this employee because they have linked Receipts."
        )
    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")