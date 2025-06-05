import csv
from sqlmodel import Field, SQLModel, create_engine, Session
from typing import Optional

class CosmeticColab(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    marca_maquillaje: str = Field(..., min_length=3, max_length=50)
    videojuego: str = Field(..., min_length=3, max_length=50)
    fecha_colaboracion: str = Field(..., min_length=3, max_length=50)
    tipo_colaboracion: str = Field(..., min_length=3, max_length=100)
    incremento_ventas_maquillaje: str = Field(..., regex=r'^\d+%$')
    image_url: str = Field(..., min_length=3, max_length=500)

DATABASE_URL = "postgresql://ubneujbnk1lslhezemaj:zCxoGN86JHkofaia1X7PGdWzBvwse9@b83z4ijpseoxobhsnucg-postgresql.services.clever-cloud.com:50013/b83z4ijpseoxobhsnucg"
engine = create_engine(DATABASE_URL)

def create_table():
    SQLModel.metadata.create_all(engine)

def insert_cosmetics_from_csv(csv_path: str):
    with open(csv_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        entries = []

        for row in reader:
            row["id"] = int(row["id"]) if row.get("id") else None
            entry = CosmeticColab(**row)
            entries.append(entry)

        with Session(engine) as session:
            session.add_all(entries)
            session.commit()

if __name__ == "__main__":
    create_table()
    insert_cosmetics_from_csv("cosmetic_colab.csv")
    print("Datos de colaboraciones cosméticas insertados.")
