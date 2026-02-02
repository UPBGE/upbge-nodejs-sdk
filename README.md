# UPBGE JavaScript SDK

Full SDK for JavaScript support in the UPBGE Game Engine, fully independent of the UPBGE core.

## Overview

This SDK provides JavaScript development support in UPBGE, including:

- **Interactive Console**: JavaScript console for quick code testing
- **External Editor Integration**: Quick open of the SDK/project in VS Code, Cursor, or a custom editor
- **Type Definitions**: Type definitions in `types/` for optional use in editors that support JSDoc / `.d.ts`
- **Game Engine Integration**: Integration with JavaScript controllers in the game engine

## Installation

### For End Users (Recommended)

**Plug-and-Play**: Download the official `upbge-javascript-sdk-X.X.X.zip` package, which includes all required binaries. See the "Option 2" section below.

### For Developers

If you are developing or contributing to the SDK, you will need to install dependencies manually:

1. **Directory structure**: Run `python scripts/setup_sdk.py`
2. **Node.js**: Run `python scripts/download_dependencies.py` or install manually (see `INSTALL_DEPENDENCIES.md` if needed)

### Option 1: Manual installation

1. Clone or download this repository
2. Run `python scripts/setup_sdk.py` to create the directory structure
3. Install dependencies (Node.js) — see `INSTALL_DEPENDENCIES.md` only if you want to install extra tools
4. In Blender, go to **Edit → Preferences → Add-ons**
5. Click **Install...** and select the `upbge-javascript` folder
6. Enable the "UPBGE JavaScript SDK" add-on
7. Configure the SDK path in the add-on preferences

### Option 2: Add-on installation (ZIP) — Recommended

1. **Download the official package** `upbge-javascript-sdk-X.X.X.zip` (includes all binaries)
2. In Blender/UPBGE, go to **Edit → Preferences → Add-ons**
3. Click **Install...** and select the downloaded ZIP file
4. Enable the "UPBGE JavaScript SDK" add-on
5. **Done!** The SDK is ready (plug-and-play, no extra dependencies to install)

![How to install](./assets/upbge-nodejs-sdk-installation.gif)

**Note for developers**: To build a distribution package with all binaries included, run:
```bash
python scripts/build_package.py
```

This will create a ZIP file ready for distribution, including the add-on and the Node.js runtime.

### Quick start

For a quick setup guide, see `SETUP.md`.

## Configuration

### Configure SDK path

1. Open **Edit → Preferences → Add-ons**
2. Select "UPBGE Node.js SDK"
3. Set **SDK Path** to the SDK directory
4. The SDK will load automatically

### SDK path options

The SDK can be configured in three ways (in order of priority):

1. **Environment variable**: `BGE_JAVASCRIPT_SDK` (absolute path)
2. **Local SDK**: `./bge_js_sdk/` relative to the .blend file
3. **Preferences**: Path set in the add-on preferences

### Persistent worker

By default, each time a JavaScript controller runs, the add-on starts a new Node.js process, runs your script, and then exits. For games with many controllers or heavy logic, that can add overhead.

You can enable **Use Persistent Worker** in the add-on preferences (**Edit → Preferences → Add-ons → UPBGE Node.js SDK → Advanced Settings**). When enabled:

- A single Node.js process is kept running for the whole game session.
- Scripts are sent to this process over stdin instead of spawning a new process per frame.
- This reduces the cost of starting Node.js repeatedly and can improve performance when many controllers run every frame.

The option is off by default so that the default behavior stays simple (one process per run). Turn it on if you notice lag or high CPU from frequent controller execution.

## SDK structure

```
upbge-javascript/
├── __init__.py              # Main add-on
├── python/                   # Python modules
│   ├── console/             # JavaScript console
│   ├── runtime/             # JavaScript runtime (Node.js wrapper)
│   └── game_engine/         # Game engine integration
├── runtime/                  # Node.js executables
│   ├── windows/
│   ├── linux/
│   └── macos/
├── lib/                      # (Optional) additional libraries and tools
└── types/                    # Type definitions for use in editors
    └── bge.d.ts
```

## Usage

### JavaScript console

1. Open the **Console** in Blender (Window → Toggle System Console or Shift+F4)
2. In the console language menu, select **JavaScript**
3. Type code and press Enter to run it

**JavaScript example:**
```javascript
>>> console.log("Hello, UPBGE!")
Hello, UPBGE!
>>> let x = 10 + 20
30
```

### JavaScript controllers

1. In the **Logic Editor**, add a **JavaScript Controller**
2. Select the controller and configure a JavaScript script using the add-on panel
3. The code runs in the game engine via Node.js

**Controller example:**
```javascript
// Move object forward
let obj = bge.logic.getCurrentObject();
if (obj) {
    obj.position[2] += 0.1;
}
```

### Type definitions (optional)

The `types/` directory contains optional `.d.ts` files for autocomplete in editors that support JSDoc/type definitions. They are not used by the add-on at runtime.

### Using TypeScript

To use TypeScript (or get full type checking and IntelliSense for the BGE API in JavaScript), include the SDK type definitions in your project. Add the files under `types/` to your `tsconfig.json` so the compiler and editor pick up the `bge` namespace and related types.

**Option A — SDK as part of your project**  
If the SDK lives inside your project (e.g. in a subfolder), add the `types` folder to `include`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true
  },
  "include": [
    "src/**/*",
    "path/to/upbge-nodejs-sdk/types/**/*.d.ts"
  ]
}
```

**Option B — SDK installed elsewhere**  
If the SDK is in another directory (e.g. add-on path), use `typeRoots` or a direct path in `include` so your `tsconfig.json` points at the SDK `types`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "typeRoots": ["./node_modules/@types", "C:/path/to/sdk/types"]
  },
  "include": ["src/**/*"]
}
```

Or reference the definition files explicitly:

```json
{
  "include": ["src/**/*", "C:/path/to/sdk/types/index.d.ts"]
}
```

Replace `C:/path/to/sdk` with the actual path to your SDK (or use a relative path). After that, types like `bge.logic`, `bge.constraints`, `GameObject`, and `Scene` will be available for autocomplete and type checking. The game engine still runs the compiled JavaScript (or the add-on’s JS runtime); the `.d.ts` files are only for development.

## Requirements

- **UPBGE**: Version 5.0 or later
- **Node.js**: Included in the SDK (no external installation required)

## Development

### Code structure

- `python/console/`: JavaScript console
- `python/runtime/`: Node.js wrapper for execution
- `python/game_engine/`: Controller integration

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a branch for your feature
3. Commit your changes
4. Open a Pull Request

## License

GPL-2.0-or-later (same license as UPBGE)

## Links

- [Documentation](https://github.com/UPBGE/upbge-javascript-sdk/wiki)
- [Issues](https://github.com/UPBGE/upbge-javascript-sdk/issues)
- [UPBGE](https://upbge.org/)

## Notes

- The SDK is fully independent of the UPBGE core
- Node.js is included in the SDK
- The SDK can be updated independently of UPBGE
- Support for multiple SDK versions per project
