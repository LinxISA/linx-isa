/*
 * Semantic-only Dhrystone timer. The one-tick interval deliberately keeps
 * performance reporting invalid while preserving deterministic completion.
 */
long time(long *result)
{
    static long ticks;
    long now = ticks++;
    if (result != 0) {
        *result = now;
    }
    return now;
}
