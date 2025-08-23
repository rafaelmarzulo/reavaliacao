import os
import json
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER

from passlib.hash import bcrypt
from dotenv import load_dotenv

from database import get_db, engine
from models import Base, Avaliacao
from sqlalchemy.orm import Session

# --- Carrega env ---
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-CHANGE-ME")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
# Pode usar ADMIN_PASSWORD_HASH (bcrypt) OU ADMIN_PASSWORD (texto plano)
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
ADMIN_PASSWORD_PLAIN = os.getenv("ADMIN_PASSWORD")

# --- DB: cria tabelas se não existirem ---
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Reavaliação Física", version="1.1.1")

# Sessões (cookies)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Estáticos
# Compatibilidade com templates que usam url_for('static', path='css/theme.css')
app.mount("/static", StaticFiles(directory="static"), name="static")
# Acesso curto direto (se você referir /css/... e /img/... no HTML)
app.mount("/css", StaticFiles(directory="static/css"), name="css")
app.mount("/img", StaticFiles(directory="static/img"), name="img")

# Templates
templates = Jinja2Templates(directory="templates")


# -------------------- Auth helpers --------------------
def verify_admin(email: str, password: str) -> bool:
    if email.strip().lower() != ADMIN_EMAIL.strip().lower():
        return False
    if ADMIN_PASSWORD_HASH:
        return bcrypt.verify(password, ADMIN_PASSWORD_HASH)
    if ADMIN_PASSWORD_PLAIN:
        return password == ADMIN_PASSWORD_PLAIN
    # fallback dev
    return password == "admin"


def require_login(request: Request) -> Optional[RedirectResponse]:
    if not request.session.get("user"):
        nxt = str(request.url)
        return RedirectResponse(url=f"/login?next={nxt}", status_code=HTTP_303_SEE_OTHER)
    return None


# -------------------- Rotas públicas --------------------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/formulario", status_code=HTTP_303_SEE_OTHER)


@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request, next: Optional[str] = None):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "next": next or "/alunos"}
    )


@app.post("/login")
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: Optional[str] = Form(None),
):
    if verify_admin(email, password):
        request.session["user"] = email
        return RedirectResponse(url=(next or "/alunos"), status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "next": next or "/alunos", "error": "Credenciais inválidas."},
        status_code=400
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)


# -------------------- Formulário --------------------
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
    melhorias: List[str] = Form(default=[]),
    outros_melhorias: str = Form(""),
    pedido_especial: str = Form(""),
    sugestao_geral: str = Form(""),
    aceite: bool = Form(False),
    aceite_info: bool = Form(False),
    db: Session = Depends(get_db)
):
    melhorias_json = json.dumps(melhorias or [])

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
        aceite=aceite,
        aceite_info=aceite_info,
        created_at=datetime.now()
    )
    db.add(nova_avaliacao)
    db.commit()

    return templates.TemplateResponse("sucesso.html", {"request": request, "nome": nome})


# -------------------- Relatórios (protegidos) --------------------
@app.get("/alunos", response_class=HTMLResponse)
async def lista_alunos(request: Request, db: Session = Depends(get_db)):
    redir = require_login(request)
    if redir:
        return redir

    alunos = db.query(Avaliacao.nome).distinct().all()
    alunos_list = [a[0] for a in alunos]
    return templates.TemplateResponse("alunos.html", {"request": request, "alunos": alunos_list})


@app.get("/aluno/{nome}", response_class=HTMLResponse)
async def historico_aluno(request: Request, nome: str, db: Session = Depends(get_db)):
    redir = require_login(request)
    if redir:
        return redir

    avaliacoes = (
        db.query(Avaliacao)
        .filter(Avaliacao.nome == nome)
        .order_by(Avaliacao.data.desc())
        .all()
    )

    for av in avaliacoes:
        try:
            av.melhorias_processadas = json.loads(av.melhorias or "[]")
        except Exception:
            av.melhorias_processadas = []

    return templates.TemplateResponse(
        "historico.html", {"request": request, "nome": nome, "avaliacoes": avaliacoes}
    )


@app.get("/comparar/{nome}", response_class=HTMLResponse)
async def comparar_avaliacoes(request: Request, nome: str, db: Session = Depends(get_db)):
    redir = require_login(request)
    if redir:
        return redir

    avaliacoes = (
        db.query(Avaliacao)
        .filter(Avaliacao.nome == nome)
        .order_by(Avaliacao.data.asc())
        .all()
    )

    for av in avaliacoes:
        try:
            av.melhorias_processadas = json.loads(av.melhorias or "[]")
        except Exception:
            av.melhorias_processadas = []

    return templates.TemplateResponse(
        "comparacao.html", {"request": request, "nome": nome, "avaliacoes": avaliacoes}
    )


# -------------------- PDF (protegido) --------------------
@app.get("/aluno/{nome}/pdf")
async def pdf_aluno(request: Request, nome: str, db: Session = Depends(get_db)):
    redir = require_login(request)
    if redir:
        return redir

    from weasyprint import HTML  # import tardio

    avaliacoes = (
        db.query(Avaliacao)
        .filter(Avaliacao.nome == nome)
        .order_by(Avaliacao.data.asc())
        .all()
    )
    for av in avaliacoes:
        try:
            av.melhorias_processadas = json.loads(av.melhorias or "[]")
        except Exception:
            av.melhorias_processadas = []

    # Renderiza HTML do relatório
    tpl = templates.get_template("relatorio.html")
    html_str = tpl.render({"request": request, "nome": nome, "avaliacoes": avaliacoes})

    # Base para resolver /static, /css e /img
    base_url = str(request.base_url)
    pdf_bytes = HTML(string=html_str, base_url=base_url).write_pdf()

    filename = f"relatorio-{nome.replace(' ', '_')}.pdf"
    headers = {"Content-Disposition": f'inline; filename="{filename}"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


# -------------------- Healthcheck --------------------
@app.get("/healthz")
async def healthz():
    return {"ok": True}
