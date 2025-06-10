from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.videogame_models import *

class VideogameOperations:

    @staticmethod
    async def get_all_videogames(session: AsyncSession) -> List[VideogameColab]:
        """Obtiene todos los registros de colaboraciones de videojuegos"""
        result = await session.execute(select(VideogameColab))
        return result.scalars().all()

    @staticmethod
    async def get_videogame_by_id(session: AsyncSession, entry_id: int) -> Optional[VideogameColab]:
        """Obtiene un registro por su ID"""
        result = await session.execute(
            select(VideogameColab).where(VideogameColab.id == entry_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_videogame(session: AsyncSession, data: dict) -> VideogameColab:
        """Crea un nuevo registro de colaboración de videojuegos"""
        new_entry = VideogameColab(**data)
        session.add(new_entry)
        await session.commit()
        await session.refresh(new_entry)
        return new_entry

    @staticmethod
    async def update_videogame(session: AsyncSession, entry_id: int, update_data: dict) -> Optional[VideogameColab]:
        """Modifica un registro existente, permitiendo cambios parciales o totales"""
        entry = await session.get(VideogameColab, entry_id)
        if not entry:
            return None

        for key, value in update_data.items():
            if hasattr(entry, key):
                # Solo actualiza si el valor no es None ni una cadena vacía
                if value not in (None, ""):
                    setattr(entry, key, value)

        await session.commit()
        await session.refresh(entry)
        return entry

    @staticmethod
    async def delete_videogame(session: AsyncSession, entry_id: int) -> Optional[VideogameColab]:
        """Elimina un registro por ID y lo guarda en deleted_videogame"""
        entry = await session.get(VideogameColab, entry_id)
        if not entry:
            return None

        # Validar los datos antes de crear la copia
        try:
            deleted_entry = DeletedVideogameColab(**entry.dict())
        except ValueError as e:
            # Manejar errores de validación
            raise ValueError(f"Error al validar los datos para la tabla de eliminados: {e}")

        session.add(deleted_entry)
        await session.delete(entry)
        await session.commit()
        return entry

    @staticmethod
    async def get_deleted_videogames(session: AsyncSession) -> List[DeletedVideogameColab]:
        """Obtiene todos los registros eliminados de videojuegos"""
        result = await session.execute(select(DeletedVideogameColab))
        return result.scalars().all()

    @staticmethod
    async def search_videogames_by_name(session: AsyncSession, nombre_videojuego: str) -> List[VideogameColab]:
        """Busca registros por nombre de videojuego"""
        result = await session.execute(
            select(VideogameColab).where(VideogameColab.videojuego.ilike(f"%{nombre_videojuego}%"))
        )
        return result.scalars().all()

    @staticmethod
    async def filter_by_recent_date(session: AsyncSession) -> List[VideogameColab]:
        """Filtra y ordena por fecha más reciente primero (solo como strings)"""
        result = await session.execute(select(VideogameColab))
        all_entries = result.scalars().all()

        # Ordenar por string de fecha (formato YYYY-MM-DD)
        return sorted(all_entries, key=lambda x: x.fecha_colaboracion, reverse=True)

    @staticmethod
    async def search_videogame_by_field(session: AsyncSession, field: str, value: str) -> List[VideogameColab]:
        """Busca registros por cualquier campo especificado"""
        if not hasattr(VideogameColab, field):
            return []
        
        # Obtener el atributo del modelo
        model_field = getattr(VideogameColab, field)
        
        # Realizar la búsqueda
        result = await session.execute(
            select(VideogameColab).where(model_field.ilike(f"%{value}%"))
        )
        return result.scalars().all()