from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


class Database:
    def __init__(self, conn_str):
        self.engine = create_engine(conn_str)
        self.session_maker = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.session_maker()
