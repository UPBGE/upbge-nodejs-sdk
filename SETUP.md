# Guia Rápido de Setup

Este é um guia rápido para configurar o UPBGE JavaScript/TypeScript SDK.

## Setup Inicial

1. **Estrutura de Diretórios**
   ```bash
   python scripts/setup_sdk.py
   ```
   Isso criará todos os diretórios necessários.

2. **Instalar Node.js**
   ```bash
   python scripts/download_dependencies.py
   ```
   Isso baixará e instalará Node.js para sua plataforma.

3. **Instalar TypeScript e LSP**
   Consulte `INSTALL_DEPENDENCIES.md` para instruções detalhadas.

## Instalação no Blender/UPBGE

1. Abra o Blender/UPBGE
2. Vá em **Edit → Preferences → Add-ons**
3. Clique em **Install...** e selecione a pasta `upbge-javascript` ou um arquivo ZIP
4. Ative o add-on "UPBGE JavaScript/TypeScript SDK"
5. Configure o **SDK Path** nas preferências do add-on
   - Pode ser o caminho absoluto para `upbge-javascript`
   - Ou use variável de ambiente `BGE_JAVASCRIPT_SDK`
   - Ou coloque SDK em `./bge_js_sdk/` relativo ao arquivo .blend

## Verificação

Após instalar, verifique se os seguintes arquivos existem:

- `runtime/windows/node.exe` (Windows) ou equivalente para sua plataforma
- `lib/typescript/tsc` ou `tsc.exe`
- `lib/lsp/typescript-language-server`

## Uso

1. Abra o Console no Blender (Window → Toggle System Console)
2. No menu de linguagem, selecione **JavaScript** ou **TypeScript**
3. Digite código e pressione Enter para executar

## Troubleshooting

### Node.js não encontrado
- Verifique se `node.exe` (Windows) ou `node-linux64`/`node-osx` está em `runtime/`
- Verifique se o SDK path está configurado corretamente nas preferências

### TypeScript não funciona
- Verifique se `tsc` está em `lib/typescript/`
- Verifique se Node.js está instalado e funcionando

### LSP não funciona
- Verifique se `typescript-language-server` está em `lib/lsp/`
- Verifique se a opção "Enable Language Server Protocol" está ativada nas preferências

## Próximos Passos

- Consulte `README.md` para documentação completa
- Consulte `INSTALL_DEPENDENCIES.md` para detalhes de instalação
- Consulte `CHANGELOG.md` para histórico de mudanças
