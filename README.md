# Blender scripts for Strider bot

This Blender add-on reads bone angles from the Strider model during animation and streams them over WebSocket to the robot.

## Recommended setup: VS Code

Use [Blender Development by Jacques Lucke](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development) (`JacquesLucke.blender-development`) to launch Blender and develop the add-on from VS Code.

1. Install Blender and VS Code. The project manifest requires Blender 4.2 or newer; the bundled native wheels target Python 3.11. Choose a Blender installation with a matching Python version, or update the wheels for its bundled Python.
2. Open this repository's root folder in VS Code—the folder containing `__init__.py` and `blender_manifest.toml`, rather than just `src/`.
3. Open the Extensions view and install Blender Development. It is already listed in `.vscode/extensions.json`, so it also appears under workspace recommendations.
4. For local Python editor tooling, install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run `uv sync` from the repository root. Use `Python: Select Interpreter` to select the resulting `.venv` if using the Python extension. This environment is separate from Blender's bundled Python; `uv sync` does not install packages into Blender.
5. Copy `example.env` to `.env` if you do not already have one. Set `BOT_URL` to the robot's hostname or IP address, without a scheme or port. The add-on connects to `ws://<BOT_URL>:8080`.
6. Open the Command Palette (`Cmd+Shift+P` on macOS, `Ctrl+Shift+P` on Windows/Linux) and run `Blender: Start`. Select your Blender executable when prompted. On macOS, it is typically `/Applications/Blender.app/Contents/MacOS/Blender`. Allow the first launch to finish setting up the extension's support dependencies.
7. In the launched Blender window, open `model/strider-2.blend`. Select an armature and enter Pose Mode. The add-on adds `Send angle data` to the Pose menu. With the robot's WebSocket server running, use that command to start sending angles; use it again to stop. Play the animation to change the angles being sent. Armature and bone names must match `src/config.py`.

The VS Code extension recognizes `blender_manifest.toml` and links the project into Blender's development extension repository. You do not need to build and install a ZIP for each code edit. See the upstream [extension support guide](https://github.com/JacquesLucke/blender_vscode/blob/master/EXTENSION-SUPPORT.md) for details.

### Editing and debugging

- Edit the add-on in `src/`. This workspace already sets `blender.addon.reloadOnSave` to `true` in `.vscode/settings.json`. You can also run `Blender: Reload Addons` manually after edits.
- Set breakpoints in VS Code, then trigger the relevant action in the Blender session launched with `Blender: Start`. Inspect errors and printed messages in VS Code's Blender terminal/output.
- Stop sending angle data before reloading. Restart Blender if a reload leaves an existing connection or background thread running.
- Use the add-on workflow for this project: `src/main.py` uses package-relative imports, so running that file alone with `Blender: Run Script` or ordinary Python is not the setup described here.

Command reference: [Blender Development documentation](https://github.com/JacquesLucke/blender_vscode#readme).

### Dependency troubleshooting

The add-on's runtime dependencies are bundled in `wheels/` and listed in `blender_manifest.toml`. If startup reports a missing module such as `websockets` or `dotenv`, check the Blender output and confirm that the listed wheel files exist and support Blender's Python version and your platform. Installing a package into `.venv` alone will not fix a Blender import error. See the wheel instructions below when adding or updating runtime dependencies.

## Directory structure

- `src/`: add-on implementation and model configuration.
- `wheels/`: third-party Python wheels bundled with the Blender extension.
- `model/`: Blender models, including `strider-2.blend`.
- `script/`: development helper scripts.
- `blender_manifest.toml`: Blender extension metadata and bundled dependency list.
- `dist/`: packaged extension ZIP output.

## Packaging and adding dependencies

These steps are for updating bundled dependencies or building a distributable ZIP. For everyday development, use the VS Code workflow above.

The packages in the addons are installed in the form of wheels. When you are installing a new package that is not already used in this project you will need to create a wheel:

1. Run `source .venv/bin/activate`(make sure you have already ran `uv sync` and have the virtual environment)

Make sure to replace the following commands' `<package-name>` with the actual name of the package:

2. Run `python3.11 -m pip download <package-name> --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=macosx_11_0_arm64`
3. Run `python3.11 -m pip download <package-name> --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=manylinux_2_28_x86_64`
4. Run `python3.11 -m pip download <package-name> --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=win_amd64`

The commands above should have made a few new files in the `./wheels/` directory, so you will need to add those in the `blender_manifest.toml` file. For example:
```toml
wheels = [
  # ... previous wheel files
  "./wheels/<package-name>-<package-version>-cp311-cp311-macosx_11_0_arm64.whl",
  "./wheels/<package-name>-<package-version>-py3-none-any.whl",
  "./wheels/<package-name>-<package-version>-cp311-cp311-win_amd64.whl",
  # ... more wheel files
]
```

Once the dependencies was installed and wheel files were created you will also need to build the extension for blender to use it and blender provides a build cli command:
Linux: https://docs.blender.org/manual/en/dev/advanced/command_line/launch/linux.html
MacOS: https://docs.blender.org/manual/en/dev/advanced/command_line/launch/macos.html
Windows: https://docs.blender.org/manual/en/dev/advanced/command_line/launch/windows.html

Then run the following command:
`blender --command extension build --source-dir <directory path to this repo> --output-dir <directory path to this repo>/dist`
or for MacOS
`Blender --command extension build --source-dir <directory path to this repo> --output-dir <directory path to this repo>/dist`

> [!NOTE]
> If any issue occur reference the blender doc: https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html 

Once this has been created you can then open blender to add the addon from this cloned repository.
Go `Edit > preferences > add-ons` then top right hand corner has a `▽` in blender 4.3 or 4.2 may have install button. Click `install from disk`. Pick the newly generated zip file. If installation fails, inspect the error and resolve it before using the add-on; a failed installation does not confirm that its dependencies are available.
