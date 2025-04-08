// Intentionally inefficient...
// Something to give us >100ms compile times
static constexpr int pow(int x, int y, int mod) {
    int ans = 1;
    for (int i = 0; i < y; ++i) ans = (ans * x) % mod;
    return ans;
}
