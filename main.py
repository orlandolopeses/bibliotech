# main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from starlette.responses import JSONResponse

app = FastAPI()

# Dependência para extrair o token do Authorization header
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

def get_drive_service(token: str = Depends(oauth2_scheme)):
    """
    Cria um objeto googleapiclient com as credenciais do usuário.
    Se o token for inválido ou ausente, lança HTTPException(401).
    """
    try:
        creds = Credentials(token=token)
        service = build("drive", "v3", credentials=creds)
        return service
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido ou ausente")

@app.get("/list_files")
async def list_files(folder_id: str = None, drive_service = Depends(get_drive_service)):
    """
    Lista arquivos de uma pasta no Google Drive.
    - Se folder_id for None, lista arquivos na pasta 'root'.
    - Retorna JSON: { "files": [ { "id": "...", "name": "...", "mimeType": "..." }, … ] }
    """
    # Monta a query para a API do Drive
    if folder_id:
        query = f"'{folder_id}' in parents and trashed = false"
    else:
        # 'root' indica a raiz do Drive
        query = "'root' in parents and trashed = false"
    try:
        resposta = drive_service.files().list(
            q=query,
            fields="files(id,name,mimeType)"
        ).execute()
        arquivos = resposta.get("files", [])
        return JSONResponse(content={"files": arquivos})
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao acessar Google Drive")
