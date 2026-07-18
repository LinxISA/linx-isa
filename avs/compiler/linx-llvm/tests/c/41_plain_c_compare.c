int plain_eq_zero(int value) { return value == 0; }

int plain_ne_zero(int value) { return value != 0; }

int plain_unsigned_ge_seven(unsigned value) { return value >= 7; }

unsigned plain_zero_extend_half(unsigned value) {
  return (unsigned short)value;
}

int plain_and_nonzero(unsigned left, unsigned right) {
  return (left & right) != 0;
}

int plain_and_mask_nonzero(unsigned value) {
  return (value & 0x55u) != 0;
}

int plain_or_nonzero(unsigned left, unsigned right) {
  return (left | right) != 0;
}

int plain_float_equal(float left, float right) { return left == right; }
