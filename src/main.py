from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import Base, engine, SessionLocal
from src import services
from src.schemas import TransactionCreate, TransactionResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wallet API",
    description="API de controle financeiro pessoal",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/transactions/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    try:
        return services.create_transaction(db, transaction)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/transactions/", response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return services.get_transactions(db)


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = services.get_transaction_by_id(db, transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    return transaction


@app.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = services.delete_transaction(db, transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    return {"message": "Transação removida com sucesso"}
