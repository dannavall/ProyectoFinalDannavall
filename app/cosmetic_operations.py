from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from app.cosmetic_models import *

class CosmeticOperations:

    @staticmethod
    async def get_all_cosmetics(session: AsyncSession) -> List[CosmeticColab]:
        """Obtiene todos los registros de colaboraciones cosméticas"""
        result = await session.execute(select(CosmeticColab))
        return result.scalars().all()

    @staticmethod
    async def get_cosmetic_by_id(session: AsyncSession, entry_id: int) -> Optional[CosmeticColab]:
        """Obtiene un registro por su ID"""
        result = await session.execute(
            select(CosmeticColab).where(CosmeticColab.id == entry_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_cosmetic(session: AsyncSession, data: dict) -> CosmeticColab:
        """Crea un nuevo registro de colaboración cosmética"""
        new_entry = CosmeticColab(**data)
        session.add(new_entry)
        await session.commit()
        await session.refresh(new_entry)
        return new_entry

    @staticmethod
    async def update_cosmetic(session: AsyncSession, entry_id: int, update_data: dict) -> Optional[CosmeticColab]:
        """Modifica un registro existente, permitiendo cambios parciales o totales"""
        entry = await session.get(CosmeticColab, entry_id)
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
    async def delete_cosmetic(session: AsyncSession, entry_id: int) -> Optional[CosmeticColab]:
        """Elimina un registro por ID y lo guarda en deleted_cosmetic"""
        entry = await session.get(CosmeticColab, entry_id)
        if not entry:
            return None

        # Validar los datos antes de crear la copia
        try:
            deleted_entry = DeletedCosmeticColab(**entry.dict())
        except ValueError as e:
            # Manejar errores de validación
            raise ValueError(f"Error al validar los datos para la tabla de eliminados: {e}")

        session.add(deleted_entry)
        await session.delete(entry)
        await session.commit()
        return entry

    @staticmethod
    async def get_deleted_cosmetics(session: AsyncSession) -> List[DeletedCosmeticColab]:
        """Obtiene todos los registros eliminados de cosméticos"""
        result = await session.execute(select(DeletedCosmeticColab))
        return result.scalars().all()

    @staticmethod
    async def search_cosmetics_by_brand(session: AsyncSession, brand_name: str) -> List[CosmeticColab]:
        """Busca registros por marca de maquillaje"""
        result = await session.execute(
            select(CosmeticColab).where(CosmeticColab.marca_maquillaje.ilike(f"%{brand_name}%"))
        )
        return result.scalars().all()

    @staticmethod
    async def filter_by_recent_date(session: AsyncSession) -> List[CosmeticColab]:
        """Filtra y ordena por fecha más reciente primero"""
        result = await session.execute(
            select(CosmeticColab).order_by(CosmeticColab.fecha_colaboracion.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def search_cosmetic_by_field(session: AsyncSession, field: str, value: str) -> List[CosmeticColab]:
        """Busca registros por cualquier campo especificado"""
        if not hasattr(CosmeticColab, field):
            return []
        
        # Obtener el atributo del modelo
        model_field = getattr(CosmeticColab, field)
        
        # Realizar la búsqueda
        result = await session.execute(
            select(CosmeticColab).where(model_field.ilike(f"%{value}%"))
        )
        return result.scalars().all()