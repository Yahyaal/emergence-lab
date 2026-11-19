/* E-85 (D-078): BFF-X with a minimum body for running one's own code ("BFF-XM"), used by scripts/bffxm.py.

   Everything is scripts/bffx.c (E-82, D-072), copied here so that E-82 to E-84 keep their own compiled library.
   The one change: a program shorter than `xmin` bytes has no code of its own. When it runs first (as A), the
   instruction pointer starts in the second code segment (the borrowed library C under libmode 2, B under libmode
   0 and 1, nothing under libmode 3) instead of at A's first byte; the heads start where they always do (head0 at
   A's first byte, head1 at B's first byte) and the data tape is A ++ B as before. A program of xmin bytes or more
   runs exactly as in BFF-X. With xmin = 0 (or xmin <= LMIN) every function here is bit-identical to bffx.c.

   So a self-copier needs at least xmin bytes, while a program that only borrows code may be as short as LMIN: the
   shortest host is long, a partner check costs a few of its bytes, and parasites still win by being short. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define TAPE_MAX 1024

static int xmin = 0;

void x_set_xmin(int v) { xmin = v; }
int x_get_xmin(void) { return xmin; }

static inline uint8_t fetch(const uint8_t *t, int la, const uint8_t *lib, int i) {
    return i < la ? t[i] : lib[i - la];
}

/* data t[0..nd), code = t[0..ca) ++ lib[0..ll) (lib == t + la for libmode 0); head1 starts at la (B's first byte).
   ca = la, except ca = 0 for a program shorter than xmin (no code of its own). */
static long runx(uint8_t *t, int nd, int la_data, const uint8_t *lib, int ll, long max_steps) {
    int la = la_data < xmin ? 0 : la_data;
    int nc = la + ll, ip = 0, h0 = 0, h1 = la_data;
    long steps = 0;
    if (h1 >= nd) h1 = nd - 1;
    while (ip >= 0 && ip < nc && steps < max_steps) {
        switch (fetch(t, la, lib, ip)) {
        case '<': if (h0 == 0) return steps + 1; h0--; break;
        case '>': if (h0 == nd - 1) return steps + 1; h0++; break;
        case '{': if (h1 == 0) return steps + 1; h1--; break;
        case '}': if (h1 == nd - 1) return steps + 1; h1++; break;
        case '-': t[h0]--; break;
        case '+': t[h0]++; break;
        case '.': t[h1] = t[h0]; break;
        case ',': t[h0] = t[h1]; break;
        case '[':
            if (t[h0] == 0) {
                int d = 1, j = ip + 1;
                for (; j < nc; j++) {
                    uint8_t c = fetch(t, la, lib, j);
                    if (c == '[') d++;
                    else if (c == ']' && --d == 0) break;
                }
                if (j >= nc) return steps + 1;
                ip = j;
            }
            break;
        case ']':
            if (t[h0] != 0) {
                int d = 1, j = ip - 1;
                for (; j >= 0; j--) {
                    uint8_t c = fetch(t, la, lib, j);
                    if (c == ']') d++;
                    else if (c == '[' && --d == 0) break;
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

/* One interaction on tape t (A ++ B, n = la + lb bytes) with library c (lc bytes; used by libmode 2 only). */
long x_run(uint8_t *t, int la, int lb, const uint8_t *c, int lc, long max_steps, int libmode) {
    uint8_t snap[TAPE_MAX];
    int n = la + lb;
    if (libmode == 0) return runx(t, n, la, t + la, lb, max_steps);
    if (libmode == 1) { memcpy(snap, t + la, lb); return runx(t, n, la, snap, lb, max_steps); }
    if (libmode == 2) return runx(t, n, la, c, lc, max_steps);
    return runx(t, n, la, t, 0, max_steps);
}

int x_cut(const uint8_t *t, int n, int marker, int lmin, int lmax, int32_t *out) {
    int k = 0, start = 0;
    for (int i = 0; i < n; i++) {
        int len = i + 1 - start;
        if ((t[i] == marker && len >= lmin) || len == lmax) {
            out[k++] = len;
            start = i + 1;
        }
    }
    int r = n - start;
    if (r > 0) {
        if (r >= lmin || k == 0) out[k++] = r;
        else if (out[k - 1] + r <= lmax) out[k - 1] += r;
        else { out[k - 1] += r - lmin; out[k++] = lmin; }
    }
    return k;
}

/* One epoch (as bffvl.c vl_epoch). lib[p] is the index (into src) of pair p's library program (libmode 2). Mode 0 =
   run, 1 = noexec (nothing runs; the cut rule still applies). Returns total steps; *nout = new N. */
long x_epoch(const uint8_t *src, const int32_t *lens, int N, const int32_t *perm, const int32_t *lib, uint8_t *dst,
             int32_t *newlens, int32_t *origin, int *nout, long max_steps, int mode, int libmode, int marker,
             int lmin, int lmax) {
    static __thread int64_t *offs = 0;
    static __thread int cap = 0;
    uint8_t tape[TAPE_MAX];
    int32_t cuts[TAPE_MAX];
    if (2 * lmax > TAPE_MAX) return -1;
    if (cap < N + 1) {
        free(offs);
        cap = 2 * N + 16;
        offs = (int64_t *)malloc(sizeof(int64_t) * cap);
    }
    offs[0] = 0;
    for (int i = 0; i < N; i++) offs[i + 1] = offs[i] + lens[i];
    long total = 0;
    int64_t w = 0;
    int k = 0;
    for (int p = 0; p + 1 < N; p += 2) {
        int a = perm[p], b = perm[p + 1], la = lens[a], lb = lens[b], n = la + lb;
        memcpy(tape, src + offs[a], la);
        memcpy(tape + la, src + offs[b], lb);
        if (mode == 0) {
            int c = libmode == 2 ? lib[p / 2] : 0;
            total += x_run(tape, la, lb, src + offs[c], lens[c], max_steps, libmode);
        }
        int np = x_cut(tape, n, marker, lmin, lmax, cuts);
        for (int j = 0; j < np; j++) {
            newlens[k] = cuts[j];
            origin[k] = p / 2;
            k++;
        }
        memcpy(dst + w, tape, n);
        w += n;
    }
    if (N % 2) {
        int a = perm[N - 1];
        memcpy(dst + w, src + offs[a], lens[a]);
        newlens[k] = lens[a];
        origin[k] = -1;
        k++;
    }
    *nout = k;
    return total;
}

static uint64_t sm(uint64_t *s) {
    uint64_t z = (*s += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}

static int isop(uint8_t b) {
    return b == '<' || b == '>' || b == '{' || b == '}' || b == '-' || b == '+' || b == '.' || b == ',' ||
           b == '[' || b == ']';
}

static int is_copy(const uint8_t *y, int ly, const uint8_t *x, int lx, int tol, int thr_pct, int opmin) {
    if (ly < lx - tol || ly > lx + tol) return 0;
    int m = ly < lx ? ly : lx, f = 0, nop = 0, op = 0;
    for (int j = 0; j < m; j++) {
        int e = y[j] == x[j];
        f += e;
        if (isop(x[j])) { nop++; op += e; }
    }
    if (f * 100 < thr_pct * lx) return 0;
    if (opmin && nop > 0 && op * 100 < opmin * nop) return 0;
    return 1;
}

/* Copies of x among the pieces after the first of tape t (n bytes) after a run. */
static int count_copies(const uint8_t *t, int n, const uint8_t *x, int lx, int marker, int lmin, int lmax, int tol,
                        int thr, int opmin) {
    int32_t cuts[TAPE_MAX];
    int np = x_cut(t, n, marker, lmin, lmax, cuts), pos = cuts[0], c = 0;
    for (int j = 1; j < np; j++) {
        c += is_copy(t + pos, cuts[j], x, lx, tol, thr, opmin);
        pos += cuts[j];
    }
    return c;
}

/* Interaction screen. x runs first (as A). Partner B: if hb != NULL, B = hb (lhb bytes, e.g. a host in libmode 1);
   otherwise lp random bytes. Library (libmode 2): if hc != NULL, C = hc; otherwise lc random bytes. Returns the
   number of trials (of `trials`) in which a piece after the first is a copy of x; *copies = total copies.
   Random bytes come from a splitmix stream. Instruction bytes in x need >= opmin % matched only if x has any
   (an inert program has none, so the byte threshold alone decides). */
int x_screen(const uint8_t *x, int lx, const uint8_t *hb, int lhb, int lp, const uint8_t *hc, int lhc, int lc,
             int trials, uint64_t seed, long max_steps, int libmode, int mode, int marker, int lmin, int lmax,
             int tol, int thr, int opmin, int *copies) {
    uint8_t tape[TAPE_MAX], cbuf[TAPE_MAX];
    uint64_t s = seed;
    int hit = 0, tot = 0;
    for (int q = 0; q < trials; q++) {
        int lb = hb ? lhb : lp, n = lx + lb;
        memcpy(tape, x, lx);
        if (hb) memcpy(tape + lx, hb, lhb);
        else for (int j = 0; j < lp; j++) tape[lx + j] = (uint8_t)sm(&s);
        const uint8_t *c = hc;
        int lcc = lhc;
        if (!hc) { for (int j = 0; j < lc; j++) cbuf[j] = (uint8_t)sm(&s); c = cbuf; lcc = lc; }
        if (mode == 0) x_run(tape, lx, lb, c, lcc, max_steps, libmode);
        int k = count_copies(tape, n, x, lx, marker, lmin, lmax, tol, thr, opmin);
        hit += k > 0;
        tot += k;
    }
    *copies = tot;
    return hit;
}

void x_match(const uint8_t *buf, const int32_t *lens, int N, const uint8_t *x, int lx, int tol, int thr_pct,
             int opmin, int32_t *out) {
    int64_t off = 0;
    for (int i = 0; i < N; i++) {
        const uint8_t *y = buf + off;
        int ly = lens[i];
        off += ly;
        if (!is_copy(y, ly, x, lx, tol, thr_pct, opmin)) { out[i] = -1; continue; }
        int m = ly < lx ? ly : lx, f = 0;
        for (int j = 0; j < m; j++) f += y[j] == x[j];
        out[i] = f - (ly > lx ? ly - lx : lx - ly);
    }
}
