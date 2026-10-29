# Apresentação ao CNPq: fonte editável

Apresentamos o laboratório em 15/09/2026. Esta pasta contém a versão atual dos slides em Slidev e os recursos locais utilizados.

## Abrir para editar

Requisitos: Node.js 22.12 ou superior e pnpm 10.32.1.

```sh
pnpm install --frozen-lockfile
pnpm dev
```

Abra o endereço local informado no terminal. Para gerar uma versão web, execute pnpm build. A saída será criada em ../04-exportacoes/web. O PDF pronto está em ../apresentacao-cnpq.pdf.

slides.md contém os slides. components, layouts e styles definem os elementos visuais. public reúne os recursos usados pela apresentação. As licenças das fontes estão em public/fontes. Os dados de acesso dos exemplos públicos foram substituídos por marcadores.
