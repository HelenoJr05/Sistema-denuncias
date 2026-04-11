# 🛡️ Sistema de Denúncias Anônimas — Combate à Homofobia

Sistema web para registro anônimo de ocorrências de homofobia, desenvolvido com **FastAPI** e interface HTML.

## Funcionalidades

- ✅ Formulário de denúncia com 4 campos principais
- 🔒 100% anônimo (sem coleta de dados pessoais)
- 📋 Geração de número de protocolo único
- 💾 Armazenamento local em JSON
- 📊 Painel administrativo para visualizar denúncias
- 🌈 Interface moderna e acessível

## Como Executar

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Inicie o servidor

```bash
uvicorn main:app --reload
```

### 3. Acesse no navegador

- **Formulário de denúncia:** http://localhost:8000
- **Painel administrativo:** http://localhost:8000/admin/denuncias

## Campos do Formulário

| Campo | Tipo | Obrigatório |
|---|---|---|
| Data do Ocorrido | Data | ✅ Sim |
| Tipo de Ocorrência | Seleção | ❌ Opcional |
| Local do Ocorrido | Texto | ✅ Sim |
| Descrição do Ocorrido | Texto longo | ✅ Sim |
| Descrição do Indivíduo | Texto longo | ✅ Sim |

## Estrutura dos Arquivos

```
app/
├── main.py              # Aplicação FastAPI
├── requirements.txt     # Dependências
├── denuncias.json       # Banco de dados local (criado automaticamente)
└── templates/
    ├── index.html       # Página do formulário
    └── admin.html       # Painel administrativo
```

## Contatos de Emergência

- **190** — Polícia Militar
- **Disque 100** — Direitos Humanos (MMFDH)
