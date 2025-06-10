from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import validator

class VideogameColabBase(SQLModel):
    videojuego: str = Field(..., min_length=3, max_length=50)
    marca_maquillaje: str = Field(..., min_length=3, max_length=50)
    fecha_colaboracion: str = Field(..., min_length=3, max_length=50)
    incremento_ventas_videojuego: str = Field(..., regex=r'^\d+%$')
    image_url: str = Field(..., min_length=3, max_length=500)

class VideogameColab(VideogameColabBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class VideogameColabCreate(VideogameColabBase):
    pass

class VideogameColabRead(VideogameColabBase):
    id: int

class VideogameColabUpdate(SQLModel):
    videojuego: Optional[str] = Field(None, min_length=3, max_length=50)
    marca_maquillaje: Optional[str] = Field(None, min_length=3, max_length=50)
    fecha_colaboracion: Optional[str] = Field(None, min_length=3, max_length=50)
    incremento_ventas_videojuego: Optional[str] = Field(None, regex=r'^\d+%$')
    image_url: Optional[str] = Field(None, min_length=3, max_length=500)

    @validator('*', pre=True)
    def skip_blank_strings(cls, v):
        if v == "":
            return None
        return v

class VideogameColabResponse(SQLModel):
    id: int
    videojuego: str
    marca_maquillaje: str
    fecha_colaboracion: str
    incremento_ventas_videojuego: str
    image_url: str

class DeletedVideogameColab(VideogameColabBase, table=True):
    __tablename__ = "deleted_videogame"  # Añade esto
    id: Optional[int] = Field(default=None, primary_key=True)