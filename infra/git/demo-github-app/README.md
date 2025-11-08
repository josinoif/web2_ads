# Demo GitHub App (Node.js + Express)

Pequeno serviço para demonstrar Pull Requests, GitHub Actions (CI/CD), releases versionadas, governança e segurança.

## Endpoints

- `GET /health` → `{ "status": "ok" }`
- `GET /sum?a=2&b=3` → `{ "result": 5 }`
- `POST /echo` (JSON) → `{ "youSent": { ... } }`

## Scripts

```bash
npm ci        # instala dependências (usa package-lock)
npm test      # executa testes com Node test runner
npm run lint  # ESLint
npm run build # esbuild gera dist/server.js
npm run dev   # inicia servidor (porta 3000)
```

## Fluxo de Desenvolvimento (Exemplo)

1. Crie uma branch: `git switch -c feat/nova-funcionalidade`.
2. Implemente e rode `npm test && npm run lint`.
3. Abra Pull Request vinculando issue (`Closes #ID`).
4. Aguarde CI (workflow `ci.yml`) passar em todas as versões de Node.
5. Após aprovação + checks verdes, faça merge (squash recomendado).
6. Gere tag de release: `git tag -a v0.1.0 -m "Release 0.1.0" && git push origin v0.1.0`.
7. Workflow `release.yml` publica artefatos em **Releases**.

## CI / Workflows

- `ci.yml`: roda em push e PR.
  - Matrizes Node 18 & 20
  - Cache npm
  - Steps: install → lint → test → build → artefato `dist/`
- `release.yml`: dispara em tag `v*.*.*` e cria release.
- `codeql.yml`: análise estática de segurança semanal e em PRs.

Se este projeto estiver em subdiretório (monorepo), mantenha os `working-directory` conforme já configurado. Se virar raiz do repo, remova `working-directory` e ajuste caminhos para `.`.

## Governança e Segurança

- `CODEOWNERS`: exige aprovação do proprietário.
- Templates de PR & issues: padronizam comunicação.
- `dependabot.yml`: atualizações semanais de dependências.
- `SECURITY.md`: política de reporte.
- CodeQL + (opcional) secret scanning e branch protection.

## Próximos Passos Sugeridos

- Adicionar cobertura (nyc / c8) e badge.
- Publicar imagem Docker via novo workflow (GHCR).
- Usar Environments (staging/prod) com aprovação manual.
- Integrar CodeCov ou SonarCloud.

## Licença

Uso educacional / exemplo. Ajuste conforme sua política.
