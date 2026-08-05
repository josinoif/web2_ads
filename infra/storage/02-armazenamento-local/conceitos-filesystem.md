# Armazenamento local (filesystem)

## Introdução

No **armazenamento local**, o backend da aplicação recebe o arquivo enviado pelo cliente (via multipart/form-data) e o grava em um **diretório no disco** do servidor. Não há serviço externo: a pasta pode estar no mesmo servidor da API ou em um volume montado. Essa abordagem é a mais simples de implementar e não gera custo adicional de infraestrutura de storage.

---

## Vantagens

- **Simplicidade**: basta configurar um caminho (ex.: `uploads/`) e gravar o arquivo com a biblioteca de upload (ex.: Multer no Express).
- **Zero custo extra**: usa o disco que já existe na máquina.
- **Controle total**: você define nomes, subpastas e permissões no sistema de arquivos.
- **Debugging**: inspecionar arquivos no disco é direto (listagem, tamanho, tipo).

---

## Limitações

- **Escala**: em ambiente com **múltiplas instâncias** (vários servidores atrás de um load balancer), cada instância tem seu próprio disco. Um upload que cai na instância A não fica visível na instância B; não há “disco compartilhado” por padrão. Para escalar com filesystem seria necessário um sistema de arquivos compartilhado (NFS, etc.), o que aumenta a complexidade.
- **Backup e recuperação**: backup do disco e políticas de retenção são responsabilidade da equipe; não há durabilidade gerenciada por um provedor.
- **Capacidade**: o disco pode encher; é preciso monitorar e eventualmente limpar ou arquivar arquivos antigos.

Por isso, o filesystem é recomendado para **desenvolvimento**, **protótipos** ou **produção com um único servidor** e volume de arquivos controlado.

---

## Boas práticas

1. **Diretório fora do código**: não salve uploads dentro da pasta do repositório (ex.: `src/uploads`). Use um caminho configurável (variável de ambiente) fora do projeto, para evitar que arquivos sejam commitados e para facilitar backup isolado.
2. **Nomes únicos**: gere nomes únicos para o arquivo (UUID, hash ou timestamp + nome original) para evitar sobrescrita e conflitos quando dois usuários enviam arquivos com o mesmo nome.
3. **Validação no backend**: sempre valide tipo (extensão e/ou content-type) e tamanho máximo no servidor. Não confie apenas na validação do frontend.
4. **Permissões**: configure o diretório de uploads com permissões restritas; o servidor deve poder escrever, mas o acesso direto ao sistema de arquivos por outros usuários deve ser evitado.
5. **Download**: sirva o arquivo via endpoint da API (leitura do disco e envio na resposta) ou, se o servidor for estático, com regras que impeçam listagem de diretório e acesso a caminhos fora da pasta de uploads.

---

## Conclusão

O filesystem é a opção mais direta para persistir arquivos quando a aplicação roda em um único servidor e o volume é pequeno. Respeitando as boas práticas acima, você reduz riscos de segurança e sobrescrita. No [tutorial-upload-disco.md](tutorial-upload-disco.md) você implementará uma API Express com upload e download em disco.
