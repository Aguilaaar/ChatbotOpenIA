from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import *
import json
from tools_ecomart import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4-1106-preview"
contexto = carrega("dados/ecomart.txt")

def criar_lista_ids():
    lista_ids_arquivos = []

    file_dados = cliente.files.create(
        file = open ("dados/dados_ecomart.txt", "rb"),
        purpose = "assistants"
    )
    lista_ids_arquivos.append(file_dados.id)

    file_politicas = cliente.files.create(
        file = open ("dados/políticas_ecomart.txt", "rb"),
        purpose = "assistants"
    )
    lista_ids_arquivos.append(file_politicas.id)

    file_produtos = cliente.files.create(
        file = open ("dados/produtos_ecomart.txt", "rb"),
        purpose = "assistants"
    )
    lista_ids_arquivos.append(file_politicas.id)

    return lista_ids_arquivos

def pegar_json():
    filename = "assistentes.json"

    if not os.path.exists(filename):
        vector_store = cria_vector_store()
        thread_id = criar_thread()
        assistent_id = criar_assistente(vector_store)
        data = {
            "assistent_id":assistent_id.id,
            'vector_store_id': vector_store.id,
            "thread_id": thread_id.id
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Arquivo 'assistentes.json' criado com sucesso.")
    
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("Arquivo 'assistentes.json' não encontrado.")

def criar_thread():
    vector_store = cria_vector_store()
    return cliente.beta.threads.create(
        tool_resources={
            'file_search': {
                'vector_store_ids': [vector_store.id]
            }
        }
    )

def cria_vector_store():
    vector_store = cliente.beta.vector_stores.create(name='Ecomart Vector Store')

    file_paths = [
        'dados/dados_ecomart.txt',
        'dados/políticas_ecomart.txt',
        'dados/produtos_ecomart.txt'
    ]
    file_streams = [open(path, 'rb') for path in file_paths]

    cliente.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=file_streams
    )

    return vector_store

def criar_assistente(vector_store):
    assistant = cliente.beta.assistants.create(
        name='Maria',
        instructions=f'''
            Você é um chatbot de atendimento a clientes de um e-commerce. 
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            Além disso, acesse os arquivos associados a você e a thread para responder as perguntas.
        ''',
        model = modelo,
        tools = minhas_tools,
        tool_resources={
            'file_search': {
                'vector_store_ids': [vector_store.id]
            }
        }
    )
    return assistant
