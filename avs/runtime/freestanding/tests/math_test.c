#include <math.h>

static int close_enough(double actual, double expected, double tolerance)
{
    return fabs(actual - expected) <= tolerance;
}

int main(void)
{
    const double pi = 3.14159265358979323846;
    const double half_pi = 1.57079632679489661923;

    if (!close_enough(sin(0.0), 0.0, 1e-12) ||
        !close_enough(sin(half_pi), 1.0, 1e-9) ||
        !close_enough(sin(-half_pi), -1.0, 1e-9) ||
        !close_enough(sin(pi), 0.0, 1e-9)) {
        return 1;
    }
    if (!close_enough(cos(0.0), 1.0, 1e-12) ||
        !close_enough(cos(half_pi), 0.0, 1e-8) ||
        !close_enough(cos(pi), -1.0, 1e-8)) {
        return 2;
    }
    if (!close_enough(sinf(0.5f), 0.47942555f, 1e-6) ||
        !close_enough(cosf(0.5f), 0.87758256f, 1e-6)) {
        return 3;
    }
    if (!close_enough(atan(1.0), pi / 4.0, 1e-9) ||
        !close_enough(atan(-1.0), -pi / 4.0, 1e-9) ||
        !close_enough(acos(0.0), half_pi, 1e-9) ||
        !close_enough(acos(-1.0), pi, 1e-9)) {
        return 4;
    }
    if (!close_enough(pow(2.0, 10.0), 1024.0, 1e-7) ||
        !close_enough(pow(-2.0, 3.0), -8.0, 1e-9) ||
        !close_enough(pow(4.0, -0.5), 0.5, 1e-7)) {
        return 5;
    }
    return 0;
}
