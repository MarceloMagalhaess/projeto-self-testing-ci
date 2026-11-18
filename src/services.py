from sqlalchemy.orm import Session

from src import repositories
from src.schemas import TransactionCreate


def create_transaction(db: Session, transaction: TransactionCreate):

    if transaction.amount <= 0:
        raise ValueError("O valor deve ser maior que zero.")

    if transaction.transaction_type not in ["income", "expense"]:
        raise ValueError("Tipo de transação inválido.")

    return repositories.create_transaction(db, transaction)


def get_transactions(db: Session):
    return repositories.get_transactions(db)


def get_transaction_by_id(db: Session, transaction_id: int):
    return repositories.get_transaction_by_id(db, transaction_id)


def delete_transaction(db: Session, transaction_id: int):
    return repositories.delete_transaction(db, transaction_id)
    