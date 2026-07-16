long subi_i64_1(long x) { return x - 1L; }
long subi_i64_4095(long x) { return x - 4095L; }
long hl_subi_i64_4096(long x) { return x - 4096L; }
long hl_subi_i64_ffffff(long x) { return x - 0xffffffL; }
long fallback_i64_1000000(long x) { return x - 0x1000000L; }
long zero_i64(long x) { return x - 0L; }

int subiw_i32_1(int x) { return x - 1; }
int subiw_i32_4095(int x) { return x - 4095; }
int hl_subiw_i32_4096(int x) { return x - 4096; }
int hl_subiw_i32_ffffff(int x) { return x - 0xffffff; }
int fallback_i32_1000000(int x) { return x - 0x1000000; }
int zero_i32(int x) { return x - 0; }
