#!/usr/bin/env python3
# fixed-poetry-build.py - Poetry build with fixes for dash-mantine-components and dash-iconify

import os
import sys
import platform
import subprocess
import shutil


def run_silent(cmd):
    """Run command silencing stdout/stderr, return (ok: bool, output: str|None)."""
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        return True, out
    except subprocess.CalledProcessError:
        return False, None
    except Exception:
        return False, None


def get_dmc_path():
    """Get dash-mantine-components path"""
    ok, out = run_silent([
        'poetry', 'run', 'python', '-c',
        'import dash_mantine_components, os; print(os.path.dirname(dash_mantine_components.__file__))'
    ])
    if ok and out:
        path = out.strip()
        print(f"✅ dash-mantine-components: {path}")
        return path
    print("⚠️ dash-mantine-components path not found")
    return None


def get_iconify_path():
    """Get dash_iconify path"""
    ok, out = run_silent([
        'poetry', 'run', 'python', '-c',
        'import dash_iconify, os; print(os.path.dirname(dash_iconify.__file__))'
    ])
    if ok and out:
        path = out.strip()
        print(f"✅ dash-iconify: {path}")
        return path
    print("⚠️ dash-iconify path not found")
    return None


def poetry_install_with_build():
    print("📦 Installing dependencies (poetry install --with build)")
    try:
        subprocess.check_call(
            ['poetry', 'install', '--with', 'build'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ Dependencies installed")
        return True
    except Exception:
        print("⚠️ Dependency installation error (continuing)")
        return False


def detect_maui_modules():
    print("🔧 Detecting MAUI submodules")
    modules = []
    for module in ['eda', 'io', 'acoustic_indices']:
        ok, _ = run_silent(['poetry', 'run', 'python', '-c', f'import maui.{module}'])
        if ok:
            modules.append(f'maui.{module}')
            print(f"✅ maui.{module}")
        else:
            print(f"⚠️ maui.{module} not available")
    return modules


def main():
    print("🎵 Maui-Software UI Build")
    print("=" * 50)

    # Poetry
    ok, _ = run_silent(['poetry', '--version'])
    if not ok:
        print("❌ Poetry not found")
        return 1
    print("✅ Poetry")

    # Install deps
    poetry_install_with_build()

    # Detect MAUI
    maui_modules = detect_maui_modules()

    # Data packages
    dmc_path = get_dmc_path()
    iconify_path = get_iconify_path()

    # Clean build
    for d in ['build', 'dist']:
        if os.path.exists(d):
            shutil.rmtree(d)

    # Build config
    system = platform.system().lower()
    exe_name = f'Maui-Software-UI-{system.title()}'
    sep = ':' if system != 'windows' else ';'

    build_args = [
        'poetry', 'run', 'pyinstaller',
        '--onefile',
        '--add-data', f'pages{sep}pages',
        '--add-data', f'assets{sep}assets',
        '--add-data', f'utils{sep}utils',
        '--add-data', f'acoustic_indices{sep}acoustic_indices',
        '--name', exe_name
    ]

    # Include data files (DMC/Iconify)
    if dmc_path and os.path.exists(dmc_path):
        build_args.extend(['--add-data', f'{dmc_path}{sep}dash_mantine_components'])
        build_args.extend(['--collect-data', 'dash_mantine_components'])
        print("✅ DMC data included")

    if iconify_path and os.path.exists(iconify_path):
        build_args.extend(['--add-data', f'{iconify_path}{sep}dash_iconify'])
        build_args.extend(['--collect-data', 'dash_iconify'])
        print("✅ Iconify data included")

    # Hidden imports
    critical_imports = [
        'maui',
        'jaraco.text',
        'dash_mantine_components',
        'dash_mantine_components._imports_',
        'dash_mantine_components.utils',
        'dash_iconify',
        'dash_iconify.DashIconify',
        'dash_iconify._imports_',
        'dash',
        'dash.dcc',
        'dash.html',
        'utils.io_utils',
        'utils.definitions',
        'utils.random_utils',
        'acoustic_indices.acoustic_indices_calculation',
    ] + maui_modules

    for module in critical_imports:
        build_args.extend(['--hidden-import', module])

    # Excludes
    build_args.extend([
        '--exclude-module', 'tkinter',
        'app.py'
    ])

    print("🏗️  Building executable")
    try:
        # Silence PyInstaller verbosity; only show our prints or final errors
        subprocess.check_call(build_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        exe_path = f'dist/{exe_name}'
        if os.path.exists(exe_path):
            if system != 'windows':
                os.chmod(exe_path, 0o755)
            size = os.path.getsize(exe_path) // 1024 // 1024
            print(f"✅ Built: {exe_path} ({size} MB)")
            print(f"🚀 Run: ./{exe_path}")
            return 0
        else:
            print("❌ Executable not created")
            return 1

    except subprocess.CalledProcessError:
        # If build fails, re-run once capturing stderr to show a short tail for debugging
        print("❌ Build failed")
        try:
            proc = subprocess.Popen(build_args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            _, err = proc.communicate()
            if err:
                tail = "\n".join(err.splitlines()[-25:])  # last 25 lines
                print("— Build error (tail) —")
                print(tail)
        except Exception:
            pass
        return 1


if __name__ == '__main__':
    sys.exit(main())

