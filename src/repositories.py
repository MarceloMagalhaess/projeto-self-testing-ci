from sqlalchemy.orm import Session

from src.models import Transaction
from src.schemas import TransactionCreate


def create_transaction(db: Session, transaction: TransactionCreate):
    db_transaction = Transaction(**transaction.model_dump())

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


def get_transactions(db: Session):
    return db.query(Transaction).all()


def get_transaction_by_id(db: Session, transaction_id: int):
    return db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()


def delete_transaction(db: Session, transaction_id: int):
    transaction = get_transaction_by_id(db, transaction_id)

    if transaction:
        db.delete(transaction)
        db.commit()

    return transaction
