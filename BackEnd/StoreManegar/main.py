from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import employees, customers, categories, suppliers
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

@app.get("/")
def root():
    return {"status": "API is running"}