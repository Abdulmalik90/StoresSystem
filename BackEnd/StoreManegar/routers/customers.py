from fastapi import APIRouter, Depends, HTTPException, status
import pymysql
from database import get_db
from schemas.customer import CreateUpdate_Customer
import uuid

router = APIRouter(prefix="/customers", tags=["Customers"])

# Create Customer
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_customer(customer: CreateUpdate_Customer, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            cid = str(uuid.uuid4())
            sql = """
                insert into customer (cid, cname, mobile_number)
                values (%s, %s, %s)
            """
            cursor.execute(sql, (cid, customer.cname, customer.mobile_number))
            conn.commit()

            return {
                "message": "Customer created successfully",
                "cid": cid
            }
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Duplicate entry or constraint violation (e.g., mobile number already exists).")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# Get many Customers
@router.get("/")
def get_customers(search: str | None = None, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            if search:
                sql = """
                    SELECT * FROM customer
                    WHERE cid LIKE %s OR cname LIKE %s OR mobile_number LIKE %s
                """
                pattern = f"%{search}%"
                cursor.execute(sql, (pattern, pattern, pattern))
            else:
                sql = "SELECT * FROM customer"
                cursor.execute(sql)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# Get A Customer
@router.get("/{cid}")
def get_a_customer(cid : str, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                select * from customer
                where cid = %s
            """
            cursor.execute(sql, (cid,))
            author = cursor.fetchone()

            if not author:
                raise HTTPException(status_code=404, detail="Customer not found")
            return author
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Update Customer
@router.put("/{cid}")
def update_customer(cid: str, customer: CreateUpdate_Customer,conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                Update customer
                set cname = %s, mobile_number = %s
                where cid = %s
            """
            cursor.execute(sql, (customer.cname, customer.mobile_number, cid))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Customers not found")
            conn.commit()
            return {"message": "Customer update successfully"}

    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Data violates database constraints.")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# Delete Customer
@router.delete("/{cid}")
def delete_customer(cid: str, conn = Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                Delete from customer
                where cid = %s
            """

            cursor.execute(sql, (cid,))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Customer Not Found")

            conn.commit()
            return {"message": "Deleted successfully"}

    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete this Customer because they have linked Receipts.")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")