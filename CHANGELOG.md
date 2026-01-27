# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] - 2024-XX-XX

### Adicionado
- Estrutura base do SDK como add-on do Blender/UPBGE
- Console JavaScript interativo usando Node.js do SDK
- Console TypeScript interativo com compilação automática
- Integração com text editor do Blender
- Sistema de autocomplete via TypeScript Language Server (estrutura base)
- Integração com game engine para controllers JavaScript/TypeScript
- Type definitions TypeScript para API BGE
- Sistema de preferências para gerenciar SDK path
- Operadores para instalar/atualizar SDK
- Suporte a múltiplas plataformas (Windows, Linux, macOS)
- Documentação completa (README.md, INSTALL_DEPENDENCIES.md)
- Scripts de setup e download de dependências

### Estrutura
- `__init__.py`: Add-on principal seguindo padrão Armory
- `python/`: Módulos Python do SDK
  - `console/`: Consoles JavaScript e TypeScript
  - `editor/`: Integração com editor e autocomplete
  - `runtime/`: Wrapper para Node.js
  - `game_engine/`: Integração com controllers
- `runtime/`: Diretório para executáveis Node.js
- `lib/`: Bibliotecas (TypeScript compiler, LSP)
- `types/`: Type definitions TypeScript
- `scripts/`: Scripts de setup e instalação

### Notas
- Node.js, TypeScript e LSP devem ser instalados manualmente ou via scripts
- SDK totalmente independente do UPBGE core
- Suporte a SDK local por projeto (./bge_js_sdk/)
- Suporte a variável de ambiente BGE_JAVASCRIPT_SDK
