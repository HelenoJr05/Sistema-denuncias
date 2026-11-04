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

> **Dados:** a partir da `v1.2.0` as denúncias ficam no PostgreSQL (volume
> `pgdata`), que **não** é alterado pelo rollback da imagem. Só o código volta
> de versão.
>
> **Atenção ao voltar para uma versão anterior à `1.2.0`:** essas versões gravam
> em arquivo JSON (volume `denuncias_data`) e não enxergam o banco. As denúncias
> registradas no PostgreSQL continuam guardadas e voltam a aparecer ao
> restaurar a `1.2.0` ou superior.

## Simulação documentada

Simulação executada em ambiente de homologação simulado (GitHub Actions).
Os prints ficam na pasta [`docs/evidencias/`](evidencias/).

| Passo | O que foi feito | Evidência |
|---|---|---|
| 1 | Lançada a `v1.0.0` (versão estável). Pipeline CD verde: testes, build, push no GHCR, release e deploy com smoke test. Imagem publicada com as tags `1.0.0` e `latest`. | [`print pipeline.png`](evidencias/print%20pipeline.png), [`print deploy.png`](evidencias/print%20deploy.png), [`package print.png`](evidencias/package%20print.png), [`print notas.png`](evidencias/print%20notas.png) |
| 2 | Introduzido um defeito de propósito no `Dockerfile` (`CMD` apontando para `main:apps` em vez de `main:app`), via Pull Request. O CI passou, pois ele testa só o código Python. Lançada a `v1.1.0`. | PR `fix/defeito-simulado-v1-1-0` e tag `v1.1.0` |
| 3 | O CD da `v1.1.0` construiu e publicou a imagem, mas o deploy em homologação **falhou** no smoke test: o container não iniciava. O log mostrou `Attribute "apps" not found in module "main"`. | [`evidencia rollback 1.png`](evidencias/evidencia%20rollback%201.png), [`evidencia rollback 2.png`](evidencias/evidencia%20rollback%202.png), [`evidencia rollback 3.png`](evidencias/evidencia%20rollback%203.png) |
| 4 | Executado o workflow **Rollback** informando `1.0.0`. A imagem dessa versão foi baixada do registry e o ambiente voltou a subir. | [`evidencia rollback 4.png`](evidencias/evidencia%20rollback%204.png) |
| 5 | O resumo do rollback confirmou a versão restaurada `1.0.0` e o smoke test (`/health` e envio de denúncia) funcionando. | [`evidencia rollback 5.png`](evidencias/evidencia%20rollback%205.png) |
| 6 | Corrigido o `Dockerfile` por Pull Request (#7) e lançada a `v1.1.1`. Deploy verde, versão `1.1.1` no ar. | [`evidencia v1.1.1.png`](evidencias/evidencia%20v1.1.1.png), [`evidencia release.png`](evidencias/evidencia%20release.png) |

### Registro da simulação

- **Data/hora:** 04/11/2026, 10:03 (horário de Brasília)
- **Versão com falha:** `v1.1.0`
- **Sintoma observado:** deploy em homologação reprovado no smoke test; `curl` sem conseguir conectar na porta 8000 durante cerca de 40 segundos.
- **Tempo até detectar:** cerca de 1min30 após a publicação da release (testes 10s + build 30s + deploy 49s).
- **Ação tomada:** execução do workflow Rollback para a versão `1.0.0` (14s).
- **Versão restaurada:** `1.0.0`, validada por smoke test.
- **Causa raiz:** erro de digitação no `CMD` do `Dockerfile` (`main:apps`). O uvicorn não encontrou o objeto da aplicação e o container reiniciava em loop.
- **Correção definitiva:** PR #7 corrigindo o `CMD`; lançada a `v1.1.1`.

### Lições aprendidas e melhorias

- O CI não detectou o defeito, porque não constrói nem sobe a imagem. Melhoria possível: adicionar um build da imagem e um teste de inicialização (`/health`) ao CI, para barrar o problema antes do merge.
- O pipeline publicou a tag `latest` apontando para a `v1.1.0` **antes** de o deploy ser validado. Durante a falha, quem usasse `latest` receberia a versão com defeito. Melhoria possível: só mover a tag `latest` depois que o deploy em homologação passar.
- O rollback funcionou como esperado, e o smoke test do deploy foi o que impediu a versão defeituosa de ser considerada saudável.
