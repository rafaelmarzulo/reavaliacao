from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import json
from datetime import datetime

from database import get_db, engine
from models import Base, Avaliacao

# cria tabelas se ainda não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Reavaliação Física", version="1.0.0")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(_: Request):
    return RedirectResponse(url="/formulario")


@app.get("/formulario", response_class=HTMLResponse)
async def formulario_get(request: Request):
    return templates.TemplateResponse("formulario.html", {"request": request})


@app.post("/formulario")
async def formulario_post(
    request: Request,
    nome: str = Form(...),
    peso: str = Form(...),
    medidas: str = Form(...),
    faltou_algo: str = Form(...),
    gostou_mais_menos: str = Form(...),
    meta_agua: str = Form(...),
    alimentacao: str = Form(...),

    melhorias: list[str] = Form([]),
    outros_melhorias: str = Form(""),
    pedido_especial: str = Form(""),
    sugestao_geral: str = Form(""),

    # 👇 novo aceite
    aceite_info: bool = Form(False),

    # aceite final já existente
    aceite: bool = Form(False),

    db: Session = Depends(get_db),
):
    melhorias_json = json.dumps(melhorias) if melhorias else "[]"

    nova_avaliacao = Avaliacao(
        nome=nome,
        data=datetime.now().date(),
        peso=peso,
        medidas=medidas,
        faltou_algo=faltou_algo,
        gostou_mais_menos=gostou_mais_menos,
        meta_agua=meta_agua,
        alimentacao=alimentacao,
        melhorias=melhorias_json,
        outros_melhorias=outros_melhorias,
        pedido_especial=pedido_especial,
        sugestao_geral=sugestao_geral,

        aceite_info=aceite_info,   # 👈 grava o novo aceite
        aceite=aceite,

        created_at=datetime.now(),
    )

    db.add(nova_avaliacao)
    db.commit()

    return templates.TemplateResponse("sucesso.html", {"request": request, "nome": nome})


@app.get("/alunos", response_class=HTMLResponse)
async def lista_alunos(request: Request, db: Session = Depends(get_db)):
    alunos = db.query(Avaliacao.nome).distinct().all()
    alunos_list = [a[0] for a in alunos]
    return templates.TemplateResponse("alunos.html", {"request": request, "alunos": alunos_list})


@app.get("/aluno/{nome}", response_class=HTMLResponse)
async def historico_aluno(request: Request, nome: str, db: Session = Depends(get_db)):
    avaliacoes = (
        db.query(Avaliacao)
        .filter(Avaliacao.nome == nome)
        .order_by(Avaliacao.data.desc())
        .all()
    )
    for av in avaliacoes:
        try:
            av.melhorias_processadas = json.loads(av.melhorias) if av.melhorias else []
        except Exception:
            av.melhorias_processadas = []
    return templates.TemplateResponse("historico.html", {"request": request, "nome": nome, "avaliacoes": avaliacoes})


@app.get("/comparar/{nome}", response_class=HTMLResponse)
async def comparar_avaliacoes(request: Request, nome: str, db: Session = Depends(get_db)):
    avaliacoes = (
        db.query(Avaliacao)
        .filter(Avaliacao.nome == nome)
        .order_by(Avaliacao.data.asc())
        .all()
    )
    for av in avaliacoes:
        try:
            av.melhorias_processadas = json.loads(av.melhorias) if av.melhorias else []
        except Exception:
            av.melhorias_processadas = []
    return templates.TemplateResponse("comparacao.html", {"request": request, "nome": nome, "avaliacoes": avaliacoes})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
