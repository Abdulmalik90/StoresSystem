from fastapi import APIRouter, Depends, HTTPException, status
import pymysql
from database import get_db
from schemas.product import CreateUpdate_Product
import uuid

router = APIRouter(prefix="/products", tags=["Products"])

# Create product
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_product(product: CreateUpdate_Product, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            pid = str(uuid.uuid4())
            sql = """
                insert into product (pid, pname, price, quantity, discount, sid, category_id)
                values (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (pid, product.pname, product.price, product.quantity, product.discount, product.sid, product.category_id))
            conn.commit()

            return {
                "message": "product created successfully",
                "pid": pid
            }
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Invalid Supplier ID (sid) or Category ID (category_id). ")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# Get many products
@router.get("/")
def get_products(search: str | None = None, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            if search:
                sql = """
                    SELECT p.pid, p.pname, p.price, p.quantity, p.discount, p.category_id, c.category_name, p.sid, s.sname As supplier_name
                    FROM product p
                    JOIN category c ON p.category_id = c.category_id
                    JOIN supplier s ON p.sid = s.sid
                    WHERE s.sname LIKE %s OR p.pname LIKE %s OR p.price LIKE %s or p.quantity like %s or p.discount like %s
                    or c.category_name like %s or p.category_id like %s
                """
                pattern = f"%{search}%"
                cursor.execute(sql, (pattern, pattern, pattern, pattern, pattern, pattern, pattern))
            else:
                sql = """
                    SELECT p.pid, p.pname, p.price, p.quantity, p.discount,
                    p.category_id, c.category_name,
                    p.sid, s.sname AS supplier_name
                    FROM product p
                    JOIN category c ON p.category_id = c.category_id
                    JOIN supplier s ON p.sid = s.sid
                """
                cursor.execute(sql)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# get a product
@router.get("/{pid}")
def get_a_product(pid : str, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT p.pid, p.pname, p.price, p.quantity, p.discount,
                    p.category_id, c.category_name,
                    p.sid, s.sname AS supplier_name
                    FROM product p
                    JOIN category c ON p.category_id = c.category_id
                    JOIN supplier s ON p.sid = s.sid
                where p.pid = %s
            """
            cursor.execute(sql, (pid,))
            product = cursor.fetchone()

            if not product:
                raise HTTPException(status_code=404, detail="product not found")
            return product
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Update product
@router.put("/{pid}")
def update_product(pid: str, product: CreateUpdate_Product,conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
            
                Update product
                set pname = %s, price = %s, quantity = %s, discount = %s, sid = %s, category_id = %s
                where pid = %s
            """
            cursor.execute(sql, (product.pname, product.price, product.quantity, product.discount, product.sid, product.category_id, pid))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="product not found")
            conn.commit()
            return {"message": "product updated successfully"}

    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Data violates database constraints.")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# Delete product
@router.delete("/{pid}")
def delete_product(pid: str, conn = Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                Delete from product
                where pid = %s
            """

            cursor.execute(sql, (pid,))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="product Not Found")

            conn.commit()
            return {"message": "Deleted successfully"}

    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete this product because it is linked to existing receipts.")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")