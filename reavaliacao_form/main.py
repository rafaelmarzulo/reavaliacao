from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from datetime import date
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/formulario", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("formulario.html", {"request": request})

@app.post("/formulario", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    nome: str = Form(...),
    data: date = Form(...),
    peso: str = Form(...),
    medidas: str = Form(...),
    faltou_algo: str = Form(...),
    gostou_mais_menos: str = Form(...),
    meta_agua: str = Form(...),
    alimentacao: str = Form(...),
    melhorias: List[str] = Form(...),
    outros_melhorias: Optional[str] = Form(""),
    pedido_especial: str = Form(...),
    sugestao_geral: Optional[str] = Form(""),
    aceite: Optional[str] = Form(...)
):
    return templates.TemplateResponse("formulario.html", {
        "request": request,
        "submitted": True,
        "dados": {
            "nome": nome,
            "data": data,
            "peso": peso,
            "medidas": medidas,
            "faltou_algo": faltou_algo,
            "gostou_mais_menos": gostou_mais_menos,
            "meta_agua": meta_agua,
            "alimentacao": alimentacao,
            "melhorias": melhorias,
            "outros_melhorias": outros_melhorias,
            "pedido_especial": pedido_especial,
            "sugestao_geral": sugestao_geral,
            "aceite": aceite
        }
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
