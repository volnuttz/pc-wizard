# Releasing pc-wizard

pc-wizard follows Semantic Versioning. The package version, Git tag, executable
version output, changelog heading, and release title must agree.

## Release checklist

1. Confirm the quality and native-binary workflows pass on the release commit.
2. Update `version` in `pyproject.toml` and `__version__` in
   `src/pc_wizard/__init__.py`, then run `uv lock`.
3. Update `docs/roadmap.md` and user-facing documentation for the release.
   Add the release summary to `CHANGELOG.md`.
4. Run the complete local gate:

   ```console
   uv run ruff format --check .
   uv run ruff check .
   uv run pyright
   uv run pytest
   uv build --clear
   ```

5. Commit the release changes and push an annotated tag matching the version:

   ```console
   git tag -a vX.Y.Z -m "pc-wizard X.Y.Z"
   git push origin vX.Y.Z
   ```

The `Native binaries` workflow rebuilds and smoke-tests all platforms, creates
platform archives and SHA-256 files, and publishes them through a GitHub Release.
The release job verifies that the tag already exists and uses GitHub-generated
release notes.

If a tag build succeeds but its release job fails, fix the workflow on the default
branch and recover without moving the tag:

```console
gh workflow run "Native binaries" --ref main -f release_tag=vX.Y.Z
```

The manual run rebuilds and smoke-tests every artifact before publishing the
existing tag. Leave `release_tag` empty for ordinary non-release manual builds.
If `gh workflow run` returns `HTTP 403: Resource not accessible by integration`,
open **Actions → Native binaries → Run workflow** on GitHub, select `main`, enter
the existing tag in `release_tag`, and start the workflow there.

## Signing and notarization

Version 0.1.0 binaries are unsigned. Windows SmartScreen and macOS Gatekeeper may
therefore warn users or block first launch. Do not tell users that an unsigned
artifact is trusted merely because it was downloaded from GitHub; they should
verify its SHA-256 file before running it.

Code signing is deferred until the project has access to a Windows code-signing
certificate and an Apple Developer ID. Before a broader public release, add
Authenticode signing for Windows and Developer ID signing plus notarization for
macOS, then verify signatures in the native workflow before publication.
