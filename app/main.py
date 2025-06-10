from fastapi import FastAPI, HTTPException, Depends, Request, Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from database.connection_db import get_session
from fastapi.templating import Jinja2Templates
import os

from app.cosmetic_models import *
from bucket.upload_images import save_file
from app.videogame_models import *
from app.cosmetic_operations import CosmeticOperations
from app.videogame_operations import VideogameOperations

app = FastAPI(
    title="Colaboraciones Maquillaje y Videojuegos",
    description="API para gestionar colaboraciones entre marcas de 👄 **maquillaje** 💄 y 🕹️ **videojuegos** 🎮.",
    version="La mejor"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))

# Página de inicio
@app.get("/", response_class=HTMLResponse, tags=["Página Principal"])
async def root(
        request: Request,
        session: AsyncSession = Depends(get_session)
):
    # Obtener todos los registros de cosméticos
    cosmetics = await CosmeticOperations.get_all_cosmetics(session)
    # Obtener todos los registros de videojuegos
    games = await VideogameOperations.get_all_videogames(session)

    # Combinar las dos listas
    all_images = list(cosmetics) + list(games)

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "all_images": all_images
        }
    )

# --------------- ELIMINADOS -----------
@app.get("/cosmetics/deleted", response_model=List[DeletedCosmeticColab], tags=["Eliminados"])
async def get_deleted_cosmetics(session: AsyncSession = Depends(get_session)):
    """Obtiene todos los cosméticos eliminados"""
    return await CosmeticOperations.get_deleted_cosmetics(session)


@app.get("/videogames/deleted", response_model=List[DeletedVideogameColab], tags=["Eliminados"])
async def get_deleted_videogames(session: AsyncSession = Depends(get_session)):
    """Obtiene todos los videojuegos eliminados"""
    return await VideogameOperations.get_deleted_videogames(session)


@app.get("/deleted", response_class=HTMLResponse, tags=["Eliminados"])
async def view_deleted(request: Request, session: AsyncSession = Depends(get_session)):
    deleted_cosmetics = await CosmeticOperations.get_deleted_cosmetics(session)
    deleted_videogames = await VideogameOperations.get_deleted_videogames(session)

    return templates.TemplateResponse(
        "deleted.html",
        {
            "request": request,
            "deleted_cosmetics": deleted_cosmetics,
            "deleted_videogames": deleted_videogames
        }
    )

@app.get("/delete", response_class=HTMLResponse, tags=["Eliminación"])
async def delete_page(request: Request):
    """Página para eliminar registros"""
    return templates.TemplateResponse("delete.html", {"request": request})

# -------------------- COSMETICS --------------------

@app.get("/cosmetics", response_class=HTMLResponse, tags=["Maquillaje"])
async def get_cosmetics(request: Request, session: AsyncSession = Depends(get_session)):
    records = await CosmeticOperations.get_all_cosmetics(session)
    return templates.TemplateResponse(
        "records.html",
        {
            "request": request,
            "records": records,
            "tipo": "cosmetics"
        }
    )

@app.get("/cosmetics/search_by_brand", response_model=List[CosmeticColabResponse], tags=["Maquillaje"])
async def search_by_brand(marca_maquillaje: str, session: AsyncSession = Depends(get_session)):
    results = await CosmeticOperations.search_cosmetics_by_brand(session, marca_maquillaje)
    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron colaboraciones con esa marca")
    return results

@app.get("/cosmetics/search_by_field", response_model=List[CosmeticColabResponse], tags=["Maquillaje"])
async def search_cosmetic_by_field(
    field: str,
    value: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Busca colaboraciones cosméticas por cualquier campo especificado.
    Campos disponibles: marca_maquillaje, videojuego, fecha_colaboracion, tipo_colaboracion, incremento_ventas_maquillaje, image_url
    """
    results = await CosmeticOperations.search_cosmetic_by_field(session, field, value)
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron colaboraciones con {field} que contenga '{value}'"
        )
    return results

@app.get("/cosmetics/by_date", response_model=List[CosmeticColabResponse], tags=["Maquillaje"])
async def get_cosmetics_by_recent_date(session: AsyncSession = Depends(get_session)):
    return await CosmeticOperations.filter_by_recent_date(session)

@app.get("/cosmetics/{cosmetic_id}", response_model=CosmeticColabResponse, tags=["Maquillaje"])
async def get_cosmetic(cosmetic_id: int, session: AsyncSession = Depends(get_session)):
    cosmetic = await CosmeticOperations.get_cosmetic_by_id(session, cosmetic_id)
    if not cosmetic:
        raise HTTPException(status_code=404, detail="Colaboración de maquillaje no encontrada")
    return cosmetic

@app.post("/cosmetics", response_model=CosmeticColabResponse, tags=["Maquillaje"])
async def create_cosmetic_endpoint(cosmetic: CosmeticColabCreate, session: AsyncSession = Depends(get_session)):
    return await CosmeticOperations.create_cosmetic(session, cosmetic.model_dump())


@app.put("/cosmetics/{cosmetic_id}", response_model=CosmeticColabResponse, tags=["Maquillaje"])
async def update_cosmetic_endpoint(
        cosmetic_id: int,
        marca_maquillaje: str = Form(None),
        videojuego: str = Form(None),
        fecha_colaboracion: str = Form(None),
        tipo_colaboracion: str = Form(None),
        incremento_ventas_maquillaje: str = Form(None),
        image_file: UploadFile = None,
        session: AsyncSession = Depends(get_session)
):
    """
    Actualiza un registro de colaboración de maquillaje.
    Solo los campos enviados en la solicitud serán actualizados.
    """
    update_data = {}

    # Recopilar campos no nulos
    if marca_maquillaje: update_data["marca_maquillaje"] = marca_maquillaje
    if videojuego: update_data["videojuego"] = videojuego
    if fecha_colaboracion: update_data["fecha_colaboracion"] = fecha_colaboracion
    if tipo_colaboracion: update_data["tipo_colaboracion"] = tipo_colaboracion
    if incremento_ventas_maquillaje: update_data["incremento_ventas_maquillaje"] = incremento_ventas_maquillaje

    # Si hay una nueva imagen, procesarla
    if image_file and image_file.filename:
        image_url = await save_file(image_file)
        if isinstance(image_url, dict) and "error" in image_url:
            raise HTTPException(status_code=400, detail=image_url["error"])
        update_data["image_url"] = image_url

    updated = await CosmeticOperations.update_cosmetic(session, cosmetic_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="La colaboración no fue actualizada")
    return updated


@app.post("/cosmetics/upload", tags=["Maquillaje"])
async def create_cosmetic_with_image(
    marca_maquillaje: str = Form(...),
    videojuego: str = Form(...),
    fecha_colaboracion: str = Form(...),
    tipo_colaboracion: str = Form(...),
    incremento_ventas_maquillaje: str = Form(...),
    image_file: UploadFile = Form(...),
    session: AsyncSession = Depends(get_session)
):
    image_url = await save_file(image_file)
    if isinstance(image_url, dict) and "error" in image_url:
        raise HTTPException(status_code=400, detail=image_url["error"])

    new_data = CosmeticColabCreate(
        marca_maquillaje=marca_maquillaje,
        videojuego=videojuego,
        fecha_colaboracion=fecha_colaboracion,
        tipo_colaboracion=tipo_colaboracion,
        incremento_ventas_maquillaje=incremento_ventas_maquillaje,
        image_url=image_url
    )

    new_colab = CosmeticColab.from_orm(new_data)
    session.add(new_colab)
    await session.commit()
    await session.refresh(new_colab)

    return {"id": new_colab.id}

@app.post("/cosmetics/delete", tags=["Maquillaje"])
async def delete_cosmetic_by_id(
    request: Request,
    id: int = Form(...),
    session: AsyncSession = Depends(get_session)
):
    deleted = await CosmeticOperations.delete_cosmetic(session, id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="El registro de cosmético no fue encontrado"
        )
    return {"message": "Registro de cosmético eliminado con éxito"}


# -------------------- VIDEOGAMES --------------------

@app.get("/videogames", response_class=HTMLResponse, tags=["Videojuegos"])
async def get_videogames(request: Request, session: AsyncSession = Depends(get_session)):
    records = await VideogameOperations.get_all_videogames(session)
    return templates.TemplateResponse(
        "records.html",
        {
            "request": request,
            "records": records,
            "tipo": "videogames"
        }
    )

@app.get("/videogames/search_by_name", response_model=List[VideogameColabResponse], tags=["Videojuegos"])
async def search_by_name(nombre_videojuego: str, session: AsyncSession = Depends(get_session)):
    results = await VideogameOperations.search_videogames_by_name(session, nombre_videojuego)
    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron colaboraciones con ese videojuego")
    return results

@app.get("/videogames/search_by_field", response_model=List[VideogameColabResponse], tags=["Videojuegos"])
async def search_videogame_by_field(
    field: str,
    value: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Busca colaboraciones de videojuegos por cualquier campo especificado.
    Campos disponibles: videojuego, marca_maquillaje, fecha_colaboracion, incremento_ventas_videojuego, image_url
    """
    results = await VideogameOperations.search_videogame_by_field(session, field, value)
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron colaboraciones con {field} que contenga '{value}'"
        )
    return results

@app.get("/videogames/by_date", response_model=List[VideogameColabResponse], tags=["Videojuegos"])
async def get_videogames_by_recent_date(session: AsyncSession = Depends(get_session)):
    return await VideogameOperations.filter_by_recent_date(session)

@app.get("/videogames/{videogame_id}", response_model=VideogameColabResponse, tags=["Videojuegos"])
async def get_videogame(videogame_id: int, session: AsyncSession = Depends(get_session)):
    videogame = await VideogameOperations.get_videogame_by_id(session, videogame_id)
    if not videogame:
        raise HTTPException(status_code=404, detail="Colaboración de videojuego no encontrada")
    return videogame

@app.post("/videogames", response_model=VideogameColabResponse, tags=["Videojuegos"])
async def create_videogame_endpoint(videogame: VideogameColabCreate, session: AsyncSession = Depends(get_session)):
    return await VideogameOperations.create_videogame(session, videogame.model_dump())

@app.put("/videogames/{videogame_id}", response_model=VideogameColabResponse, tags=["Videojuegos"])
async def update_videogame_endpoint(
        videogame_id: int,
        videojuego: str = Form(None),
        marca_maquillaje: str = Form(None),
        fecha_colaboracion: str = Form(None),
        incremento_ventas_videojuego: str = Form(None),
        image_file: UploadFile = None,
        session: AsyncSession = Depends(get_session)
):
    """
    Actualiza un registro de colaboración de videojuegos.
    Solo los campos enviados en la solicitud serán actualizados.
    """
    update_data = {}

    # Recopilar campos no nulos
    if videojuego: update_data["videojuego"] = videojuego
    if marca_maquillaje: update_data["marca_maquillaje"] = marca_maquillaje
    if fecha_colaboracion: update_data["fecha_colaboracion"] = fecha_colaboracion
    if incremento_ventas_videojuego: update_data["incremento_ventas_videojuego"] = incremento_ventas_videojuego

    # Si hay una nueva imagen, procesarla
    if image_file and image_file.filename:
        image_url = await save_file(image_file)
        if isinstance(image_url, dict) and "error" in image_url:
            raise HTTPException(status_code=400, detail=image_url["error"])
        update_data["image_url"] = image_url

    updated = await VideogameOperations.update_videogame(session, videogame_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="La colaboración en videojuegos no fue actualizada")
    return updated


@app.post("/videogames/upload", tags=["Videojuegos"])
async def create_videogame_with_image(
    videojuego: str = Form(...),
    marca_maquillaje: str = Form(...),
    fecha_colaboracion: str = Form(...),
    incremento_ventas_videojuego: str = Form(...),
    image_file: UploadFile = Form(...),
    session: AsyncSession = Depends(get_session)
):
    image_url = await save_file(image_file)
    if isinstance(image_url, dict) and "error" in image_url:
        raise HTTPException(status_code=400, detail=image_url["error"])

    new_data = VideogameColabCreate(
        videojuego=videojuego,
        marca_maquillaje=marca_maquillaje,
        fecha_colaboracion=fecha_colaboracion,
        incremento_ventas_videojuego=incremento_ventas_videojuego,
        image_url=image_url
    )

    new_colab = VideogameColab.from_orm(new_data)
    session.add(new_colab)
    await session.commit()
    await session.refresh(new_colab)

    return {"id": new_colab.id}


@app.post("/videogames/delete", tags=["Eliminación"])
async def delete_videogame_by_id(
    request: Request,
    id: int = Form(...),
    session: AsyncSession = Depends(get_session)
):
    deleted = await VideogameOperations.delete_videogame(session, id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="El registro de videojuego no fue encontrado"
        )
    return {"message": "Registro de videojuego eliminado con éxito"}

# -------------- MOSTRAR REGISTROS ----------------
@app.get("/show", response_class=HTMLResponse, tags=["Registros"])
async def show_records(
        request: Request,
        session: AsyncSession = Depends(get_session)
):
    cosmetics = await CosmeticOperations.get_all_cosmetics(session)
    games = await VideogameOperations.get_all_videogames(session)

    return templates.TemplateResponse(
        "show.html",
        {
            "request": request,
            "cosmetics": cosmetics,
            "games": games
        }
    )

# -------------------- CREACIÓN --------------------
@app.get("/create", response_class=HTMLResponse, tags=["Creación"])
async def create_page(request: Request):
    """Página para crear nuevos registros"""
    return templates.TemplateResponse("create.html", {"request": request})

# --------------- ACTUALIZACIÓN -----------
@app.get("/update", response_class=HTMLResponse, tags=["Actualización"])
async def update_page(request: Request):
    return templates.TemplateResponse("update.html", {"request": request})

# --------------- CONSULTAS -----------
@app.get("/query", response_class=HTMLResponse, tags=["Consultas"])
async def query_page(request: Request):
    return templates.TemplateResponse("query.html", {"request": request})

# --------------- DESARROLLADOR -----------
@app.get("/developer", response_class=HTMLResponse, tags=["Info Desarrollador"])
async def developer_info(request: Request):
    return templates.TemplateResponse("developer.html", {"request": request})

# --------------- PROYECTO ----------------
@app.get("/goal", response_class=HTMLResponse, tags=["Info Proyecto"])
async def objetivo_proyecto(request: Request):
    return templates.TemplateResponse("goal.html", {"request": request})

# --------------- PLANEACIÓN ----------------
@app.get("/planning", response_class=HTMLResponse, tags=["Planeación"])
async def planeacion_proyecto(request: Request):
    return templates.TemplateResponse("planning.html", {"request":request})

# --------------- DISEÑO ----------------
@app.get("/design", response_class=HTMLResponse, tags=["Diseño"])
async def diseno_proyecto(request: Request):
    return templates.TemplateResponse("design.html", {"request":request})
