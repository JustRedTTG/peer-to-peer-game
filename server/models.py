import bcrypt
from sqlalchemy import Column, String, DateTime, func, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
import os

connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String)
    created_at = Column(DateTime, default=func.now())
    hashed_password = Column(String(60), nullable=False)

    def __init__(self, *args, **kwargs):
        try:
            password = kwargs.pop('password')
        except KeyError:
            raise ValueError('Password is required')
        kwargs['hashed_password'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        super().__init__(*args, **kwargs)

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))


engine = create_engine(connection_string)

Base.metadata.create_all(engine)
