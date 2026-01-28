# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] - 2024-XX-XX

### Adicionado
- Estrutura base do SDK como add-on do Blender/UPBGE
- Console JavaScript interativo usando Node.js do SDK
- Integração com text editor do Blender (legado, não mais registrada por padrão)
- Integração com game engine para controllers JavaScript
- Type definitions em `types/` para API BGE (para uso opcional em editores)
- Sistema de preferências para gerenciar SDK path
- Operadores para instalar/atualizar SDK
- Suporte a múltiplas plataformas (Windows, Linux, macOS)
- Documentação completa (README.md, INSTALL_DEPENDENCIES.md)
- Scripts de setup e download de dependências

### Estrutura
- `__init__.py`: Add-on principal seguindo padrão Armory
- `python/`: Módulos Python do SDK
  - `console/`: Console JavaScript
  - `runtime/`: Wrapper para Node.js
  - `game_engine/`: Integração com controllers
- `runtime/`: Diretório para executáveis Node.js
- `types/`: Type definitions para uso em editores
- `scripts/`: Scripts de setup e instalação

### Notas
- Node.js deve ser instalado manualmente ou via scripts
- SDK totalmente independente do UPBGE core
- Suporte a SDK local por projeto (./bge_js_sdk/)
- Suporte a variável de ambiente BGE_JAVASCRIPT_SDK
