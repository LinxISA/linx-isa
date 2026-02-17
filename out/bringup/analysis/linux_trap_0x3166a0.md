# Linux Trap Triage

Generated: `2026-02-16 18:27:10 UTC`

## Trap

- PC: `0x3166a0`
- Function (addr2line): `.LBB15_10`
- File/line: `vsprintf.c:0`
- Nearest non-local symbol: `T vsnprintf` (delta `0x124`)

## Revisions

- external linux: `4011f8a20` (`/Users/zhoubot/linux`)
- external qemu: `5294f2d01e` (`/Users/zhoubot/qemu`)
- pinned linux submodule: `37a93dd5c49b` (`/Users/zhoubot/linx-isa/kernel/linux`)
- pinned qemu submodule: `8d0c4e0d34` (`/Users/zhoubot/linx-isa/emulator/qemu`)

## Suggested Next Commands

```bash
/Users/zhoubot/llvm-project/build-linxisa-clang/bin/llvm-addr2line -e /Users/zhoubot/linux/build-linx-fixed/vmlinux -f -C 0x3166a0
/Users/zhoubot/llvm-project/build-linxisa-clang/bin/llvm-nm -n /Users/zhoubot/linux/build-linx-fixed/vmlinux | rg 3166a0
cd /Users/zhoubot/linux && git bisect start && git bisect bad 4011f8a20 && git bisect good 37a93dd5c49b
cd /Users/zhoubot/qemu && git bisect start && git bisect bad 5294f2d01e && git bisect good 8d0c4e0d34
```
