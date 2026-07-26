"""Create all warehouse tables. Run once after `docker compose up -d`."""
from database.connection import engine
from database.models import Base


def init_db() -> None:
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("Warehouse schema created.")
