// Executa a mesma validação da versão compilada e gera o PDF com as capturas Full HD.
process.argv.push('--pdf')
await import('./validar.mjs')
