/* E-81 (D-070): variable-length BFF ("BFF-VL"), used by scripts/bffvl.py.

   The interpreter is BFF exactly (emergence/programs/bff.c), with head1 starting at the partner's first byte
   (head1 = LA, the variable-length form of the h = 64 head-start rule of E-56/E-80 Part B; head0 and the
   instruction pointer start at 0). Every byte value other than the ten instructions is a no-op, including the
   marker M.

   The only new rule is how a pair's tape is split back into programs. The tape A ++ B (n = LA + LB bytes) is cut
   after every marker byte M and wherever a piece reaches LMAX bytes (greedy, left to right); a cut that would make
   a piece shorter than LMIN is skipped; a last piece shorter than LMIN is merged into the one before it (or, if that
   would exceed LMAX, the last cut moves back so the last piece has LMIN bytes). A pair can therefore leave 1 to
   n / LMIN programs. Bytes are conserved exactly, so the soup is a fixed byte budget W with a varying number of
   programs. With no marker in the tape and LMAX = LA = LB the cut is the fixed BFF midpoint (bit-identical to
   bff_kernels.epoch_h with h1 = L). */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define TAPE_MAX 1024

static long run(uint8_t *t, int n, long max_steps, int h1, int edge) {
    int ip = 0, h0 = 0;
    long steps = 0;
    h1 %= n;
    while (ip >= 0 && ip < n && steps < max_steps) {
        switch (t[ip]) {
        case '<': if (edge && h0 == 0) return steps + 1; h0 = (h0 + n - 1) % n; break;
        case '>': if (edge && h0 == n - 1) return steps + 1; h0 = (h0 + 1) % n; break;
        case '{': if (edge && h1 == 0) return steps + 1; h1 = (h1 + n - 1) % n; break;
        case '}': if (edge && h1 == n - 1) return steps + 1; h1 = (h1 + 1) % n; break;
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

long vl_run(uint8_t *t, int n, long max_steps, int h1, int edge) { return run(t, n, max_steps, h1, edge); }

/* Piece lengths of tape t (n bytes) under the cut rule; returns the number of pieces. marker < 0 or > 255: no
   marker (cuts only at lmax). Requires n >= lmin and lmax >= 2 * lmin. */
int vl_cut(const uint8_t *t, int n, int marker, int lmin, int lmax, int32_t *out) {
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

/* One epoch. Programs are stored back to back in src (lengths lens[0..N-1]). perm is a permutation of 0..N-1;
   pairs are (perm[0], perm[1]), (perm[2], perm[3]), ...; with N odd the last program sits out unchanged. The new soup
   is written back to back into dst (same total bytes), its lengths into newlens, and for each new program the
   index of the pair it came from into origin (-1 for the one that sat out) and its rank among the pair's pieces
   into rank. Mode 0 = BFF-VL, 1 = noexec (nothing runs; the cut rule still applies), 2 = copyall (the B region
   is overwritten by A repeated, whatever A is; deceptive control). Returns total steps; *nout = new N. */
long vl_epoch(const uint8_t *src, const int32_t *lens, int N, const int32_t *perm, uint8_t *dst, int32_t *newlens,
              int32_t *origin, int32_t *rank, int *nout, long max_steps, int mode, int marker, int lmin, int lmax,
              int edge) {
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
        if (mode == 0) total += run(tape, n, max_steps, la, edge);
        else if (mode == 2) for (int i = 0; i < lb; i++) tape[la + i] = tape[i % la];
        int np = vl_cut(tape, n, marker, lmin, lmax, cuts);
        for (int j = 0; j < np; j++) {
            newlens[k] = cuts[j];
            origin[k] = p / 2;
            rank[k] = j;
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
        rank[k] = 0;
        k++;
    }
    *nout = k;
    return total;
}

/* Copy screen for one program x (length lx) against random partners of length lp: x runs first; a partner counts
   as copied into if some piece other than the first is a copy of x: same length within +-tol bytes and, over the
   first min(len, lx) bytes, >= thr_pct % of x's bytes matched AND >= opmin % of x's instruction bytes matched.
   x itself need not survive (a copier that fills the whole tape overwrites itself when the tape length is not a
   multiple of its own length). Returns the number of partners (of `partners`) in which
   x made at least one copy; *copies = total copies over all partners. Partner bytes come from a splitmix stream. */
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
    if (opmin && (nop == 0 || op * 100 < opmin * nop)) return 0;
    return 1;
}

int vl_screen(const uint8_t *x, int lx, int lp, int partners, uint64_t seed, long max_steps, int marker, int lmin,
              int lmax, int tol, int thr_pct, int opmin, int mode, int edge, int *copies) {
    uint8_t tape[TAPE_MAX];
    int32_t cuts[TAPE_MAX];
    uint64_t s = seed;
    int hit = 0, tot = 0;
    for (int q = 0; q < partners; q++) {
        int n = lx + lp;
        memcpy(tape, x, lx);
        for (int j = 0; j < lp; j++) tape[lx + j] = (uint8_t)sm(&s);
        if (mode == 0) run(tape, n, max_steps, lx, edge);
        else if (mode == 2) for (int i = 0; i < lp; i++) tape[lx + i] = tape[i % lx];
        int np = vl_cut(tape, n, marker, lmin, lmax, cuts), pos = cuts[0], c = 0;
        for (int j = 1; j < np; j++) {
            c += is_copy(tape + pos, cuts[j], x, lx, tol, thr_pct, opmin);
            pos += cuts[j];
        }
        hit += c > 0;
        tot += c;
    }
    *copies = tot;
    return hit;
}

/* Family membership for many programs at once: out[i] = 1 if program i (stored back to back, lengths lens) is a
   copy of x by is_copy(tol, thr_pct, opmin). */
void vl_members(const uint8_t *buf, const int32_t *lens, int N, const uint8_t *x, int lx, int tol, int thr_pct,
                int opmin, uint8_t *out) {
    int64_t off = 0;
    for (int i = 0; i < N; i++) {
        out[i] = (uint8_t)is_copy(buf + off, lens[i], x, lx, tol, thr_pct, opmin);
        off += lens[i];
    }
}

/* Match scores for many programs against x: out[i] = bytes of program i equal to x over the first min(len, lx)
   bytes, or -1 if program i fails is_copy(tol, thr_pct, opmin). Used to assign programs to the closer of two
   candidates in head-to-head assays. */
void vl_match(const uint8_t *buf, const int32_t *lens, int N, const uint8_t *x, int lx, int tol, int thr_pct,
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
