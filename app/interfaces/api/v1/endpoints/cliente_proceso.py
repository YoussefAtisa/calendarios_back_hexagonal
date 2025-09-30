from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.db.database import SessionLocal
from app.interfaces.schemas.cliente_proceso import GenerarClienteProcesoRequest
from app.infrastructure.db.repositories.cliente_proceso_repository_sql import ClienteProcesoRepositorySQL
from app.infrastructure.db.repositories.proceso_repository_sql import ProcesoRepositorySQL
from app.infrastructure.db.repositories.proceso_hito_maestro_repository_sql import ProcesoHitoMaestroRepositorySQL
from app.infrastructure.db.repositories.cliente_proceso_hito_repository_sql import ClienteProcesoHitoRepositorySQL

from app.application.use_cases.cliente_proceso.crear_cliente_proceso import crear_cliente_proceso
from app.application.use_cases.cliente_proceso.generar_calendario_cliente_proceso import generar_calendario_cliente_proceso
from typing import Optional
from fastapi import Query, Depends

router = APIRouter(prefix="/cliente-procesos", tags=["ClienteProceso"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_repo(db: Session = Depends(get_db)):
    return ClienteProcesoRepositorySQL(db)

def get_repo_proceso(db: Session = Depends(get_db)):
    return ProcesoRepositorySQL(db)

def get_repo_proceso_hito_maestro(db: Session = Depends(get_db)):
    return ProcesoHitoMaestroRepositorySQL(db)

def get_repo_cliente_proceso_hito(db: Session = Depends(get_db)):
    return ClienteProcesoHitoRepositorySQL(db)

@router.post("/")
def crear(data: dict, repo = Depends(get_repo)):
    return crear_cliente_proceso(data, repo)

@router.get("/")
def listar(repo = Depends(get_repo)):
    return repo.listar()

@router.get("/{id}")
def get(id: int, repo = Depends(get_repo)):
    cliente_proceso = repo.obtener_por_id(id)
    if not cliente_proceso:
        raise HTTPException(status_code=404, detail="No encontrado")
    return cliente_proceso

@router.get("/cliente/{cliente_id}")
def get_por_cliente(cliente_id: str,
                    page: Optional[int] = Query(None, ge=1, description="Página actual"),
                    limit: Optional[int] = Query(None, ge=1, le=100, description="Cantidad de resultados por página"),
                    repo = Depends(get_repo)):

    cliente_procesos = repo.listar_por_cliente(cliente_id)
    total = len(cliente_procesos)

    if page is not None and limit is not None:
        start = (page - 1) * limit
        end = start + limit
        cliente_procesos = cliente_procesos[start:end]

    return {
        "clienteProcesos" : cliente_procesos,
        "total": total
    }

@router.delete("/{id}")
def delete(id: int, repo = Depends(get_repo)):
    ok = repo.eliminar(id)
    if not ok:
        raise HTTPException(status_code=404, detail="No encontrado")
    return {"mensaje": "Eliminado"}

router_calendario = APIRouter(prefix="", tags=["Generar Calendario"])

@router_calendario.post("/generar-calendario-cliente-proceso")
def generar_calendario_cliente_by_proceso(request: GenerarClienteProcesoRequest,
                                        repo = Depends(get_repo),
                                        proceso_repo = Depends(get_repo_proceso),
                                        repo_proceso_hito_maestro = Depends(get_repo_proceso_hito_maestro),
                                        repo_cliente_proceso_hito = Depends(get_repo_cliente_proceso_hito)):
    proceso_maestro = proceso_repo.obtener_por_id(request.proceso_id) #esto podria hacerse tambien en vez de mediante el repo, con el caso de uso...
    return generar_calendario_cliente_proceso(request,proceso_maestro, repo,repo_proceso_hito_maestro, repo_cliente_proceso_hito)
