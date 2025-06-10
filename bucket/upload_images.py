import os
import uuid
from fastapi import UploadFile
from dotenv import load_dotenv
import aiofiles
from supabase import create_client
import unicodedata
import re

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'app', '.env')
load_dotenv(dotenv_path)

# Configuración de Supabase
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def upload_file(file: UploadFile, filename: str) -> str:
    """
    Sube un archivo a Supabase Storage y devuelve su URL público.
    """
    content = await file.read()
    file_path = f"images/{filename}"  # Carpeta lógica en el bucket

    # Subir a Supabase
    supabase.storage.from_(SUPABASE_BUCKET).upload(
        file_path,
        content,
        {"content-type": file.content_type}
    )

    # Obtener URL pública
    public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
    return public_url


def clean_filename(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^\w\-_.]", "_", name)
    return name

async def save_file(file: UploadFile, to_supabase: bool = True):
    if not file.content_type.startswith("image/"):
        return {"error": "Solo se permiten imágenes"}
    filename = f"{uuid.uuid4().hex}_{clean_filename(file.filename)}"
    if to_supabase:
        return await upload_file(file, filename)
    else:
        return await save_to_local(file, filename)


async def save_to_local(file: UploadFile, filename: str):
    """
    Guarda el archivo en una carpeta local llamada 'uploads'.
    """
    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", filename)

    async with aiofiles.open(path, "wb") as f:
        content = await file.read()
        await f.write(content)

    return {"filename": filename, "local_path": path}
