import os
import json
import requests
import threading
import time
from typing import List, Dict, Any

# --- Importações das Ferramentas ---
import uvicorn
from fastapi import FastAPI

# --- Importações do LangChain ---
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langgraph.prebuilt import create_react_agent

# --- INÍCIO: FERRAMENTA 1: API EXTERNA FICTÍCIA (FastAPI) ---
app_api = FastAPI()

@app_api.get("/api/real-time-price/{provider}")
def get_real_time_price(provider: str):
    """Retorna o preço em tempo real de uma GPU específica por provedor."""
    prices = {
        "aws": {"gpu_model": "NVIDIA A100", "price_per_hour": 3.95},
        "azure": {"gpu_model": "NVIDIA H100", "price_per_hour": 4.10},
        "gcp": {"gpu_model": "NVIDIA T4", "price_per_hour": 1.15},
    }
    price_data = prices.get(provider.lower(), {"error": "Provider not found"})
    return price_data

def start_fake_api():
    """Função para iniciar o servidor FastAPI em uma thread separada."""
    print("[LOG] Iniciando API Fictícia em http://127.0.0.1:8001")
    uvicorn.run(app_api, host="127.0.0.1", port=8001, log_level="warning")

# --- FIM: FERRAMENTA 1 ---

# --- FERRAMENTA 2: Banco de Dados Vetorial (FAISS) ---
try:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    docs_text = [
        "Relatório de Análise GCP: O Google Cloud (GCP) tem se destacado com suas TPUs e GPUs T4, oferecendo uma excelente relação custo-benefício para inferência.",
        "Análise AWS 2025: A AWS continua a dominar com as instâncias P4 e P5 (NVIDIA A100/H100), mas seus preços são geralmente mais altos, exceto por instâncias spot.",
        "Azure AI: A Azure investiu pesadamente em instâncias ND-series (H100), focando em grandes modelos de linguagem. A integração com o OpenAI Service é um diferencial.",
        "Custo-Benefício: Um estudo recente indicou que, para workloads de média escala, o GCP (T4) apresenta o menor custo por hora, enquanto a AWS (A100) oferece a melhor performance bruta."
    ]
    
    vector_store = FAISS.from_texts(docs_text, embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})

    @tool
    def search_vector_database(query: str) -> str:
        """
        Consulta a base de dados vetorial (FAISS) para obter insights e análises 
        qualitativas sobre provedores de nuvem e GPUs (AWS, Azure, GCP).
        Use isso para entender o 'porquê' dos preços ou tendências.
        """
        print(f"\n[LOG Ferramenta] Consultando VectorDB: '{query}'")
        docs = retriever.invoke(query)
        return "\n---\n".join([doc.page_content for doc in docs])

except Exception as e:
    print(f"Erro ao inicializar o VectorDB (Verifique a API Key): {e}")
    @tool
    def search_vector_database(query: str) -> str:
        """MOCK: Consulta a base de dados vetorial (FAISS)"""
        print(f"\n[LOG Ferramenta] MOCK VectorDB: '{query}'")
        return "Relatório de Análise GCP: O Google Cloud (GCP) tem se destacado com suas TPUs e GPUs T4, oferecendo uma excelente relação custo-benefício para inferência."

# --- FERRAMENTA 3: Pesquisa Interna (JSON Mock) ---
@tool
def simulated_internal_search(query: str) -> str:
    """
    Simula uma busca em um banco de dados interno (ex: JSON) para obter 
    o preço MÉDIO histórico de GPUs. Retorna um JSON.
    """
    print(f"\n[LOG Ferramenta] Consultando Busca Interna: '{query}'")
    data = {
        "aws": {"average_price_per_hour": 4.10, "models_available": ["A100", "H100", "T4"]},
        "azure": {"average_price_per_hour": 4.25, "models_available": ["H100", "A100", "V100"]},
        "gcp": {"average_price_per_hour": 3.80, "models_available": ["T4", "A100", "TPU v5"]},
    }
    return json.dumps(data)

# --- FERRAMENTA 4: Chamada à API Fictícia ---
@tool
def get_real_time_gpu_price(provider: str) -> str:
    """
    Obtém o preço "em tempo real" (SPOT) de uma GPU específica de um 
    provedor (aws, azure, ou gcp) chamando a API externa.
    """
    print(f"\n[LOG Ferramenta] Chamando API Externa: provider={provider}")
    try:
        response = requests.get(f"http://127.0.0.1:8001/api/real-time-price/{provider}")
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Erro ao chamar a API: {e}"

# --- CONFIGURAÇÃO DO AGENTE ---

def main():
    # 1. Iniciar a API Fictícia
    api_thread = threading.Thread(target=start_fake_api, daemon=True)
    api_thread.start()
    
    print("[LOG] Aguardando API Fictícia iniciar...")
    time.sleep(2)
    print("[LOG] API Fictícia pronta.")

    # 2. Definir ferramentas
    tools = [
        search_vector_database,
        simulated_internal_search,
        get_real_time_gpu_price
    ]

    # 3. Definir o LLM com System Message
    from langchain_core.messages import SystemMessage
    
    # IMPORTANTE: Usar o nome correto do modelo para v1beta
    # Opções: "gemini-pro", "gemini-1.5-flash-latest", "gemini-2.0-flash-exp"
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)

    # 4. System Message
    system_message = SystemMessage(content="""Você é um assistente especialista em análise de custos de Cloud (AWS, Azure, GCP).
Sua tarefa é responder à consulta do usuário de forma estruturada.
Você deve usar as ferramentas disponíveis para coletar dados.
Analise os dados coletados (preços médios, preços em tempo real e relatórios qualitativos) para formular sua resposta.
Sempre justifique sua recomendação final com base nos dados.
Não invente informações; use apenas o que as ferramentas retornam.
Seja claro e conciso.""")

    # 5. Criar o Agente usando LangGraph
    agent_executor = create_react_agent(
        model=llm, 
        tools=tools
    )

    # 6. Executar o Agente
    print("\n" + "="*50)
    print("INICIANDO AGENTE AUTÔNOMO")
    print("="*50 + "\n")
    
    query = """Monte um relatório que mostre o preço médio de GPUs na AWS, Azure e GCP, 
e sugira a opção mais barata por hora de uso com base em dados em tempo real 
e análises de custo-benefício da base de conhecimento."""
    
    print(f"[LOG] Executando query: {query}\n")
    
    # Executar o agente COM system message
    messages = []
    for chunk in agent_executor.stream(
        {"messages": [system_message, ("user", query)]},
        stream_mode="values"
    ):
        messages = chunk["messages"]
        if messages:
            last_msg = messages[-1]
            if hasattr(last_msg, 'content') and hasattr(last_msg, 'type'):
                msg_preview = str(last_msg.content)[:200] if last_msg.content else ""
                print(f"[STEP] {last_msg.type}: {msg_preview}...")

    print("\n" + "="*50)
    print("EXECUÇÃO DO AGENTE CONCLUÍDA")
    print("="*50 + "\n")

    # 7. Exibir resposta final
    print("--- RESPOSTA FINAL ESTRUTURADA ---")
    final_response = messages[-1].content if messages else "Nenhuma resposta gerada"
    print(final_response)

if __name__ == "__main__":
    if "GOOGLE_API_KEY" not in os.environ:
        print("Erro: A variável de ambiente GOOGLE_API_KEY não está definida.")
        print("Por favor, configure-a antes de executar o script.")
        print("\nNo PowerShell, use:")
        print('$env:GOOGLE_API_KEY="sua_chave_aqui"')
    else:
        main()
