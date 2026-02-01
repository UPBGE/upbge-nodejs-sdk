# Guia Rápido de Setup

Este é um guia rápido para configurar o UPBGE Node.js SDK.

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

3. Dependências adicionais (opcional)
   Consulte `INSTALL_DEPENDENCIES.md` se precisar de Node.js fora do pacote.

## Instalação no Blender/UPBGE

1. Abra o Blender/UPBGE
2. Vá em **Edit → Preferences → Add-ons**
3. Clique em **Install...** e selecione a pasta `upbge-javascript` ou um arquivo ZIP
4. Ative o add-on "UPBGE Node.js SDK"
5. Configure o **SDK Path** nas preferências do add-on
   - Pode ser o caminho absoluto para `upbge-javascript`
   - Ou use variável de ambiente `BGE_JAVASCRIPT_SDK`
   - Ou coloque SDK em `./bge_js_sdk/` relativo ao arquivo .blend

## Verificação

Após instalar, verifique se os seguintes arquivos existem:

- `runtime/windows/node.exe` (Windows) ou equivalente para sua plataforma

## Uso

1. Abra o Console no Blender (Window → Toggle System Console)
2. No menu de linguagem, selecione **JavaScript**
3. Digite código e pressione Enter para executar

## Troubleshooting

### Node.js não encontrado
- Verifique se `node.exe` (Windows) ou `node-linux64`/`node-osx` está em `runtime/`
- Verifique se o SDK path está configurado corretamente nas preferências

### JavaScript não executa
- Verifique se Node.js está em `runtime/` ou no PATH do sistema
- Verifique se o SDK path está correto nas preferências do add-on

## Próximos Passos

- Consulte `README.md` para documentação completa
- Consulte `INSTALL_DEPENDENCIES.md` para detalhes de instalação
- Consulte `CHANGELOG.md` para histórico de mudanças
