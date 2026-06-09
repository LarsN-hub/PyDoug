from PyInstaller.utils.hooks import collect_all, copy_metadata

def hook(hook_api):
    packages = [
        "porespy"
    ]
    for package in packages:
        datas, binaries, hiddenimports = collect_all(package)
        datas += copy_metadata(package)
        hook_api.add_datas(datas)
        hook_api.add_binaries(binaries)
        hook_api.add_imports(*hiddenimports)
