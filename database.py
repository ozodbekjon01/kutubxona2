from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Ma'lumotlar bazasi manzilini kiriting (masalan, SQLite yoki MySQL)
DATABASE_URL = "sqlite:///kutubxona.db"  # Agar MySQL bo'lsa: "mysql+pymysql://user:password@localhost/db_name"

# SQLAlchemy uchun aloqani yaratish
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# ORM model yaratish uchun asosiy sinf
Base = declarative_base()
Base.query = db_session.query_property()

# Ma'lumotlar bazasini yaratish funksiyasi
def init_db():
    import models  # Model sinflari shu joyda bo‘lishi kerak
    Base.metadata.create_all(bind=engine)
