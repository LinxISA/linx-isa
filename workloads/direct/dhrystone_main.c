/* Give the K&R Dhrystone main a deterministic direct-boot return value. */
void dhry_main(void);

int main(void)
{
    dhry_main();
    return 0;
}
