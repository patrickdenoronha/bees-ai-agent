# 🚀 Instruções de Execução

## Pré-requisitos

- Python 3.11 ou superior
- Chave API do Google Gemini ([obtenha aqui](https://aistudio.google.com/app/apikey))
- Docker (opcional, para execução containerizada)

---

## Opção 1: Execução Local (Recomendado para Desenvolvimento)

### Windows (PowerShell)

```powershell
# 1. Clone ou extraia o projeto
cd C:\Projetos\ai-agent-challenge

# 2. Crie o ambiente virtual
python -m venv .venv

# 3. Ative o ambiente virtual
.venv\Scripts\activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Configure a chave API
$env:GOOGLE_API_KEY="sua_chave_api_aqui"

# 6. Execute o agente
python agent.py
```

### Linux / macOS

```bash
# 1. Clone ou extraia o projeto
cd ~/ai-agent-challenge

# 2. Crie o ambiente virtual
python3 -m venv .venv

# 3. Ative o ambiente virtual
source .venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Configure a chave API
export GOOGLE_API_KEY="sua_chave_api_aqui"

# 6. Execute o agente
python agent.py
```

---

## Opção 2: Execução com Docker

### Usando Docker diretamente

```bash
# 1. Build da imagem
docker build -t ai-agent-challenge .

# 2. Execute o container
docker run -e GOOGLE_API_KEY="sua_chave_api_aqui" ai-agent-challenge
```

### Usando Docker Compose (Recomendado)

```bash
# 1. Crie o arquivo .env (copie do .env.example)
cp .env.example .env

# 2. Edite o .env e adicione sua chave API
notepad .env  # Windows
nano .env     # Linux/Mac

# 3. Inicie o serviço
docker-compose up --build

# 4. Para parar
docker-compose down
```

---

## Opção 3: Execução com Arquivo .env (Mais Seguro)

```bash
# 1. Instale python-dotenv (já incluído no requirements.txt)
pip install python-dotenv

# 2. Crie o arquivo .env
cp .env.example .env

# 3. Edite o .env com sua chave API
GOOGLE_API_KEY=sua_chave_api_aqui

# 4. Modifique agent.py para carregar do .env (adicione no início):
from dotenv import load_dotenv
load_dotenv()

# 5. Execute normalmente
python agent.py
```

---

## 📊 Saída Esperada

Ao executar com sucesso, você verá:

```
[LOG] Iniciando API Fictícia em http://127.0.0.1:8001
[LOG] Aguardando API Fictícia iniciar...
[LOG] API Fictícia pronta.

==================================================
INICIANDO AGENTE AUTÔNOMO
==================================================

[LOG] Executando query: Monte um relatório que mostre o preço médio de GPUs...

[STEP] human: Monte um relatório...
[STEP] ai: ...
[LOG Ferramenta] Consultando Busca Interna: 'preço médio de GPUs AWS'
[LOG Ferramenta] Consultando Busca Interna: 'preço médio de GPUs GCP'
[LOG Ferramenta] Consultando Busca Interna: 'preço médio de GPUs Azure'
[LOG Ferramenta] Chamando API Externa: provider=aws
[LOG Ferramenta] Chamando API Externa: provider=azure
[LOG Ferramenta] Chamando API Externa: provider=gcp
[LOG Ferramenta] Consultando VectorDB: 'análise de custo benefício...'

==================================================
EXECUÇÃO DO AGENTE CONCLUÍDA
==================================================

--- RESPOSTA FINAL ESTRUTURADA ---
## Relatório de Preços de GPUs (AWS, Azure, GCP)
...
**Recomendação:** GCP (NVIDIA T4) @ $1.15/hora
```

---

## ⚠️ Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'langchain'"

**Solução:**
```bash
pip install -r requirements.txt
```

### Erro: "404 models/gemini-1.5-pro-latest is not found"

**Solução:** Atualize o modelo no código:
```python
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
```

### Erro: "error while attempting to bind on address ('127.0.0.1', 8001)"

**Solução:** Porta 8001 já está em uso. Mate o processo ou mude a porta:

**Windows:**
```powershell
netstat -ano | findstr :8001
taskkill /PID <numero_do_processo> /F
```

**Linux/Mac:**
```bash
lsof -ti:8001 | xargs kill -9
```

### Erro: "GOOGLE_API_KEY não está definida"

**Solução:**
```bash
# Verifique se a variável está setada
echo $env:GOOGLE_API_KEY  # Windows
echo $GOOGLE_API_KEY       # Linux/Mac

# Se vazio, configure novamente
$env:GOOGLE_API_KEY="sua_chave"  # Windows
export GOOGLE_API_KEY="sua_chave" # Linux/Mac
```

### Erro de certificado SSL no Windows

**Solução:**
```powershell
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## 🧪 Testando Manualmente

Após a execução bem-sucedida, você pode testar a API fictícia:

```bash
# Em outro terminal
curl http://127.0.0.1:8001/api/real-time-price/aws
curl http://127.0.0.1:8001/api/real-time-price/azure
curl http://127.0.0.1:8001/api/real-time-price/gcp
```

Resposta esperada:
```json
{"gpu_model":"NVIDIA A100","price_per_hour":3.95}
```

---

## 📝 Modificando a Query

Para testar com outras consultas, edite o arquivo `agent.py` na linha:

```python
query = """Monte um relatório que mostre o preço médio de GPUs..."""
```

Exemplos de outras queries:
```python
# Exemplo 1: Comparação simples
query = "Qual provedor tem a GPU mais barata?"

# Exemplo 2: Análise detalhada
query = "Faça uma análise detalhada comparando custo-benefício das GPUs"

# Exemplo 3: Recomendação específica
query = "Qual GPU devo escolher para treinar modelos de machine learning?"
```

---

## 📚 Próximos Passos

1. ✅ Execute o código e valide o funcionamento
2. ✅ Leia o README.md para entender a arquitetura
3. ✅ Explore os logs para ver o raciocínio do agente
4. ✅ Modifique a query e teste diferentes cenários
5. ✅ (Opcional) Adicione novas ferramentas ao agente

---

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs de erro completos
2. Confirme que a chave API está válida
3. Teste a conexão com a API do Gemini separadamente
4. Verifique se todas as dependências estão instaladas

**Contato:** Patrick (patrick@denoronha.com)

---

## ✅ Checklist de Validação

Antes de enviar, verifique:

- [ ] O código executa sem erros
- [ ] Todas as 3+ ferramentas são chamadas
- [ ] A resposta final está estruturada
- [ ] Os logs mostram o chain-of-thought
- [ ] O Docker build funciona (opcional)
- [ ] O README está completo
- [ ] As decisões técnicas estão documentadas

---

**Tempo estimado de setup:** 5-10 minutos  
**Tempo de execução:** ~8 segundos por query  
**Status:** ✅ Pronto para produção
