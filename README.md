# 🛡️ Sistema de Denúncias Anônimas — Combate à Homofobia

Sistema web para registro anônimo de ocorrências de homofobia.

---

## ☁️ Arquitetura atual

```
Usuário
  │
  ▼
Frontend (templates Jinja2 servidos pela própria API)
  │
  ▼
FastAPI (main.py) — rotas /, /denunciar, /admin/denuncias, /api/cep/{cep}
  │
  ▼
Persistência local em JSON (denuncias.json)
  │
  ▼
Integração externa: ViaCEP (enriquecimento de endereço)
```

> **Nota:** versões anteriores do README descreviam uma arquitetura serverless
> na AWS (Lambda / API Gateway / DynamoDB / S3). Essa é uma evolução planejada
> para as próximas fases do projeto (A2/A3, com Docker e IaC). A implementação
> atual roda localmente com FastAPI e persistência em arquivo.

---

## ✅ Funcionalidades

- 📋 Formulário de denúncia com campos obrigatórios e opcionais
- 🔒 100% anônimo — sem coleta de dados pessoais
- 🔑 Geração automática de protocolo único
- 🌍 Enriquecimento automático de endereço via CEP (API pública ViaCEP)
- 📊 Painel administrativo (`/admin/denuncias`) para visualizar denúncias

---

## 📁 Estrutura do Repositório

```
├── .github/workflows/
│   └── ci.yml              # Pipeline de CI (lint + testes)
├── templates/               # Templates Jinja2 (index.html, admin.html)
├── main.py                  # Aplicação FastAPI
├── test_integracao.py       # Testes de integração e mockados
├── requirements.txt
└── README.md
```

---

## 🔌 Endpoints da API

### `GET /`
Retorna o formulário de denúncia (HTML).

### `GET /api/cep/{cep}`
Consulta o ViaCEP e retorna os dados de endereço para um CEP. Usado pelo
frontend para autocompletar o campo de local.

**Resposta (sucesso):**
```json
{
  "cep": "70040-010",
  "logradouro": "Esplanada dos Ministérios",
  "bairro": "Zona Cívico-Administrativa",
  "localidade": "Brasília",
  "uf": "DF"
}
```

### `POST /denunciar`
Registra uma nova denúncia.

**Campos (form-data):**

| Campo | Tipo | Obrigatório |
|---|---|---|
| data_ocorrido | Data | ✅ Sim |
| horario_ocorrido | Hora | ❌ Opcional |
| local_ocorrido | Texto | ✅ Sim |
| descricao_ocorrido | Texto longo | ✅ Sim |
| descricao_individuo | Texto longo | ✅ Sim |
| tipo_ocorrido | Seleção | ❌ Opcional |
| cep_ocorrido | Texto | ❌ Opcional |

**Resposta:**
```json
{
  "sucesso": true,
  "protocolo": "DEN-20260613-A1B2C3",
  "endereco_confirmado": "Esplanada dos Ministérios",
  "mensagem": "Sua denúncia foi registrada com sucesso e será analisada em sigilo absoluto."
}
```

### `GET /admin/denuncias`
Lista todas as denúncias registradas (HTML).

---

## 🚀 Rodando localmente

### Pré-requisitos
- Python 3.11+

### Passos

```bash
git clone https://github.com/HelenoJr05/Sistema-denuncias
cd Sistema-denuncias
pip install -r requirements.txt
uvicorn main:app --reload
```

Acesse `http://localhost:8000` para o formulário e
`http://localhost:8000/admin/denuncias` para o painel administrativo.

---

## 🧪 Testes

```bash
pip install -r requirements.txt

# Testes mockados (não precisam de internet, rodam no CI)
pytest

# Inclui também os testes de integração real contra o ViaCEP
pytest -m integration
```

---

## 🔄 CI/CD

Pipeline configurado em [`.github/workflows/ci.yml`](.github/workflows/ci.yml),
executado automaticamente a cada `push` ou `pull request` para a branch `main`:

1. Checkout do código
2. Setup do Python 3.11
3. Instalação de dependências
4. Lint com `flake8`
5. Testes com `pytest`

A branch `main` é protegida: merges exigem Pull Request revisado e o pipeline
de CI passando.

---

## 📞 Contatos de Emergência

- **190** — Polícia Militar
- **Disque 100** — Direitos Humanos (MMFDH)

---

## 🛠️ Tecnologias

Python 3.11 · FastAPI · Jinja2 · httpx · pytest · GitHub Actions
