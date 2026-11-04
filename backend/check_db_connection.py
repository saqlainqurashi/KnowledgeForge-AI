from sqlalchemy import text

from app.core.database import engine

print("Connecting to Neon PostgreSQL...", flush=True)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT version();")
        )

        print("Database connected successfully!")
        print("PostgreSQL:", result.scalar())

        vector_version = connection.execute(
            text(
                "SELECT extversion FROM pg_extension "
                "WHERE extname = 'vector';"
            )
        ).scalar()

        print("pgvector version:", vector_version)

        if vector_version is None:
            raise RuntimeError("pgvector extension is not enabled")

except Exception as exc:
    print("Database connection failed!")
    print(f"Error: {exc}")
    raise