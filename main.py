from fastapi import FastAPI
from routers import clients, admin, shows
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Event Management API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],            # Allow all HTTP methods
    allow_headers=["*"],            # Allow all headers
)
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(shows.router, prefix="/api/shows", tags=["Shows"])

