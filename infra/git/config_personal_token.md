## GitHub: configurando e usando Personal Access Tokens (PAT)

Este tutorial mostra, passo a passo, como criar, configurar e usar um Personal Access Token (PAT) no GitHub para operações via HTTPS (git clone/pull/push), automações locais e integração com registries (GHCR, npm). Inclui práticas de segurança, rotação e troubleshooting em Linux.

---

## 1) O que é um PAT e quando usar

Um PAT funciona como uma “senha” de API para autenticar no GitHub sem usar usuário/senha ou SSH. Use PAT quando:
- Você usa HTTPS para `git clone/pull/push` (em vez de SSH).
- Precisa autenticar scripts locais, o `gh` (GitHub CLI) ou ferramentas que não suportam SSH.
- Vai publicar/baixar artefatos de registries do GitHub (Packages/GHCR).

Preferências (em ordem):
- Para CI no GitHub Actions, prefira o `GITHUB_TOKEN` embutido sempre que possível; use PAT apenas se precisar acessar outro repo/organização com permissões específicas.
- Para dev local, avalie SSH (chaves) como alternativa mais conveniente. PAT é útil quando a rede bloqueia SSH ou para ferramentas que pedem token.

---

## 2) Tipos de tokens: Fine‑grained vs Classic

GitHub hoje recomenda “Fine‑grained personal access tokens”.

- Fine‑grained PAT (recomendado): escopo por repositório/organização, permissões granulares (apenas leitura/escrita específicas) e expiração obrigatória.
- Classic PAT: escopos amplos (ex.: `repo`, `workflow`, `gist`), ainda suportado mas menos seguro.

Quando possível, crie um fine‑grained PAT e dê acesso apenas aos repositórios e permissões necessárias.

---

## 3) Criando um Fine‑grained PAT (UI Web)

1. No GitHub (web), clique na sua foto (top‑right) → Settings.
2. No menu lateral, vá em “Developer settings”.
3. “Personal access tokens” → “Fine‑grained tokens” → “Generate new token”.
4. Preencha:
   - Nome (Note para que serve, ex.: "Dev‑local HTTPS"), Expiração (obrigatória), Owner (org/usuário).
   - Repositories: selecione os repositórios (ou toda a org, se apropriado).
   - Permissions: marque exatamente o necessário. Para git push/pull: `Repository permissions → Contents: Read and write`.
5. Clique em “Generate token” e copie o valor mostrado uma única vez. Guarde com segurança.

Permissões comuns (fine‑grained):
- Git push/pull: `Repository → Contents: Read and write`.
- Releases: `Repository → Metadata (Read)` e `Repository → Contents (Write)`, às vezes `Actions (Read)`.
- Packages/GHCR: `Repository → Packages: Read/Write` (ou `Organization → Packages` se for no nível da org).

---

## 4) Criando um Classic PAT (se necessário)

1. Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token.
2. Defina Expiration (não deixe "No expiration").
3. Selecione os escopos mínimos:
   - `repo` (para acesso a repos privados; inclui vários subescopos).
   - `workflow` (se precisa disparar/ler Actions).
   - `read:org` (se scripts precisam ler membros/teams).
   - `write:packages`/`read:packages` (para GHCR/Packages).
4. Gere e guarde o token com segurança.

---

## 5) Usando o PAT com Git via HTTPS

Você pode usá‑lo de duas formas: digitar quando o Git pedir a senha, ou configurar um helper para salvar com segurança.

### 5.1 Clone / push usando PAT (prompt)

```bash
# ao clonar via HTTPS, informe seu usuário GitHub como username e o PAT como password
git clone https://github.com/OWNER/REPO.git
# Username: seu_usuario
# Password: <cole o PAT>
```

### 5.2 Armazenamento seguro no Linux (credential helpers)

Opções comuns:
- cache (memória, expira):
  ```bash
  git config --global credential.helper 'cache --timeout=7200'  # 2h
  ```
- libsecret (guarda no keyring do sistema, ex.: GNOME Keyring):
  ```bash
  # Instale o helper (em distros Debian/Ubuntu):
  sudo apt-get install -y libsecret-1-0 libsecret-1-dev
  # Em algumas distros, o binário já vem como git-credential-libsecret
  git config --global credential.helper libsecret
  ```
- store (plaintext – não recomendado):
  ```bash
  git config --global credential.helper store  # salva em texto puro em ~/.git-credentials
  ```

Após configurar o helper, faça um `git pull`/`push` e, no primeiro uso, informe username + PAT. O helper salvará para os próximos usos.

### 5.3 Atualizando a URL remota se necessário

```bash
# certifique-se de que a URL usa HTTPS (para usar PAT)
cd /caminho/do/seu/repo
git remote -v
# se estiver em SSH, troque para HTTPS
git remote set-url origin https://github.com/OWNER/REPO.git
```

---

## 6) Usando o PAT com GitHub CLI (gh)

O `gh` aceita autenticação por token via pipe e variável de ambiente.

```bash
# login com token (não ecoa na tela)
export GH_TOKEN='<seu_pat>'
printf "%s" "$GH_TOKEN" | gh auth login --with-token

# verificar
gh auth status
```

Dica: você também pode usar `GITHUB_TOKEN` como nome de variável; o `gh` reconhece ambos.

---

## 7) Usando o PAT em registries do GitHub

### 7.1 GitHub Container Registry (GHCR)

Scopes necessários: `read:packages` para pull e `write:packages` para push.

```bash
# login
echo "$PAT" | docker login ghcr.io -u seu_usuario --password-stdin

# tag e push de uma imagem
IMAGE=ghcr.io/OWNER/REPO/app:latest
docker build -t "$IMAGE" .
docker push "$IMAGE"
```

### 7.2 GitHub Packages (npm)

`.npmrc` no projeto ou global:

```ini
@OWNER:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GH_TOKEN}
```

Depois:
```bash
npm publish --access public   # (se aplicável)
```

---

## 8) Boas práticas de segurança

- Mínimo necessário: defina somente as permissões estritamente necessárias.
- Expiração curta e rotação periódica (30~90 dias conforme política interna).
- Nunca comite PAT em código, .env ou histórico (ative secret scanning no repo/org).
- Prefira helpers seguros (libsecret/OS keychain) em vez de `store` (plaintext).
- Revogue tokens não utilizados. Nomeie tokens de forma descritiva (para saber onde usou).
- Para CI no GitHub, prefira `GITHUB_TOKEN`; use PAT apenas se precisar alcançar outro repo/organização/escopos.

---

## 9) Revogar, regenerar e rotacionar

- Revogar: Settings → Developer settings → Personal access tokens → (Fine‑grained ou Classic) → Revoke.
- Regenerar: crie um novo token, teste e só então revogue o antigo para evitar indisponibilidade.
- Em scripts/serviços, armazene tokens como variáveis de ambiente e troque a origem do valor (secret manager) durante a rotação.

---

## 10) Troubleshooting

- 401/403 ao `git push`:
  - Verifique se a URL é HTTPS e o PAT tem permissão `Contents: Read and write` no repo correto (fine‑grained) ou `repo` (classic).
  - Confirme se o PAT não expirou.
- Prompt de senha sempre reaparece:
  - Configure um credential helper (cache/libsecret) e teste novamente.
  - Remova credenciais antigas: `git credential reject` (irá solicitar host/username); ou limpe do keyring.
- Erro ao usar GHCR:
  - Garanta `write:packages` no PAT para push (ou `read:packages` para pull) e que a imagem está tagueada como `ghcr.io/OWNER/REPO/...`.
- CI no GitHub não reconhece PAT:
  - Em Actions, salve o PAT em `Settings → Secrets and variables → Actions` e acesse via `${{ secrets.MY_PAT }}`. Atente para `permissions:` do job.

---

## 11) Apêndice: usando `.netrc` (opcional, avançado)

Você pode automatizar autenticação com `.netrc`, mas cuidado: é texto puro.

```bash
cat >> ~/.netrc <<'EOF'
machine github.com
  login seu_usuario
  password SEU_PAT
EOF
chmod 600 ~/.netrc
```

Sempre prefira credential helpers seguros quando possível.
