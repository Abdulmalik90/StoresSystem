from fastapi import APIRouter, Depends, HTTPException, status
import pymysql
from database import get_db
from schemas.supplier import CreateUpdate_Supplier
import uuid

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

# Create supplier
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_supplier(supplier: CreateUpdate_Supplier, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sid = str(uuid.uuid4())
            sql = """
                insert into supplier (sid, sname, mobile_number, email)
                values (%s, %s, %s, %s)
            """
            cursor.execute(sql, (sid, supplier.sname, supplier.mobile_number, supplier.email))
            conn.commit()

            return {
                "message": "supplier created successfully",
                "sid": sid
            }
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Duplicate entry or constraint violation (e.g., email already exists).")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# Get many Suppliers
@router.get("/")
def get_suppliers(search: str | None = None, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            if search:
                sql = """
                    SELECT * FROM supplier
                    WHERE sid LIKE %s OR sname LIKE %s OR mobile_number LIKE %s or email like %s
                """
                pattern = f"%{search}%"
                cursor.execute(sql, (pattern, pattern, pattern, pattern))
            else:
                sql = "SELECT * FROM supplier"
                cursor.execute(sql)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# get a supplier
@router.get("/{sid}")
def get_a_supplier(sid : str, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                select * from supplier
                where sid = %s
            """
            cursor.execute(sql, (sid,))
            author = cursor.fetchone()

            if not author:
                raise HTTPException(status_code=404, detail="Supplier not found")
            return author
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Update Supplier
@router.put("/{sid}")
def update_supplier(sid: str, supplier: CreateUpdate_Supplier,conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                Update supplier
                set sname = %s, mobile_number = %s, email = %s
                where sid = %s
            """
            cursor.execute(sql, (supplier.sname, supplier.mobile_number, supplier.email, sid))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Supplier not found")
            conn.commit()
            return {"message": "Supplier update successfully"}

    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Data violates database constraints.")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# Delete Supplier
@router.delete("/{sid}")
def delete_supplier(sid: str, conn = Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                Delete from supplier
                where sid = %s
            """

            cursor.execute(sql, (sid,))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Supplier Not Found")

            conn.commit()
            return {"message": "Deleted successfully"}

    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete this Supplier because they have linked Products.")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")