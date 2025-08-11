from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    data = Column(Date, nullable=False)
    peso = Column(String(20), nullable=False)
    medidas = Column(Text, nullable=False)              # Pescoço, Cintura, Quadril
    faltou_algo = Column(Text, nullable=False)          # Faltas no treino
    gostou_mais_menos = Column(Text, nullable=False)    # Aspectos positivos e negativos
    meta_agua = Column(Text, nullable=False)            # Meta de ingestão de água
    alimentacao = Column(Text, nullable=False)          # Alimentação e dificuldades
    melhorias = Column(Text, nullable=True)             # Itens de melhora (JSON)
    outros_melhorias = Column(Text, nullable=True)      # Texto livre de melhorias extras
    pedido_especial = Column(Text, nullable=True)       # Pedido para próximo treino
    sugestao_geral = Column(Text, nullable=True)        # Sugestões ou observações

    # Aceites
    aceite_info = Column(Boolean, default=False, nullable=False)  # Aceite sobre envio de fotos (novo)
    aceite = Column(Boolean, default=False, nullable=False)       # Declaração final

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Avaliacao(id={self.id}, nome='{self.nome}', data='{self.data}')>"
