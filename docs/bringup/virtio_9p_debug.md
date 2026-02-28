# virtio-9p bring-up status (Linx virt)

## Summary

We are bringing up host→guest file sharing for the Linx Linux bring-up using **virtio-9p over virtio-mmio**.

Current status:

- virtio-mmio transport(s): **working** (guest enumerates virtio devices)
- virtio-blk on virtio-mmio: **working** (guest sees `vda`)
- virtio-9p mount: **failing** with `EPROTO (-71)` when running `mount -t 9p render-share /opt/share ...`

## Minimal reproduction

### QEMU

Use Linx virt DT-provided transports (do **not** add `virtio_mmio.device=...` when DT already declares virtio-mmio nodes).

Example:

```bash
QEMU=~/linx-isa/emulator/qemu/build/qemu-system-linx64
KERNEL=~/linx-isa/kernel/linux/build-linx-render/vmlinux
INITRD=~/linx-isa/kernel/linux/build-linx-fixed/linx-initramfs/initramfs.cpio
SHARE=~/linx-isa/out/render-share

$QEMU \
  -machine virt -m 1024M -smp 1 \
  -kernel "$KERNEL" -initrd "$INITRD" \
  -append "console=ttyS0 lpj=1000000 loglevel=7" \
  -nographic -monitor none \
  -fsdev local,id=fsdev0,path="$SHARE",security_model=none,multidevs=remap \
  -device virtio-9p-device,fsdev=fsdev0,mount_tag=render-share
```

### Guest

In initramfs, run `m9p` (debug applet) to attempt the mount and print the raw return code:

- expected today: `9p_mount=ffffffffffffffb9`  (== -71, EPROTO)

## Known pitfalls / notes

- If you pass `virtio_mmio.device=0x200@0x30001000:1` while the DT already contains virtio-mmio nodes, Linux may attempt to register a *second* virtio-mmio transport and hit probe conflicts (e.g. `-16`).
- Endianness assumption: **little-endian** for virtio and 9p protocol fields.

## Related PRs

- QEMU: multi, modern virtio-mmio transports for linx virt (infrastructure for virtio bring-up)
  - https://github.com/LinxISA/qemu/pull/19
- Linux: initramfs `m9p` applet and `/opt/share` dirs for in-guest reproduction
  - https://github.com/LinxISA/linux/pull/15

## Next debug steps

- Add minimal QEMU-side logging for the first 9p exchange (Tversion/Rversion) to determine if the failure is:
  - feature negotiation mismatch
  - virtqueue descriptor parsing issue
  - payload endian/length decoding issue
