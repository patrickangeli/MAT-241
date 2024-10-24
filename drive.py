import os
import pickle
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Escopos que dão acesso ao Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Função para fazer login e autenticação
def authenticate():
    creds = None
    # O arquivo token.pickle armazena as credenciais de acesso do usuário
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Se não houver credenciais válidas, o usuário será solicitado a fazer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Salva as credenciais para futuras execuções
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Função para enviar arquivos para o Google Drive
def upload_files(service, folder_id, folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            file_metadata = {'name': file_name, 'parents': [folder_id]}
            media = MediaFileUpload(file_path, resumable=True)
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"Arquivo {file_name} enviado com sucesso.")

# Função para verificar se a pasta já existe no Google Drive
def get_drive_folder_id(service, folder_name):
    response = service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'", spaces='drive').execute()
    files = response.get('files', [])
    if not files:
        # Criar a pasta se ela não existir
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    else:
        return files[0].get('id')

def main():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # Especificar o nome da pasta no Google Drive e o caminho da pasta local
    folder_name = 'MinhaPastaSincronizada'
    local_folder_path = '/caminho/para/sua/pasta'

    # Verifica se a pasta já existe no Drive
    folder_id = get_drive_folder_id(service, folder_name)

    # Sincroniza a pasta local com o Google Drive
    upload_files(service, folder_id, local_folder_path)

if __name__ == '__main__':
    main()
