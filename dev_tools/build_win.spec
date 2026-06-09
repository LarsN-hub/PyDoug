# build.spec

from PyInstaller.utils.hooks import (
    collect_all,
    collect_submodules,
    copy_metadata,
)

napari_datas, napari_binaries, napari_hidden = collect_all("napari")
builtins_datas, builtins_binaries, builtins_hidden = collect_all("napari_builtins")
svg_datas, svg_binaries, svg_hidden = collect_all("napari_svg")
vispy_datas, vispy_binaries, vispy_hidden = collect_all("vispy")
magicgui_datas, magicgui_binaries, magicgui_hidden = collect_all("magicgui")
cmasher_datas, cmasher_binaries, cmasher_hidden = collect_all("cmasher")
chardet_datas, chardet_binaries, chardet_hidden = collect_all("chardet")

datas = (
    napari_datas +
    vispy_datas +
    magicgui_datas +
    cmasher_datas +
    builtins_datas +
    svg_datas +
    chardet_datas
)

datas += copy_metadata("napari")
datas += copy_metadata("magicgui")
datas += copy_metadata("vispy")
datas += copy_metadata("imageio")
datas += copy_metadata("qtpy")
datas += copy_metadata("chardet")
datas += copy_metadata("urllib3")
datas += copy_metadata("requests")

binaries = (
    napari_binaries +
    vispy_binaries +
    magicgui_binaries +
    cmasher_binaries +
    builtins_binaries +
    svg_binaries +
    chardet_binaries
)

hiddenimports = (
    napari_hidden +
    vispy_hidden +
    magicgui_hidden +
    cmasher_hidden +
    builtins_hidden +
    svg_hidden +
    chardet_hidden
)

hiddenimports += collect_submodules("napari_builtins")
hiddenimports += collect_submodules("qtpy")
hiddenimports = [x for x in hiddenimports if "charset_normalizer" not in x]

a = Analysis(
    ["PyDoug/__main__.py"],
    pathex = ["."],
    binaries = binaries,
    datas = datas,
    hiddenimports = hiddenimports,
    excludedimports = ["charset_normalizer"],
    hookspath = ["PyDoug/hooks"]
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries = True,
    name = "PyDoug_Windows",
    console = True
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name = "PyDoug_Windows"
)
