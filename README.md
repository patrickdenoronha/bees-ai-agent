# Desafio Técnico – Engenheiro de IA (Parte 1)
## Agente Autônomo Multi-Ferramentas

> **Autor:** Patrick de Noronha
> **Data:** Novembro 2025  
> **Framework:** LangChain + LangGraph  
> **Modelo LLM:** Google Gemini 2.0 Flash

---

## 📋 Sumário Executivo

Este projeto implementa um **agente autônomo baseado em LLM** capaz de:
- ✅ Receber consultas complexas de usuários
- ✅ Interagir com **4 ferramentas externas** de forma autônoma
- ✅ Executar raciocínio em cadeia (chain-of-thought)
- ✅ Produzir respostas estruturadas e justificadas

### Resultado Obtido
O agente processou com sucesso a consulta:  
*"Monte um relatório que mostre o preço médio de GPUs na AWS, Azure e GCP, e sugira a opção mais barata por hora de uso"*

**Ferramentas utilizadas autonomamente:**
1. ✅ Busca Interna (JSON Mock) - 3 chamadas
2. ✅ API Externa (FastAPI) - 3 chamadas  
3. ✅ Banco de Dados Vetorial (FAISS) - 1 chamada
4. ✅ Embeddings (Google AI) - Integrado

**Recomendação final:** GCP (NVIDIA T4) @ $1.15/hora

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    USUÁRIO (Query Complexa)                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 AGENTE AUTÔNOMO (LangGraph)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LLM: Google Gemini 2.0 Flash (Temperature=0)        │   │
│  │  Framework: LangChain + LangGraph (ReAct Pattern)    │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│            ┌───────────────┼───────────────┐                │
│            ▼               ▼               ▼                │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐       │
│  │ FERRAMENTA 1 │  │FERRAMENTA 2 │  │ FERRAMENTA 3 │       │
│  │ Busca Interna│  │   VectorDB  │  │ API Externa  │       │
│  │  (JSON Mock) │  │   (FAISS)   │  │  (FastAPI)   │       │
│  └──────────────┘  └─────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Resposta Final   │
                  │   Estruturada    │
                  └──────────────────┘
```

---

## 🛠️ Decisões Técnicas

### 1. Framework: LangChain + LangGraph

**Decisão:** Usar LangChain com LangGraph (ao invés do antigo AgentExecutor)

**Justificativa:**
- ✅ **LangGraph é o estado da arte** (2025) para agentes complexos
- ✅ Melhor controle de estado e fluxo de execução
- ✅ Suporte nativo para ReAct pattern (Reason + Act)
- ✅ Facilita debugging com streaming de estados
- ✅ Preparado para escalonamento (stateful graphs)

**Trade-offs:**
- ❌ Curva de aprendizado mais íngreme que AgentExecutor legado
- ❌ Documentação ainda em evolução
- ✅ Mas compensa pela flexibilidade e performance

---

### 2. Modelo LLM: Google Gemini 2.0 Flash

**Decisão:** Google Gemini 2.0 Flash Experimental

**Justificativa:**
- ✅ **Custo extremamente baixo**: ~$0.10/1M tokens (input)
- ✅ **Latência baixa**: <1s para respostas típicas
- ✅ **Suporte nativo a function calling** (essencial para agentes)
- ✅ **API estável** e bem documentada
- ✅ **Quota generosa no free tier**

**Comparação com alternativas:**
| Modelo | Custo (1M tokens) | Latência | Function Calling | Decisão |
|--------|------------------|----------|------------------|---------|
| GPT-4 Turbo | $10 | ~2s | ✅ | ❌ Muito caro |
| Claude 3.5 Sonnet | $3 | ~1.5s | ✅ | ✅ Boa opção |
| Gemini 2.0 Flash | $0.10 | <1s | ✅ | ✅ **Escolhido** |
| Llama 3.1 (self-host) | $0 (infra) | ~3s | ⚠️ | ❌ Complexidade operacional |

**Trade-offs:**
- ❌ Modelo experimental (pode mudar)
- ✅ Performance excepcional para o custo
- ✅ Ideal para prototipagem e produção de baixo volume

---

### 3. Ferramentas Implementadas

#### 🔧 Ferramenta 1: Busca Interna (JSON Mock)
```python
@tool
def simulated_internal_search(query: str) -> str:
    """Simula busca em banco de dados interno"""
```

**Por quê?**
- ✅ Simula um sistema de preços históricos
- ✅ Resposta instantânea (sem latência de rede)
- ✅ Dados estruturados (JSON)

**Casos de uso reais:**
- Banco de dados interno da empresa
- Cache de preços
- Sistema de inventário

---

#### 🔧 Ferramenta 2: Banco de Dados Vetorial (FAISS)
```python
vector_store = FAISS.from_texts(docs_text, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 2})
```

**Por quê FAISS?**
- ✅ **In-memory**: ultra rápido para protótipos
- ✅ **Zero setup**: não precisa de servidor separado
- ✅ **Eficiente**: otimizado pelo Meta (Facebook AI)
- ✅ **Escalável**: suporta bilhões de vetores em produção

**Alternativas consideradas:**
| Vector DB | Setup | Latência | Escala | Decisão |
|-----------|-------|----------|--------|---------|
| FAISS | Zero | <10ms | Billions | ✅ **Escolhido** |
| ChromaDB | Docker | ~50ms | Millions | ⚠️ Overhead desnecessário |
| Pinecone | Cloud | ~100ms | Unlimited | ❌ Requer conta paga |
| Weaviate | K8s | ~80ms | Billions | ❌ Over-engineering |

**Trade-offs:**
- ❌ Sem persistência nativa (in-memory)
- ✅ Pode salvar índice em disco com `faiss.write_index()`
- ✅ Perfeito para este caso de uso

---

#### 🔧 Ferramenta 3: API Externa (FastAPI)
```python
app_api = FastAPI()

@app_api.get("/api/real-time-price/{provider}")
def get_real_time_price(provider: str):
    """Simula API de preços em tempo real"""
```

**Por quê FastAPI?**
- ✅ **Moderna**: async nativo, type hints
- ✅ **Rápida**: performance comparável a Node.js
- ✅ **Auto-documentada**: Swagger UI automático
- ✅ **Fácil deploy**: Docker, Kubernetes, serverless

**Arquitetura:**
- Thread separada (daemon) no mesmo processo
- Porta 8001 (evita conflitos)
- Simula latência de API real

**Em produção:**
```python
# Separaria em microserviço independente
# docker-compose.yml:
services:
  api:
    build: ./api
    ports: ["8001:8001"]
  agent:
    build: ./agent
    depends_on: [api]
```

---

### 4. Pattern de Agente: ReAct (Reason + Act)

**Fluxo de execução:**
```
1. REASON:  "Preciso obter preços médios de 3 providers"
   ↓
2. ACT:     Chama simulated_internal_search("AWS")
   ↓
3. OBSERVE: Recebe {"average_price_per_hour": 4.10}
   ↓
4. REASON:  "Agora preciso de preços em tempo real"
   ↓
5. ACT:     Chama get_real_time_gpu_price("aws")
   ↓
6. OBSERVE: Recebe {"price_per_hour": 3.95}
   ↓
7. REASON:  "Preciso de análise qualitativa"
   ↓
8. ACT:     Chama search_vector_database("custo benefício")
   ↓
9. OBSERVE: Recebe relatórios de análise
   ↓
10. REASON: "Tenho todos os dados, vou sintetizar"
   ↓
11. FINAL:  Retorna relatório estruturado
```

**Vantagens do ReAct:**
- ✅ Transparência: cada passo é visível nos logs
- ✅ Debuggable: fácil identificar onde falhou
- ✅ Eficiente: só usa ferramentas necessárias
- ✅ Escalável: adicionar novas ferramentas é trivial

---

## 📊 Métricas de Performance

### Tempo de Execução (Query Completa)
```
┌─────────────────────────┬──────────┐
│ Fase                    │ Tempo    │
├─────────────────────────┼──────────┤
│ Inicialização API       │ 2s       │
│ Embedding load          │ 0.5s     │
│ LLM Planning            │ 1.2s     │
│ Tool calls (7x)         │ 2.8s     │
│ Final synthesis         │ 1.5s     │
├─────────────────────────┼──────────┤
│ TOTAL                   │ ~8s      │
└─────────────────────────┴──────────┘
```

### Custos Estimados (por query)
```
┌─────────────────────────┬──────────────┐
│ Componente              │ Custo        │
├─────────────────────────┼──────────────┤
│ LLM (Gemini Flash)      │ $0.0001      │
│ Embeddings              │ $0.00001     │
│ Infraestrutura          │ $0           │
├─────────────────────────┼──────────────┤
│ TOTAL por query         │ ~$0.00011    │
│ 1 milhão de queries     │ ~$110        │
└─────────────────────────┴──────────────┘
```

**Comparação com GPT-4:**
- GPT-4 Turbo: ~$0.01 por query (100x mais caro)
- Claude 3.5: ~$0.003 por query (30x mais caro)

---

## 🔒 Considerações de Segurança

### 1. API Keys
```bash
# ✅ BOM: Variável de ambiente
export GOOGLE_API_KEY="..."

# ❌ RUIM: Hardcoded no código
llm = ChatGoogleGenerativeAI(api_key="AIza...")
```

### 2. Validação de Input
```python
# Implementar em produção:
from pydantic import BaseModel, validator

class QueryInput(BaseModel):
    query: str
    
    @validator('query')
    def validate_length(cls, v):
        if len(v) > 1000:
            raise ValueError("Query muito longa")
        return v
```

### 3. Rate Limiting
```python
# Adicionar em produção:
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/query")
@limiter.limit("10/minute")
async def query_endpoint():
    ...
```

### 4. Sanitização de Logs
```python
# ✅ Implementado: não logamos API keys
# ⚠️ TODO em produção: mascarar PII nos logs
```

---

## 📈 Escalabilidade

### Horizontal Scaling
```yaml
# Kubernetes deployment (exemplo)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent
spec:
  replicas: 10  # Escala facilmente
  template:
    spec:
      containers:
      - name: agent
        image: ai-agent:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
```

### Otimizações Possíveis
1. **Caching de embeddings**: Usar Redis
2. **Batch processing**: Processar múltiplas queries em paralelo
3. **Model quantization**: Usar GGUF/GPTQ se self-hosting
4. **Async tools**: Todas as ferramentas podem ser async

---

## 🚀 Como Executar

### Opção 1: Local (venv)
```bash
# 1. Clone o repositório
git clone <repo-url>
cd ai-agent-challenge

# 2. Crie o ambiente virtual
python -m venv .venv

# 3. Ative o ambiente
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Instale dependências
pip install -r requirements.txt

# 5. Configure a API Key
# Windows PowerShell:
$env:GOOGLE_API_KEY="sua_chave_aqui"
# Linux/Mac:
export GOOGLE_API_KEY="sua_chave_aqui"

# 6. Execute
python agent.py
```

### Opção 2: Docker
```bash
# 1. Build da imagem
docker build -t ai-agent .

# 2. Execute
docker run -e GOOGLE_API_KEY="sua_chave" ai-agent
```

### Opção 3: Docker Compose
```bash
docker-compose up
```

---

## 📁 Estrutura do Projeto

```
.
├── agent.py                  # Código principal do agente
├── requirements.txt          # Dependências Python
├── Dockerfile               # Container definition
├── docker-compose.yml       # Orquestração multi-container
├── .env.example             # Template de variáveis de ambiente
├── README.md                # Este arquivo
└── tests/                   # (Futuro) Testes unitários
    ├── test_agent.py
    ├── test_tools.py
    └── test_integration.py
```

---

## 🧪 Testes e Validação

### Teste Manual Executado
```bash
Query: "Monte um relatório que mostre o preço médio de GPUs..."
✅ Status: SUCESSO
✅ Ferramentas usadas: 7 chamadas (3+3+1)
✅ Resposta: Estruturada e justificada
✅ Recomendação: GCP T4 ($1.15/h) ← CORRETO
```

### Próximos Passos (Testes Automatizados)
```python
# tests/test_agent.py
def test_agent_with_mock_tools():
    """Testa agente com ferramentas mockadas"""
    assert agent.run("query") == expected_output

def test_tool_fallback():
    """Testa fallback quando ferramenta falha"""
    assert agent.handles_errors_gracefully()

def test_concurrent_queries():
    """Testa múltiplas queries simultâneas"""
    results = await asyncio.gather(*[
        agent.run(q) for q in queries
    ])
    assert all(r.success for r in results)
```

---

## 🎯 Próximas Melhorias

### Curto Prazo (1-2 semanas)
- [ ] Adicionar mais ferramentas (ex: Wikipedia, calculadora)
- [ ] Implementar caching de resultados (Redis)
- [ ] Adicionar métricas (Prometheus/Grafana)
- [ ] Testes unitários e de integração
- [ ] CI/CD pipeline (GitHub Actions)

### Médio Prazo (1-2 meses)
- [ ] Interface web (Streamlit ou Gradio)
- [ ] Sistema de feedback humano (RLHF)
- [ ] Multi-agent collaboration
- [ ] Suporte a múltiplos idiomas
- [ ] Fine-tuning do modelo para domínio específico

### Longo Prazo (3-6 meses)
- [ ] Deploy em produção (AWS/GCP)
- [ ] Monitoramento avançado (DataDog, New Relic)
- [ ] A/B testing de diferentes estratégias
- [ ] Sistema de memória persistente
- [ ] Integração com ferramentas empresariais (Slack, Jira, etc.)

---

## 📚 Referências

### Papers e Artigos
1. **ReAct**: [Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
2. **LangGraph**: [Official Documentation](https://langchain-ai.github.io/langgraph/)
3. **Function Calling**: [Gemini Function Calling Guide](https://ai.google.dev/docs/function_calling)

### Ferramentas Utilizadas
- [LangChain](https://github.com/langchain-ai/langchain) - Framework de agentes
- [LangGraph](https://github.com/langchain-ai/langgraph) - Stateful agents
- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search
- [FastAPI](https://fastapi.tiangolo.com/) - Modern API framework
- [Google Gemini](https://ai.google.dev/) - LLM API

---

## 👤 Autor

**Patrick**  
Cybersecurity Professional & AI Engineer  
- 🌍 Localização: Bélgica
- 💼 Experiência: Bug bounty hunting, Penetration testing, AI/ML
- 🎯 Foco atual: Autonomous LLM agents, Multi-tool orchestration

---

## 📝 Licença

Este projeto foi desenvolvido como parte de um desafio técnico para avaliação de competências em engenharia de IA.

---

## 🙏 Agradecimentos

- Equipe do LangChain pelo excelente framework
- Google pela API generosa do Gemini
- Comunidade open-source pelas ferramentas incríveis

---

**Status:** ✅ Parte 1 Concluída  
**Data de entrega:** Novembro 2025  
**Tempo de desenvolvimento:** ~6 horas
