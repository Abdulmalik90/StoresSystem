from fastapi import APIRouter, Depends, HTTPException, status
import pymysql
from database import get_db
from schemas.category import CreateUpdate_Category
import uuid
from utils.auth import require_role
router = APIRouter(prefix="/categories", tags=["Categories"], dependencies=[Depends(require_role(["admin", "cashier"]))])

# Create category
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_category(category: CreateUpdate_Category, conn=Depends(get_db), current_user: dict = Depends(require_role(["admin"]))):
    try:
        with conn.cursor() as cursor:
            cat_id = str(uuid.uuid4())
            sql = """
                insert into category (category_id, category_name)
                values (%s, %s)
            """
            cursor.execute(sql, (cat_id, category.category_name))
            conn.commit()

            return {
                "message": "Category created successfully",
                "category_id": cat_id
            }
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Duplicate entry or constraint violation (e.g., name already exists).")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

#Get a Category
@router.get("/{category_id}")
def get_a_category(category_id : str, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = """
                select * from category
                where category_id = %s
            """
            cursor.execute(sql, (category_id,))
            author = cursor.fetchone()

            if not author:
                raise HTTPException(status_code=404, detail="Category not found")
            return author
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Get many categories
@router.get("/")
def get_categories(search: str | None = None, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            if search:
                sql = """
                    SELECT * FROM category
                    WHERE category_id LIKE %s OR category_name LIKE %s 
                """
                pattern = f"%{search}%"
                cursor.execute(sql, (pattern, pattern))
            else:
                sql = "SELECT * FROM category"
                cursor.execute(sql)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")


# Update category
@router.put("/{category_id}")
def update_category(category_id: str, category: CreateUpdate_Category,conn=Depends(get_db), current_user: dict = Depends(require_role(["admin"]))):
    try:
        with conn.cursor() as cursor:
            sql = """
                Update category
                set category_name = %s
                where category_id = %s
            """
            cursor.execute(sql, (category.category_name, category_id))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="category not found")
            conn.commit()
            return {"message": "category update successfully"}

    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Data violates database constraints.")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# Delete category
@router.delete("/{category_id}")
def delete_category(category_id: str, conn = Depends(get_db), current_user: dict = Depends(require_role(["admin"]))):
    try:
        with conn.cursor() as cursor:
            sql = """
                Delete from category
                where category_id = %s
            """

            cursor.execute(sql, (category_id,))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="category Not Found")

            conn.commit()
            return {"message": "Deleted successfully"}

    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete this category because they have linked to Products.")

    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")