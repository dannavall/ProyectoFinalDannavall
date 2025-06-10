from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import validator

class CosmeticColabBase(SQLModel):
    marca_maquillaje: str = Field(..., min_length=3, max_length=50)
    videojuego: str = Field(..., min_length=3, max_length=50)
    fecha_colaboracion: str = Field(..., min_length=3, max_length=50)
    tipo_colaboracion: str = Field(..., min_length=3, max_length=100)
    incremento_ventas_maquillaje: str = Field(..., regex=r'^\d+%$')
    image_url: str = Field(..., min_length=3, max_length=500)

class CosmeticColab(CosmeticColabBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class CosmeticColabCreate(CosmeticColabBase):
    pass

class CosmeticColabRead(CosmeticColabBase):
    id: int

class CosmeticColabUpdate(SQLModel):
    marca_maquillaje: Optional[str] = Field(None, min_length=3, max_length=50)
    videojuego: Optional[str] = Field(None, min_length=3, max_length=50)
    fecha_colaboracion: Optional[str] = Field(None, min_length=3, max_length=50)
    tipo_colaboracion: Optional[str] = Field(None, min_length=3, max_length=100)
    incremento_ventas_maquillaje: Optional[str] = Field(None, regex=r'^\d+%$')
    image_url: Optional[str] = Field(None, min_length=3, max_length=500)

    @validator('*', pre=True)
    def skip_blank_strings(cls, v):
        if v == "":
            return None
        return v

class CosmeticColabResponse(SQLModel):
    id: int
    marca_maquillaje: str
    videojuego: str
    fecha_colaboracion: str
    tipo_colaboracion: str
    incremento_ventas_maquillaje: str
    image_url: str

class DeletedCosmeticColab(CosmeticColabBase, table=True):
    __tablename__ = "deleted_cosmetic"
    id: Optional[int] = Field(default=None, primary_key=True)