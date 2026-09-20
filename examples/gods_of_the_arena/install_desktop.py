#!/usr/bin/env python3
"""Install a macOS desktop launcher for the current local GotA build.

Requires Pillow and macOS iconutil. The launcher uses this checkout's assets
and refreshes its bundled executable after subsequent native builds.
"""

import os
from pathlib import Path
import plistlib
import shlex
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps


def install():
    if sys.platform != "darwin":
        raise SystemExit("The desktop launcher requires macOS.")
    root = Path(__file__).resolve().parents[2]
    binary = root / "examples/gods_of_the_arena/gota"
    logo = root.parent / "polyworld_data/themes/gota/gota_logo.png"
    app = Path.home() / "Desktop/Gods of the Arena.app"
    identifier = "com.softmax.polyworld.gods-of-the-arena"
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise SystemExit("Build examples/gods_of_the_arena/gota.nim first.")
    if app.exists():
        info = app / "Contents/Info.plist"
        if not info.is_file() or plistlib.loads(info.read_bytes()).get(
            "CFBundleIdentifier"
        ) != identifier:
            raise SystemExit(f"Another application already occupies {app}")
    contents = app / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    macos.mkdir(parents=True, exist_ok=True)
    resources.mkdir(parents=True, exist_ok=True)

    # Package the existing logo in standard square icon representations.
    # Preserve its aspect ratio and alpha; the artwork itself is unchanged.
    with Image.open(logo) as source, tempfile.TemporaryDirectory() as temporary:
        iconset = Path(temporary) / "AppIcon.iconset"
        iconset.mkdir()
        for points in (16, 32, 128, 256, 512):
            for density in (1, 2):
                size = points * density
                canvas = Image.new("RGBA", (size, size))
                fitted = ImageOps.contain(
                    source.convert("RGBA"), (size, size), Image.Resampling.LANCZOS
                )
                canvas.alpha_composite(
                    fitted, ((size - fitted.width) // 2, (size - fitted.height) // 2)
                )
                suffix = "@2x" if density == 2 else ""
                canvas.save(iconset / f"icon_{points}x{points}{suffix}.png")
        subprocess.run(
            ["/usr/bin/iconutil", "-c", "icns", str(iconset),
             "-o", str(resources / "AppIcon.icns")], check=True
        )

    (contents / "Info.plist").write_bytes(plistlib.dumps({
        "CFBundleName": "Gods of the Arena",
        "CFBundleDisplayName": "Gods of the Arena",
        "CFBundleIdentifier": identifier,
        "CFBundleExecutable": "launch",
        "CFBundleIconFile": "AppIcon.icns",
        "CFBundlePackageType": "APPL",
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleShortVersionString": "0.1.0",
        "CFBundleVersion": "1",
        "LSMinimumSystemVersion": "11.0",
        "NSHighResolutionCapable": True,
    }))
    (contents / "PkgInfo").write_bytes(b"APPL????")
    executable = macos / "Gods of the Arena"
    staged = executable.with_suffix(".new")
    shutil.copy2(binary, staged)
    staged.replace(executable)
    launcher = macos / "launch"
    launcher.write_text(f'''#!/bin/sh
set -eu
cd {shlex.quote(str(root))}
bundle_bin="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/Gods of the Arena"
source_bin={shlex.quote(str(binary))}
if [ "$source_bin" -nt "$bundle_bin" ]; then
    staged="$bundle_bin.new.$$"
    trap 'rm -f "$staged"' EXIT
    /bin/cp -p "$source_bin" "$staged"
    /bin/mv -f "$staged" "$bundle_bin"
    trap - EXIT
fi
exec "$bundle_bin" "$@"
''')
    launcher.chmod(0o755)
    subprocess.run(["/usr/bin/plutil", "-lint", str(contents / "Info.plist")], check=True)
    registration = Path(
        "/System/Library/Frameworks/CoreServices.framework/Frameworks/"
        "LaunchServices.framework/Support/lsregister"
    )
    subprocess.run([str(registration), "-f", str(app)], check=True)
    print(f"Installed {app}")


if __name__ == "__main__":
    install()
