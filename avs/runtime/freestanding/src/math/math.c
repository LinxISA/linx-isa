/* Minimal freestanding libm services used by AVS and direct-boot workloads. */

#include <linxisa_libc.h>
#include <math.h>

static inline u64 linx_f64_bits(double x)
{
    union {
        double f;
        u64 u;
    } v;
    v.f = x;
    return v.u;
}

static inline double linx_f64_from_bits(u64 x)
{
    union {
        double f;
        u64 u;
    } v;
    v.u = x;
    return v.f;
}

static inline u32 linx_f32_bits(float x)
{
    union {
        float f;
        u32 u;
    } v;
    v.f = x;
    return v.u;
}

static inline float linx_f32_from_bits(u32 x)
{
    union {
        float f;
        u32 u;
    } v;
    v.u = x;
    return v.f;
}

double fabs(double x)
{
    return linx_f64_from_bits(linx_f64_bits(x) & ~(1ULL << 63));
}

float fabsf(float x)
{
    return linx_f32_from_bits(linx_f32_bits(x) & ~(1U << 31));
}

double sqrt(double x)
{
    if (x <= 0.0) {
        return x == 0.0 ? 0.0 : linx_f64_from_bits(0x7ff8000000000000ULL);
    }

    /* Newton-Raphson with a crude initial guess. */
    double g = x;
    for (int i = 0; i < 16; i++) {
        g = 0.5 * (g + x / g);
    }
    return g;
}

float sqrtf(float x)
{
    return (float)sqrt((double)x);
}

static double linx_trig_reduce(double x)
{
    const double two_pi_hi = 6.28318530717958623200;
    const double two_pi_lo = 2.44929359829470641435e-16;
    const double inv_two_pi = 0.15915494309189533577;
    const u64 bits = linx_f64_bits(x);
    const u64 exponent = (bits >> 52) & 0x7ff;

    if (exponent == 0x7ff) {
        return linx_f64_from_bits(0x7ff8000000000000ULL);
    }

    /*
     * Direct-boot workloads stay well inside this exact-integer reduction
     * range. Keeping the bound explicit avoids an overflowing conversion for
     * enormous finite inputs while still providing real periodic semantics.
     */
    if (fabs(x) > 0x1p52) {
        return linx_f64_from_bits(0x7ff8000000000000ULL);
    }

    const double turns = x * inv_two_pi;
    const long long nearest = (long long)(turns + (turns < 0.0 ? -0.5 : 0.5));
    return (x - (double)nearest * two_pi_hi) - (double)nearest * two_pi_lo;
}

double sin(double x)
{
    const double pi = 3.14159265358979323846;
    const double half_pi = 1.57079632679489661923;
    double y = linx_trig_reduce(x);
    if (linx_f64_bits(y) == 0x7ff8000000000000ULL) {
        return y;
    }
    if (y > half_pi) {
        y = pi - y;
    } else if (y < -half_pi) {
        y = -pi - y;
    }

    const double y2 = y * y;
    return y * (1.0 + y2 * (-1.0 / 6.0 + y2 * (1.0 / 120.0 +
           y2 * (-1.0 / 5040.0 + y2 * (1.0 / 362880.0 +
           y2 * (-1.0 / 39916800.0 + y2 * (1.0 / 6227020800.0)))))));
}

double cos(double x)
{
    const double pi = 3.14159265358979323846;
    const double half_pi = 1.57079632679489661923;
    double y = linx_trig_reduce(x);
    double sign = 1.0;
    if (linx_f64_bits(y) == 0x7ff8000000000000ULL) {
        return y;
    }
    if (y > half_pi) {
        y = pi - y;
        sign = -1.0;
    } else if (y < -half_pi) {
        y = -pi - y;
        sign = -1.0;
    }

    const double y2 = y * y;
    return sign * (1.0 + y2 * (-1.0 / 2.0 + y2 * (1.0 / 24.0 +
           y2 * (-1.0 / 720.0 + y2 * (1.0 / 40320.0 +
           y2 * (-1.0 / 3628800.0 + y2 * (1.0 / 479001600.0)))))));
}

float cosf(float x)
{
    return (float)cos((double)x);
}

float sinf(float x)
{
    return (float)sin((double)x);
}

double acos(double x)
{
    const double pi = 3.14159265358979323846;
    const double half_pi = 1.57079632679489661923;

    if (x < -1.0 || x > 1.0) {
        return linx_f64_from_bits(0x7ff8000000000000ULL);
    }
    if (x == 1.0) {
        return 0.0;
    }
    if (x == -1.0) {
        return pi;
    }
    if (x == 0.0) {
        return half_pi;
    }

    const double ratio = sqrt((1.0 - x) * (1.0 + x)) / fabs(x);
    return x > 0.0 ? atan(ratio) : pi - atan(ratio);
}

double atan(double x)
{
    const double pi_over_2 = 1.57079632679489661923;
    const double pi_over_4 = 0.78539816339744830962;
    const double tan_pi_over_8 = 0.41421356237309504880;
    const u64 bits = linx_f64_bits(x);
    const u64 exponent = (bits >> 52) & 0x7ff;

    if (exponent == 0x7ff) {
        if (bits & 0x000fffffffffffffULL) {
            return x;
        }
        return bits >> 63 ? -pi_over_2 : pi_over_2;
    }

    const int negative = x < 0.0;
    double y = fabs(x);
    double offset = 0.0;
    int reciprocal = 0;
    if (y > 1.0) {
        y = 1.0 / y;
        offset = pi_over_2;
        reciprocal = 1;
    }
    if (y > tan_pi_over_8) {
        y = (y - 1.0) / (y + 1.0);
        offset = reciprocal ? pi_over_4 : pi_over_4;
        reciprocal = 0;
    }

    const double y2 = y * y;
    double term = y;
    double sum = y;
    for (int denominator = 3, subtract = 1; denominator <= 25;
         denominator += 2, subtract = !subtract) {
        term *= y2;
        sum += (subtract ? -term : term) / (double)denominator;
    }
    double result = reciprocal ? offset - sum : offset + sum;
    return negative ? -result : result;
}

double pow(double x, double y)
{
    if (y == 0.0) {
        return 1.0;
    }
    if (x == 0.0) {
        return y > 0.0 ? 0.0 : linx_f64_from_bits(0x7ff0000000000000ULL);
    }
    if (x > 0.0) {
        return exp(y * log(x));
    }

    if (fabs(y) > 0x1p52) {
        return linx_f64_from_bits(0x7ff8000000000000ULL);
    }
    const long long integral_y = (long long)y;
    if ((double)integral_y != y) {
        return linx_f64_from_bits(0x7ff8000000000000ULL);
    }
    const double magnitude = exp(y * log(-x));
    return (integral_y & 1LL) ? -magnitude : magnitude;
}

static inline double linx_f64_pos_inf(void)
{
    return linx_f64_from_bits(0x7ff0000000000000ULL);
}

static inline double linx_f64_neg_inf(void)
{
    return linx_f64_from_bits(0xfff0000000000000ULL);
}

static inline double linx_f64_qnan(void)
{
    return linx_f64_from_bits(0x7ff8000000000000ULL);
}

static inline int linx_f64_is_nan(u64 bits)
{
    return (((bits >> 52) & 0x7ff) == 0x7ff) && ((bits & 0x000fffffffffffffULL) != 0);
}

static inline int linx_f64_is_inf(u64 bits)
{
    return (((bits >> 52) & 0x7ff) == 0x7ff) && ((bits & 0x000fffffffffffffULL) == 0);
}

static double linx_pow2_int(int e)
{
    if (e > 1023) {
        return linx_f64_pos_inf();
    }
    if (e < -1074) {
        return 0.0;
    }
    if (e < -1022) {
        const int shift = e + 1074; /* 0..51 */
        return linx_f64_from_bits((u64)1ULL << (u64)shift);
    }
    return linx_f64_from_bits((u64)(e + 1023) << 52);
}

double exp(double x)
{
    const u64 bits = linx_f64_bits(x);
    if (linx_f64_is_nan(bits)) {
        return x;
    }
    if (linx_f64_is_inf(bits)) {
        if (bits >> 63) {
            return 0.0;
        }
        return linx_f64_pos_inf();
    }

    /* Clamp to avoid overflow/underflow. */
    if (x > 709.782712893384) {
        return linx_f64_pos_inf();
    }
    if (x < -745.1332191019411) {
        return 0.0;
    }

    /* Range-reduce using x = n*ln2 + r, r in ~[-ln2/2, ln2/2]. */
    const double ln2 = 0.6931471805599453;
    const double invln2 = 1.4426950408889634;

    int n = (int)(x * invln2 + (x >= 0.0 ? 0.5 : -0.5));
    double r = x - (double)n * ln2;

    /* exp(r) via a short Taylor series around 0. */
    double term = 1.0;
    double sum = 1.0;
    for (int i = 1; i <= 12; i++) {
        term *= r / (double)i;
        sum += term;
    }

    return sum * linx_pow2_int(n);
}

float expf(float x)
{
    return (float)exp((double)x);
}

double log(double x)
{
    const u64 bits = linx_f64_bits(x);
    if (linx_f64_is_nan(bits)) {
        return x;
    }
    if (linx_f64_is_inf(bits)) {
        if (bits >> 63) {
            return linx_f64_qnan();
        }
        return linx_f64_pos_inf();
    }
    if (x == 0.0) {
        return linx_f64_neg_inf();
    }
    if (x < 0.0) {
        return linx_f64_qnan();
    }

    /* Decompose x = m * 2^e with m in [1,2). */
    u64 exp_bits = (bits >> 52) & 0x7ff;
    u64 mant = bits & 0x000fffffffffffffULL;
    int e = 0;
    if (exp_bits == 0) {
        /* Subnormal: treat as underflow for bring-up. */
        return linx_f64_neg_inf();
    } else {
        e = (int)exp_bits - 1023;
    }

    const double m = 1.0 + (double)mant / (double)(1ULL << 52);

    /* log(m) using atanh-series: log(m) = 2*(y + y^3/3 + y^5/5 + ...)
     * where y = (m-1)/(m+1), and for m in [1,2), y in [0, 1/3]. */
    const double y = (m - 1.0) / (m + 1.0);
    const double y2 = y * y;
    double term = y;
    double acc = term;
    for (int k = 3; k <= 11; k += 2) {
        term *= y2;
        acc += term / (double)k;
    }
    const double ln_m = 2.0 * acc;

    const double ln2 = 0.6931471805599453;
    return ln_m + (double)e * ln2;
}

float logf(float x)
{
    return (float)log((double)x);
}
