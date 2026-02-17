# Linux Trap Triage

Generated: `2026-02-16 19:15:26 UTC`

## Inputs

- vmlinux: `/Users/zhoubot/linux/build-linx-fixed/vmlinux`
- logs scanned: `1`
- trap entries parsed: `2`
- log: `/Users/zhoubot/linx-isa/out/bringup/gates/logs/external_linux_smoke.log`

## Trap PCs

### `0x6`

- observations: `1`
- function (addr2line): `??`
- file/line: `??:0`
- nearest non-local symbol: `? <unknown>` (delta `0x-1`)
- latest trap fields: trapnum=`0x5` cause=`0x1` traparg0=`0x8` async=`0x0`

### `0x2cf6e0`

- observations: `1`
- function (addr2line): `.LBB22_2`
- file/line: `string.c:0`
- nearest non-local symbol: `T memset` (delta `0x10`)
- latest trap fields: trapnum=`0x2c` cause=`0x0` traparg0=`0x0` async=`0x1`

## Revisions

- external linux: `4011f8a20` (`/Users/zhoubot/linux`)
- external qemu: `5294f2d01e` (`/Users/zhoubot/qemu`)
- pinned linux submodule: `37a93dd5c49b` (`/Users/zhoubot/linx-isa/kernel/linux`)
- pinned qemu submodule: `8d0c4e0d34` (`/Users/zhoubot/linx-isa/emulator/qemu`)

## Suggested Next Commands

```bash
/Users/zhoubot/llvm-project/build-linxisa-clang/bin/llvm-addr2line -e /Users/zhoubot/linux/build-linx-fixed/vmlinux -f -C 0x6
/Users/zhoubot/llvm-project/build-linxisa-clang/bin/llvm-addr2line -e /Users/zhoubot/linux/build-linx-fixed/vmlinux -f -C 0x2cf6e0
/Users/zhoubot/llvm-project/build-linxisa-clang/bin/llvm-nm -n /Users/zhoubot/linux/build-linx-fixed/vmlinux | rg -n '__switch_to|linx_ret_from_fork|linx_enter_user'
cd /Users/zhoubot/linux && git bisect start && git bisect bad 4011f8a20 && git bisect good 37a93dd5c49b
cd /Users/zhoubot/qemu && git bisect start && git bisect bad 5294f2d01e && git bisect good 8d0c4e0d34
```
