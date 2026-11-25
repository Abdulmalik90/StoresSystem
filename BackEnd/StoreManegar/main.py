from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (employees, customers,
                     categories, suppliers, products,
                     receipts, auth)
app = FastAPI(title="Store Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(employees.router )
app.include_router(customers.router )
app.include_router(categories.router )
app.include_router(suppliers.router )
app.include_router(products.router)
app.include_router(receipts.router)
app.include_router(auth.router)
@app.get("/")
def root():
    return {"status": "API is running"}