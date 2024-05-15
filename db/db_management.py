from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

DB_PATH = 'sqlite:///db/database.db'

engine = create_engine(DB_PATH)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
Base = declarative_base()


class Flashcard(Base):
    __tablename__ = 'flashcards'

    card_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    card_front_side = Column(String)
    card_back_side = Column(String)
    allow_hints = Column(Boolean)
    hint = Column(String)

    box_number = Column(Integer, default=1)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Добавление флэш-карты
def db_add_flashcard(user_id, front, back, allow_hints, hint):
    with session_scope() as session:
        new_flashcard = Flashcard(user_id=user_id, card_front_side=front, card_back_side=back,
                                  allow_hints=allow_hints, hint=hint)
        session.add(new_flashcard)


# Получение информации о флэш-картах
def db_get_flashcard_info(user_id):
    with session_scope() as session:
        result = session.query(Flashcard.card_id, Flashcard.card_front_side, Flashcard.card_back_side,
                               Flashcard.allow_hints,
                               Flashcard.hint, Flashcard.box_number).filter(Flashcard.user_id == user_id).all()
        return result


# Получение информации для удаления флэш-карт
def db_get_deletable_flashcard(user_id):
    with session_scope() as session:
        result = session.query(Flashcard.card_id, Flashcard.card_front_side, Flashcard.card_back_side,
                               Flashcard.hint).filter(Flashcard.user_id == user_id).all()
        return result


# Получение информации для статистики
def db_get_flashcard_for_stats(user_id, id):
    with session_scope() as session:
        result = session.query(Flashcard.card_id, Flashcard.card_front_side, Flashcard.card_back_side,
                               Flashcard.hint).filter(Flashcard.user_id == user_id, Flashcard.card_id == id).all()
        return result


# Удаление флэш-карт
def db_delete_flashcard(user_id, front, back):
    with session_scope() as session:
        session.query(Flashcard).filter(Flashcard.user_id == user_id, Flashcard.card_front_side == front,
                                        Flashcard.card_back_side == back).delete()


# Изменение номера коробки Лейтнера
def db_update_box_number(user_id, id, action):
    with session_scope() as session:
        flashcard = session.query(Flashcard).filter(Flashcard.user_id == user_id, Flashcard.card_id == id).first()
        if action == 'promote' and flashcard.box_number < 5:
            flashcard.box_number += 1
        elif action == 'demote' and flashcard.box_number > 1:
            flashcard.box_number = 1


Base.metadata.create_all(engine)
