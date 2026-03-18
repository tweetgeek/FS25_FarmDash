"""Generates a PyInstaller Windows version info file from a version string."""
import re
import sys


def parse_version(version_str: str) -> tuple:
    parts = re.findall(r'\d+', version_str)
    while len(parts) < 4:
        parts.append('0')
    return tuple(int(x) for x in parts[:4])


def generate(version_str: str) -> str:
    v = parse_version(version_str)
    return f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={v},
    prodvers={v},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'TweetGeek'),
         StringStruct(u'FileDescription', u'FarmDash \u2014 FS25 Live Dashboard'),
         StringStruct(u'FileVersion', u'{version_str}'),
         StringStruct(u'InternalName', u'FarmDash'),
         StringStruct(u'LegalCopyright', u'\u00a9 TweetGeek'),
         StringStruct(u'OriginalFilename', u'FarmDash-{version_str}.exe'),
         StringStruct(u'ProductName', u'FarmDash'),
         StringStruct(u'ProductVersion', u'{version_str}')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""


if __name__ == '__main__':
    version = sys.argv[1] if len(sys.argv) > 1 else '0.0.0'
    content = generate(version)
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'version_info.txt generated for version {version}')
