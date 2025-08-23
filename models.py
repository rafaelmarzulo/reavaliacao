from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False, index=True)
    data = Column(Date, nullable=False)

    peso = Column(String(50), nullable=False)
    medidas = Column(Text, nullable=False)

    faltou_algo = Column(Text, nullable=False)
    gostou_mais_menos = Column(Text, nullable=False)

    meta_agua = Column(Text, nullable=False)
    alimentacao = Column(Text, nullable=False)

    melhorias = Column(Text, nullable=True)  # JSON em string
    outros_melhorias = Column(Text, nullable=True)

    pedido_especial = Column(Text, nullable=True)
    sugestao_geral = Column(Text, nullable=True)

    aceite = Column(Boolean, default=False, nullable=False)
    aceite_info = Column(Boolean, default=False, nullable=False)  # << NOVO

    created_at = Column(DateTime, nullable=False)
