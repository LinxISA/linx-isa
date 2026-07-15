signed char plain_load_signed_byte_and_advance(signed char **cursor) {
  signed char *pointer = *cursor;
  signed char value = *pointer;
  *cursor = pointer + 1;
  return value;
}

unsigned char plain_load_unsigned_byte_and_advance(unsigned char **cursor) {
  unsigned char *pointer = *cursor;
  unsigned char value = *pointer;
  *cursor = pointer + 1;
  return value;
}

short plain_load_signed_half_and_advance(short **cursor) {
  short *pointer = *cursor;
  short value = *pointer;
  *cursor = pointer + 1;
  return value;
}

unsigned short plain_load_unsigned_half_and_advance(unsigned short **cursor) {
  unsigned short *pointer = *cursor;
  unsigned short value = *pointer;
  *cursor = pointer + 1;
  return value;
}

unsigned long plain_load_unsigned_word_and_advance(unsigned **cursor) {
  unsigned *pointer = *cursor;
  unsigned value = *pointer;
  *cursor = pointer + 1;
  return value;
}

long plain_load_doubleword_and_advance(long **cursor) {
  long *pointer = *cursor;
  long value = *pointer;
  *cursor = pointer + 1;
  return value;
}

void plain_store_signed_byte_and_advance(signed char **cursor,
                                         signed char value) {
  signed char *pointer = *cursor;
  *pointer = value;
  *cursor = pointer + 1;
}

void plain_store_signed_half_and_advance(short **cursor, short value) {
  short *pointer = *cursor;
  *pointer = value;
  *cursor = pointer + 1;
}

void plain_store_doubleword_and_advance(long **cursor, long value) {
  long *pointer = *cursor;
  *pointer = value;
  *cursor = pointer + 1;
}

unsigned plain_external_unsigned_word;

unsigned long plain_load_external_unsigned_word(void) {
  return plain_external_unsigned_word;
}

int plain_accumulate_not_equal_one(int accumulator, int value) {
  return accumulator + (value != 1);
}
