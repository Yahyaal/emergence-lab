/* BFF interpreter (Aguera y Arcas et al. 2024, "Computational Life"), used by bff.py.

   A tape of n bytes is both program and data. Instruction pointer and two heads start at 0;
   heads wrap modulo n. Bytes other than the ten instructions are no-ops:

     <  head0--        >  head0++        {  head1--        }  head1++
     -  tape[head0]--  +  tape[head0]++  .  tape[head1] = tape[head0]
     ,  tape[head0] = tape[head1]
     [  if tape[head0] == 0, jump forward to the matching ]
     ]  if tape[head0] != 0, jump back to the matching [

   Execution stops after max_steps instructions, when the instruction pointer leaves the
   tape, or at an unmatched bracket. Brackets are matched by scanning, at the moment of the
   jump, because the program can rewrite itself. */
#include <stdint.h>

static long run(uint8_t *t, int n, long max_steps) {
    int ip = 0, h0 = 0, h1 = 0;
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

long bff_run(uint8_t *tape, int n, long max_steps) { return run(tape, n, max_steps); }

/* One epoch: for each pair (a, b), run the tape soup[a] + soup[b] (each L bytes) and write the
   halves back. Mode 0 = BFF, 1 = no execution (control), 2 = copy-all (deceptive control: the
   first program is copied over the second, whatever it is). Returns the total steps run. */
long bff_epoch(uint8_t *soup, int L, const int32_t *pairs, int npairs, long max_steps, int mode) {
    uint8_t tape[1024];
    long total = 0;
    if (2 * L > 1024) return -1;
    for (int p = 0; p < npairs; p++) {
        uint8_t *a = soup + (long)pairs[2 * p] * L, *b = soup + (long)pairs[2 * p + 1] * L;
        if (mode == 1) continue;
        if (mode == 2) { for (int i = 0; i < L; i++) b[i] = a[i]; continue; }
        for (int i = 0; i < L; i++) { tape[i] = a[i]; tape[L + i] = b[i]; }
        total += run(tape, 2 * L, max_steps);
        for (int i = 0; i < L; i++) { a[i] = tape[i]; b[i] = tape[L + i]; }
    }
    return total;
}
