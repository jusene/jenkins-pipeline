from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from .config import config
from datetime import datetime
import sys

Base = declarative_base()
engine = create_engine(config.DATABASE_URL, 
                       echo=config.DATABASE_DEBUG,
                       pool_size=config.DATABASE_POOL,
                       max_overflow=config.DATABASE_POOL_OVERFLOW,
                       pool_timeout=config.DATABASE_POOL_TIMEOUT,
                       pool_recycle=config.DATABASE_POOL_RECYCLE)
Session = sessionmaker(bind=engine)
session = Session()


class AppDeploy(Base):
    __tablename__ = 'appdeploy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    appname = Column(String(50), nullable=False)
    project = Column(String(20), nullable=False)
    arch = Column(Enum("F", "B"), nullable=False)
    env = Column(String(10), nullable=False)
    jmx = Column(Integer, default=None)
    create_time = Column(DateTime, default=datetime.now(), nullable=False)
    update_time = Column(DateTime, default=datetime.now(), nullable=False)
    group_id = Column(Integer, ForeignKey('groupmanager.id'))
    group = relationship('GroupManager', back_populates='app')

    __table_args__ = (
        UniqueConstraint('appname', 'env', name='app_env'),
    )


class GroupManager(Base):
    __tablename__ = 'groupmanager'
    id = Column(Integer, primary_key=True, autoincrement=True)
    groupname = Column(String(50), unique=True, nullable=False)
    app = relationship('AppDeploy', uselist=False, back_populates='group')
    hosts = relationship('HostManager')


class HostManager(Base):
    __tablename__ = 'hostmanager'
    id = Column(Integer, primary_key=True, autoincrement=True)
    host = Column(String(50), nullable=True, unique=True)
    ip = Column(String(30), nullable=True)
    group_id = Column(Integer, ForeignKey('groupmanager.id'))

def create_all():
    '''
    create all tables
    '''
    Base.metadata.create_all(engine)


def drop_all():
    '''
    drop all tables
    '''
    Base.metadata.drop_all(engine)


if __name__ == "__main__":
    try:
        if sys.argv[1] == "create":
            create_all()
        elif sys.argv[1] == "drop":
            drop_all()
        else:
            raise(IndexError)
    except IndexError:
        print('Usage: {} create|drop'.format(sys.argv[0]))
