from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    rating = Column(Float, default=1500.0)
    rd = Column(Float, default=350.0)
    volatility = Column(Float, default=0.06)

def get_engine(db_url='sqlite:///ratings.db'):
    """
    Возвращает SQLAlchemy engine.
    Можно заменить db_url на URL вашей БД.
    """
    return create_engine(db_url, echo=False)

def create_tables(engine):
    """Создает таблицы в базе, если они ещё не созданы."""
    Base.metadata.create_all(engine)

def get_session(engine):
    """Возвращает сессию SQLAlchemy."""
    Session = sessionmaker(bind=engine)
    return Session()

def get_all_users(session):
    """
    Загружает всех пользователей из таблицы.
    Возвращает список объектов User.
    """
    return session.query(User).all()

def bulk_update_users(session, ids, new_ratings, new_rds, new_vols):
    """
    Массовое обновление пользователей.
    
    :param session: SQLAlchemy session
    :param ids: список идентификаторов пользователей (порядок должен соответствовать массивам)
    :param new_ratings: массив новых рейтингов
    :param new_rds: массив новых значений RD
    :param new_vols: массив новых значений волатильности
    """
    for i, user_id in enumerate(ids):
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.rating = new_ratings[i]
            user.rd = new_rds[i]
            user.volatility = new_vols[i]
    session.commit()
