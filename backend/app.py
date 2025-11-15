from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Route modules
from .routes.admin_routes import router as admin_router
from .routes.voter_routes import router as voter_router
from .routes.election import router as election_router

# Database
from .database.session import Base, engine


# --------------------------------------------------------
# Initialize Database
# --------------------------------------------------------

def create_tables():
    """
    Creates all database tables on startup if they don’t exist.
    """
    Base.metadata.create_all(bind=engine)


# --------------------------------------------------------
# FastAPI App
# --------------------------------------------------------

app = FastAPI(
    title="VoteChain",
    description="A local-network blockchain-backed voting platform.",
    version="1.0.0"
)

# Allow all origins for LAN use (can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # allow local devices
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------
# Attach Routes
# --------------------------------------------------------

app.include_router(admin_router)
app.include_router(voter_router)
app.include_router(election_router)


# --------------------------------------------------------
# Startup Hook
# --------------------------------------------------------

@app.on_event("startup")
def startup():
    create_tables()
    print("[VoteChain] Database initialized. Server ready.")


# --------------------------------------------------------
# Root Test Endpoint
# --------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "VoteChain backend is running.",
        "docs": "/docs",
        "admin": "/admin",
        "voter": "/voter"
    }
