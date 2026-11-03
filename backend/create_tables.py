from app.core.database import Base, engine
import app.models  # noqa: F401

print("Creating database tables...", flush=True)

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")