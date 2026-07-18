signed char plain_external_signed_byte;
unsigned char plain_external_unsigned_byte;
short plain_external_signed_half;
unsigned short plain_external_unsigned_half;
int plain_external_word;

signed char plain_load_external_signed_byte(void) {
  return plain_external_signed_byte;
}

unsigned char plain_load_external_unsigned_byte(void) {
  return plain_external_unsigned_byte;
}

short plain_load_external_signed_half(void) {
  return plain_external_signed_half;
}

unsigned short plain_load_external_unsigned_half(void) {
  return plain_external_unsigned_half;
}

int plain_load_external_word(void) { return plain_external_word; }

void plain_store_external_signed_byte(signed char value) {
  plain_external_signed_byte = value;
}

void plain_store_external_signed_half(short value) {
  plain_external_signed_half = value;
}

void plain_store_external_word(int value) { plain_external_word = value; }

int plain_load_and_advance(int **cursor) {
  int *pointer = *cursor;
  int value = *pointer;
  *cursor = pointer + 1;
  return value;
}

void plain_store_and_advance(int **cursor, int value) {
  int *pointer = *cursor;
  *pointer = value;
  *cursor = pointer + 1;
}
