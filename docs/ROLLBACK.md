[ROLLBACK.md](https://github.com/user-attachments/files/34132305/ROLLBACK.md)
# Versionamento e Rollback

Este documento descreve como o projeto versiona suas imagens/releases e como
reverter para uma versão anterior em caso de falha (entrega A2).

## Versionamento semântico

Seguimos [SemVer](https://semver.org/lang/pt-BR/): `MAJOR.MINOR.PATCH`.

| Mudança | Exemplo | Incrementa |
|---|---|---|
| Correção de bug compatível | `1.0.0` → `1.0.1` | PATCH |
| Nova funcionalidade compatível | `1.0.1` → `1.1.0` | MINOR |
| Mudança incompatível | `1.1.0` → `2.0.0` | MAJOR |

Cada versão é uma **tag Git** no formato `vX.Y.Z` e gera:

- imagem `ghcr.io/helenojr05/sistema-denuncias:X.Y.Z` (e `latest`);
- uma Release no GitHub com notas geradas automaticamente.

## Como lançar uma versão

Sempre a partir da `main`, depois que o PR foi mesclado e o CI passou:

```bash
git checkout main && git pull
git tag -a v1.0.0 -m "release: primeira versão estável"
git push origin v1.0.0
```

O workflow `cd.yml` então executa: testes → build → push no GHCR → release →
deploy simulado em homologação com smoke test (`/health` + `POST /denunciar`).

## Quando fazer rollback

- O smoke test do deploy falhou, ou
- a versão recém-implantada apresenta erro em uso (ex.: `/denunciar` retornando 500).

## Procedimento de rollback

### Opção 1 — Workflow de rollback (GitHub Actions)

1. Actions → **Rollback** → *Run workflow*.
2. Informe a versão estável anterior (ex.: `1.0.0`).
3. O workflow baixa a imagem dessa versão, sobe o ambiente e valida com smoke test.

### Opção 2 — Docker Compose (local ou servidor)

```bash
APP_TAG=1.0.0 docker compose pull app
APP_TAG=1.0.0 docker compose up -d --no-build
curl http://localhost:8000/health    # deve mostrar "version": "1.0.0"
```

### Opção 3 — Corrigir para frente

Quando o problema é pequeno: `git revert <commit>` via Pull Request e lançar
um novo PATCH (ex.: `v1.1.1`).

> **Dados:** as denúncias ficam no volume `denuncias_data`, que **não** é
> alterado pelo rollback da imagem. Só o código volta de versão.

## Simulação documentada

Preencha com as evidências reais (prints do Actions e saída dos comandos).

| Passo | O que fazer | Evidência |
|---|---|---|
| 1 | Lançar `v1.0.0` (versão estável) e confirmar o deploy verde | print do run do CD |
| 2 | Introduzir um defeito que os testes automatizados não cobrem (ex.: quebrar algo visível no `templates/index.html`), mesclar via PR e lançar `v1.1.0` | link do PR e da tag |
| 3 | Observar o defeito em uso (abrir a aplicação) ou no log do deploy | print / log |
| 4 | Executar o rollback para `1.0.0` (Opção 1 ou 2) | print do run do Rollback |
| 5 | Confirmar `GET /health` com `"version": "1.0.0"` e envio de denúncia funcionando | saída do `curl` |
| 6 | Registrar a causa e a correção (novo PATCH) | texto abaixo |

### Registro da simulação

- **Data/hora:**
- **Versão com falha:**
- **Sintoma observado:**
- **Tempo até detectar:**
- **Ação tomada:**
- **Versão restaurada:**
- **Causa raiz e correção definitiva:**
