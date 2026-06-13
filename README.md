# 🛡️ Sistema de Denúncias Anônimas — Combate à Homofobia

Sistema web para registro anônimo de ocorrências de homofobia, com arquitetura serverless na AWS.

---

## ☁️ Arquitetura

```
Usuário
  │
  ▼
S3 Static Website        ← index.html + admin.html
  │
  ▼
API Gateway (REST)       ← rotas /denunciar e /admin/denuncias
  │
  ▼
AWS Lambda (Python)      ← lambda_function.py
  │
  ▼
DynamoDB                 ← tabela "denuncias"
```

---

## ✅ Funcionalidades

- 📋 Formulário de denúncia com 5 campos principais
- 🔒 100% anônimo — sem coleta de dados pessoais
- 🔑 Geração automática de número de protocolo único
- ☁️ Armazenamento em nuvem no DynamoDB (AWS)
- 📊 Painel administrativo para visualizar e filtrar denúncias
- 🌈 Interface moderna e responsiva

---

## 📁 Estrutura do Repositório

```
├── lambda/
│   └── lambda_function.py   # Função Lambda — salva e lista denúncias no DynamoDB
├── frontend/
│   ├── index.html           # Formulário de denúncia (deploy no S3)
│   └── admin.html           # Painel administrativo (deploy no S3)
├── DEPLOY.md                # Guia passo a passo de deploy na AWS
└── README.md
```

---

## 🚀 Deploy Rápido

### Pré-requisitos
- Conta AWS ativa
- Permissões para criar Lambda, API Gateway, DynamoDB e S3

### 1. DynamoDB
- Crie uma tabela chamada `denuncias`
- Partition key: `id` (String)
- Capacity: On-demand

### 2. Lambda
- Runtime: **Python 3.12**
- Faça upload do arquivo `lambda/lambda_function.py` em um `.zip`
- Variável de ambiente: `DYNAMODB_TABLE=denuncias`
- Permissão na role: `dynamodb:PutItem` e `dynamodb:Scan` na tabela `denuncias`

### 3. API Gateway (REST API)
| Método | Recurso | Integração |
|--------|---------|------------|
| POST | `/denunciar` | Lambda Proxy |
| GET | `/admin/denuncias` | Lambda Proxy |
| OPTIONS | `/denunciar` | Mock (CORS) |
| OPTIONS | `/admin/denuncias` | Mock (CORS) |

- Habilite **Lambda Proxy Integration** nos métodos POST e GET
- Faça deploy no stage `prod`

### 4. S3 Static Website
- Crie um bucket e habilite **Static Website Hosting**
- Index document: `index.html`
- Bucket policy: acesso público de leitura
- Substitua `API_URL` nos HTMLs pela Invoke URL do API Gateway
- Faça upload de `index.html` e `admin.html`

> Guia completo com prints e configurações detalhadas em [`DEPLOY.md`](./DEPLOY.md)

---

## 📋 Campos do Formulário

| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| Data do Ocorrido | Data | ✅ Sim |
| Horário | Hora | ❌ Opcional |
| Tipo de Ocorrência | Seleção | ❌ Opcional |
| Local do Ocorrido | Texto | ✅ Sim |
| Descrição do Ocorrido | Texto longo | ✅ Sim |
| Descrição do Indivíduo | Texto longo | ✅ Sim |

---

## 🔌 Endpoints da API

### `POST /denunciar`
Registra uma nova denúncia no DynamoDB.

**Body (JSON):**
```json
{
  "data_ocorrido": "2026-06-13",
  "horario_ocorrido": "14:30",
  "local_ocorrido": "Centro, São Paulo/SP",
  "descricao_ocorrido": "Descrição do que aconteceu...",
  "descricao_individuo": "Descrição do agressor...",
  "tipo_ocorrido": "Agressão verbal"
}
```

**Resposta:**
```json
{
  "sucesso": true,
  "protocolo": "DEN-20260613-A1B2C3",
  "mensagem": "Sua denúncia foi registrada com sucesso..."
}
```

### `GET /admin/denuncias`
Retorna todas as denúncias registradas.

**Resposta:**
```json
{
  "denuncias": [ { "protocolo": "...", "status": "Recebida", ... } ],
  "total": 1
}
```

---

## 📞 Contatos de Emergência

- **190** — Polícia Militar
- **Disque 100** — Direitos Humanos (MMFDH)

---

## 🛠️ Tecnologias

![AWS Lambda](https://img.shields.io/badge/AWS_Lambda-FF9900?style=flat&logo=awslambda&logoColor=white)
![DynamoDB](https://img.shields.io/badge/DynamoDB-4053D6?style=flat&logo=amazondynamodb&logoColor=white)
![API Gateway](https://img.shields.io/badge/API_Gateway-FF4F8B?style=flat&logo=amazonapigateway&logoColor=white)
![S3](https://img.shields.io/badge/Amazon_S3-569A31?style=flat&logo=amazons3&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=flat&logo=python&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
