/* E-55 copy-kernel census (scripts/bff_kernels.py). Same interpreter as emergence/programs/bff.c, except
   that head1 starts at `h1start` (0 = the standard rule; L = counterfactual). Kept separate on purpose so the
   soup interpreter is untouched. */
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

static long run(uint8_t *t, int n, long max_steps, int h1start) {
    int ip = 0, h0 = 0, h1 = h1start % n;
    long steps = 0;
    while (ip >= 0 && ip < n && steps < max_steps) {
        switch (t[ip]) {
        case '<': h0 = (h0 + n - 1) % n; break;
        case '>': h0 = (h0 + 1) % n; break;
        case '{': h1 = (h1 + n - 1) % n; break;
        case '}': h1 = (h1 + 1) % n; break;
        case '-': t[h0]--; break;
        case '+': t[h0]++; break;
        case '.': t[h1] = t[h0]; break;
        case ',': t[h0] = t[h1]; break;
        case '[':
            if (t[h0] == 0) {
                int d = 1, j = ip + 1;
                for (; j < n; j++) {
                    if (t[j] == '[') d++;
                    else if (t[j] == ']' && --d == 0) break;
                }
                if (j >= n) return steps + 1;
                ip = j;
            }
            break;
        case ']':
            if (t[h0] != 0) {
                int d = 1, j = ip - 1;
                for (; j >= 0; j--) {
                    if (t[j] == ']') d++;
                    else if (t[j] == '[' && --d == 0) break;
                }
                if (j < 0) return steps + 1;
                ip = j;
            }
            break;
        default: break;
        }
        ip++;
        steps++;
    }
    return steps;
}

static uint64_t sm(uint64_t *s) {
    uint64_t z = (*s += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}

/* out[i]: bit0 = forward copy with every partner, bit1 = reverse copy with every partner
   (partner half matches the program, or its reverse, in >= thr bytes AND program half intact >= thr). */
void classify(const uint8_t *progs, int nprog, int L, int h1start, int partners, uint64_t seed,
              long max_steps, int thr, uint8_t *out) {
    uint8_t tape[1024];
    for (int i = 0; i < nprog; i++) {
        const uint8_t *p = progs + (long)i * L;
        uint64_t s = seed ^ (0xD1B54A32D192ED03ull * (uint64_t)(i + 1));
        int fwd = 1, rev = 1;
        for (int q = 0; q < partners && (fwd || rev); q++) {
            memcpy(tape, p, L);
            for (int j = 0; j < L; j++) tape[L + j] = (uint8_t)sm(&s);
            run(tape, 2 * L, max_steps, h1start);
            int intact = 0, f = 0, r = 0;
            for (int j = 0; j < L; j++) {
                intact += tape[j] == p[j];
                f += tape[L + j] == p[j];
                r += tape[L + j] == p[L - 1 - j];
            }
            if (intact < thr) { fwd = rev = 0; break; }
            if (f < thr) fwd = 0;
            if (r < thr) rev = 0;
        }
        out[i] = (uint8_t)(fwd | (rev << 1));
    }
}

/* One soup epoch with head1 starting at h1start (E-56 counterfactual soups); otherwise identical to
   bff_epoch in emergence/programs/bff.c, mode 0. */
long epoch_h(uint8_t *soup, int L, const int32_t *pairs, int npairs, long max_steps, int h1start) {
    uint8_t tape[1024];
    long total = 0;
    if (2 * L > 1024) return -1;
    for (int p = 0; p < npairs; p++) {
        uint8_t *a = soup + (long)pairs[2 * p] * L, *b = soup + (long)pairs[2 * p + 1] * L;
        for (int i = 0; i < L; i++) { tape[i] = a[i]; tape[L + i] = b[i]; }
        total += run(tape, 2 * L, max_steps, h1start);
        for (int i = 0; i < L; i++) { a[i] = tape[i]; b[i] = tape[L + i]; }
    }
    return total;
}

/* E-57: run one tape in place (exposes run() for product extraction). */
long run_tape(uint8_t *t, int n, long max_steps, int h1start) { return run(t, n, max_steps, h1start); }

/* E-61: shift-aware copy classifier. Like classify(), but the partner half may hold the program (or its
   reverse) shifted by d bytes, |d| <= maxshift: agreement is counted on the overlap (L - |d| bytes) and must be
   >= overlap - (L - thr). The same d must work with every partner. out[i] = orientation bits as classify();
   shift[i] = d of the forward copy if any, else of the reverse copy (0 if none). Program half intact >= thr. */
void classify_shift(const uint8_t *progs, int nprog, int L, int h1start, int partners, uint64_t seed,
                    long max_steps, int thr, int maxshift, uint8_t *out, int8_t *shift) {
    uint8_t tape[1024];
    int slack = L - thr, nd = 2 * maxshift + 1;
    uint8_t okf[129], okr[129];
    for (int i = 0; i < nprog; i++) {
        const uint8_t *p = progs + (long)i * L;
        uint64_t s = seed ^ (0xD1B54A32D192ED03ull * (uint64_t)(i + 1));
        for (int k = 0; k < nd; k++) okf[k] = okr[k] = 1;
        int alive = 1;
        for (int q = 0; q < partners && alive; q++) {
            memcpy(tape, p, L);
            for (int j = 0; j < L; j++) tape[L + j] = (uint8_t)sm(&s);
            run(tape, 2 * L, max_steps, h1start);
            int intact = 0;
            for (int j = 0; j < L; j++) intact += tape[j] == p[j];
            if (intact < thr) { alive = 0; break; }
            alive = 0;
            for (int k = 0; k < nd; k++) {
                int d = k - maxshift, ov = L - (d < 0 ? -d : d), f = 0, r = 0;
                for (int j = 0; j < L; j++) {
                    int src = j - d;           /* partner[j] should equal program[j - d] */
                    if (src < 0 || src >= L) continue;
                    f += tape[L + j] == p[src];
                    r += tape[L + j] == p[L - 1 - src];
                }
                if (f < ov - slack) okf[k] = 0;
                if (r < ov - slack) okr[k] = 0;
                alive |= okf[k] | okr[k];
            }
        }
        int fw = -999, rv = -999;
        if (alive)
            for (int k = 0; k < nd; k++) {   /* smallest |d| wins */
                int d = k - maxshift;
                if (okf[k] && (fw == -999 || abs(d) < abs(fw))) fw = d;
                if (okr[k] && (rv == -999 || abs(d) < abs(rv))) rv = d;
            }
        out[i] = (uint8_t)((fw != -999) | ((rv != -999) << 1));
        shift[i] = (int8_t)(fw != -999 ? fw : (rv != -999 ? rv : 0));
    }
}
