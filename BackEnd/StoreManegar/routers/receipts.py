from decimal import Decimal
import uuid
import pymysql
from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from schemas.receipt import ReceiptCreate, ReceiptUpdate

router = APIRouter(prefix="/receipts", tags=["Receipts"])

#Create a Receipt
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_receipt(receipt: ReceiptCreate, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            rid = str(uuid.uuid4())
            total_discount = Decimal("0.00")
            total_price = Decimal("0.00")
            prepared_items = []

            for item in receipt.items:
                sql_check = "SELECT price, discount, quantity from product where pid = %s for update"
                cursor.execute(sql_check, (item.pid,))
                product = cursor.fetchone()

                if not product:
                    conn.rollback()
                    raise HTTPException(status_code=404, detail=f"Product {item.pid} not found")

                if product["quantity"] < item.quantity:
                    conn.rollback()
                    raise HTTPException(status_code=400, detail=f"Insufficient quantity for product {item.pid}")

                unit_price = product["price"]
                unit_discount = product["discount"] or Decimal("0.00")
                price_at_sale = unit_price - unit_discount

                total_discount += unit_discount * item.quantity
                total_price += price_at_sale * item.quantity

                prepared_items.append({
                    "pid": item.pid,
                    "quantity_sold": item.quantity,
                    "price_at_sale": price_at_sale
                })

            sql_order = """
                INSERT INTO receipt (rid, totaldiscount, totalprice, cid, eid)
                    values (%s, %s, %s, %s, %s)
            """

            cursor.execute(sql_order, (rid, total_discount, total_price, receipt.cid, receipt.eid))

            sql_item = """
                INSERT INTO receipt_product (rid, pid, quantity_sold, price_at_sale)
                values (%s, %s, %s, %s)
            """

            sql_update_quantity = "UPDATE product set quantity = quantity - %s where pid = %s"
            for p_item in prepared_items:
                cursor.execute(sql_item, (rid, p_item["pid"], p_item["quantity_sold"], p_item["price_at_sale"]))
                cursor.execute(sql_update_quantity, (p_item["quantity_sold"], p_item["pid"]))

            conn.commit()
            return {
                "message": "Receipt Created Successfully",
                "receipt_id": rid,
                "total_discount": total_discount,
                "total_price": total_price

            }
    except HTTPException:
        raise
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Invalid customer_id, employee_id, or duplicate item in receipt.")
    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/")
def get_receipt(search: str | None = None, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            base_sql = """
                SELECT r.rid, r.rdate, r.totaldiscount, r.totalprice,
                       r.cid, c.cname,
                       r.eid, e.ename
                FROM receipt r
                JOIN customer c ON r.cid = c.cid
                JOIN employee e ON r.eid = e.eid
            """
            if search:
                sql = base_sql + " WHERE r.rid LIKE %s OR c.cname LIKE %s OR e.ename LIKE %s"
                pattern = f"%{search}%"
                cursor.execute(sql, (pattern, pattern, pattern))
            else:
                cursor.execute(base_sql)
            return cursor.fetchall()
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@router.get("/{rid}")
def get_receipt_details(rid: str, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:

            sql_order = """
                SELECT r.rid, r.rdate, r.totaldiscount, r.totalprice,
                       r.cid, c.cname,
                       r.eid, e.ename
                FROM receipt r
                JOIN customer c ON r.cid = c.cid
                JOIN employee e ON r.eid = e.eid
                WHERE r.rid = %s
            """
            cursor.execute(sql_order, (rid,))
            reciept = cursor.fetchone()

            if not reciept:
                raise HTTPException(status_code=404, detail="Receipt not found")


            sql_items = """
                SELECT rp.pid, p.pname, rp.quantity_sold, rp.price_at_sale
                FROM receipt_product rp
                JOIN product p ON rp.pid = p.pid
                WHERE rp.rid = %s
            """
            cursor.execute(sql_items, (rid,))
            reciept["items"] = cursor.fetchall()

            return reciept
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/{rid}")
def update_receipt(rid: str, reciept: ReceiptUpdate, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE receipt SET cid = %s, eid = %s WHERE rid = %s"
            cursor.execute(sql, (reciept.cid, reciept.eid, rid))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Receipt not found")
            conn.commit()
            return {"message": "Receipt updated successfully"}
    except pymysql.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Invalid customer_id or employee_id.")
    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/{rid}")
def delete_order(rid: str, conn=Depends(get_db)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT pid, quantity_sold FROM receipt_product WHERE rid = %s", (rid,))
            items = cursor.fetchall()


            for item in items:
                cursor.execute(
                    "UPDATE product SET quantity = quantity + %s WHERE pid = %s",
                    (item["quantity_sold"], item["pid"])
                )


            cursor.execute("DELETE FROM receipt_product WHERE rid = %s", (rid,))


            cursor.execute("DELETE FROM receipt WHERE rid = %s", (rid,))
            if cursor.rowcount == 0:
                conn.rollback()
                raise HTTPException(status_code=404, detail="Receipt not found")

            conn.commit()
            return {"message": "Receipt deleted and Quantity restored successfully"}
    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")