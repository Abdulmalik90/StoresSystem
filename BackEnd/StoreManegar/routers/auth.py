import pymysql
from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from schemas.auth import GoogleLoginRequest
from utils.auth import verify_google_token, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/google")
def login_with_google(payload: GoogleLoginRequest, conn=Depends(get_db)):

    google_user = verify_google_token(payload.id_token)
    email = google_user["email"]
    sub = google_user["sub"]

    try:
        with conn.cursor() as cursor:

            sql = "SELECT eID, ename, email, erole, google_sub FROM employee WHERE email = %s"
            cursor.execute(sql, (email,))
            employee = cursor.fetchone()

            if not employee:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. Your email is not registered as an employee."
                )


            if not employee["google_sub"]:
                cursor.execute(
                    "UPDATE employee SET google_sub = %s WHERE eID = %s",
                    (sub, employee["eID"])
                )
                conn.commit()
            elif employee["google_sub"] != sub:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Google account mismatch for this employee email."
                )


            token_data = {
                "eID": employee["eID"],
                "email": employee["email"],
                "erole": employee["erole"]
            }
            access_token = create_access_token(token_data)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "employee": {
                    "eID": employee["eID"],
                    "ename": employee["ename"],
                    "email": employee["email"],
                    "erole": employee["erole"]
                }
            }
    except HTTPException:
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")