"""Build croods_offline.apk from the original The Croods 1.3.1 APK.

- Points the Rovio cloud URLs at the fake server on the emulator host (10.0.2.2:8000).
- x86 only: makes the "Lua error! Crashing app..." log line print the actual Lua error,
  and lets the game keep running after it instead of aborting.
- Drops the old signature; sign the result with apksigner afterwards.
"""
import sys
import zipfile

NEW_URL = b'http://10.0.2.2:8000'

# GameLua::update catch block (x86): before building the log call, store
# Throwable::what() (char* at exception+0xac) as the first vararg at [esp+0x18].
X86_CATCH_OFF = 0x17da85
X86_CATCH_OLD = bytes.fromhex(
    '8b8338daffff 8db424ac000000 83c00c c744241001000000 898424ac000000'
    ' c744240c37030000 8d8394ede6ff 893424 89442414'.replace(' ', ''))
X86_CATCH_NEW = bytes.fromhex(
    '8b88ac000000'      # mov ecx,[eax+0xac]      ; exception->what()
    '894c2418'          # mov [esp+0x18],ecx      ; vararg for %s
    '8b8338daffff'      # mov eax,[ebx-0x25c8]
    '8db424ac000000'    # lea esi,[esp+0xac]
    '83c00c'            # add eax,0xc
    'c744241001000000'  # mov dword [esp+0x10],1
    '8906'              # mov [esi],eax
    '8d8394ede6ff'      # lea eax,[ebx-0x19126c]  ; format string
    '893424'            # mov [esp],esi
    '89442414'          # mov [esp+0x14],eax
    '909090')           # pad (line-number store dropped)
X86_FMT_OLD = b'Lua error! Crashing app...\x00'
X86_FMT_NEW = b'LUAERR: %s\x00'

# Crash guard (x86). After logging, the same catch block called std::terminate(), so any Lua
# error killed the app. Instead: end the catch and leave GameLua::update through its normal
# epilogue (stack-canary check at 0x17d247) - the error is logged and the next frame runs as
# usual. The bytes come from the call to ~string() on the empty log-tag string, which is a
# no-op for the shared empty representation, so dropping it is safe.
X86_TERM_OFF = 0x17dad2
X86_TERM_OLD = bytes.fromhex(
    '893424'            # mov [esp],esi
    'e876853e00'        # call ~string            ; 0x566050
    'e8511d4000')       # call std::terminate     ; 0x57f830
X86_TERM_NEW = bytes.fromhex(
    'e8c90d4000'        # call __cxa_end_catch    ; 0x57e8a0
    'e96bf7ffff'        # jmp 0x17d247            ; canary check, pop, ret
    '909090')
# The inner catch (around the call into Lua) sets GameLua+0x134 before rethrowing; while it is
# set update() skips Lua and only draws a debug error screen. Keep it cleared so play goes on.
X86_FLAG_OFF = 0x17db5c
X86_FLAG_OLD = bytes.fromhex('c6823401000001')  # mov byte [edx+0x134],1
X86_FLAG_NEW = bytes.fromhex('c6823401000000')  # mov byte [edx+0x134],0


def patch_lib(name, data):
    for old in (b'https://cloud.rovio.com\x00', b'http://cloud.rovio.com\x00'):
        assert old in data, (name, old)
        data = data.replace(old, NEW_URL + b'\x00' * (len(old) - len(NEW_URL)))
    if '/x86/' in name:
        assert len(X86_CATCH_NEW) == len(X86_CATCH_OLD)
        assert data[X86_CATCH_OFF:X86_CATCH_OFF + len(X86_CATCH_OLD)] == X86_CATCH_OLD
        data = data[:X86_CATCH_OFF] + X86_CATCH_NEW + data[X86_CATCH_OFF + len(X86_CATCH_NEW):]
        for off, old, new in ((X86_TERM_OFF, X86_TERM_OLD, X86_TERM_NEW), (X86_FLAG_OFF, X86_FLAG_OLD, X86_FLAG_NEW)):
            assert len(old) == len(new) and data[off:off + len(old)] == old, (name, hex(off))
            data = data[:off] + new + data[off + len(new):]
        i = data.index(X86_FMT_OLD)
        data = data[:i] + X86_FMT_NEW.ljust(len(X86_FMT_OLD), b'\x00') + data[i + len(X86_FMT_OLD):]
    return data


def main(src, dst):
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(dst, 'w')
    for it in zin.infolist():
        if it.filename.startswith('META-INF/'):
            continue
        data = zin.read(it.filename)
        if it.filename.endswith('libCroods.so'):
            data = patch_lib(it.filename, data)
            print('patched', it.filename)
        zout.writestr(it, data, compress_type=it.compress_type)
    zout.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
