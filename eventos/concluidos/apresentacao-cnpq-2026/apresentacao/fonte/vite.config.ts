export default {
  build: { emptyOutDir: true },
  plugins: [{
    name: 'idioma-portugues',
    transformIndexHtml(html: string) { return html.replace('<html lang="en">', '<html lang="pt-BR">') },
  }],
}
