from pathlib import Path

from PyInstaller.utils.hooks import copy_metadata


project_root = Path(SPECPATH)

analysis = Analysis(
    [str(project_root / "src" / "pc_wizard" / "__main__.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=copy_metadata("pc-wizard"),
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="pc-wizard-onefile",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
