import re


def _tok(s):
    return re.findall(r"\w+|[^\w\s]", s.lower(), re.UNICODE)


def _ngrams(tokens, n):
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


def _f1(p, r):
    return 2*p*r/(p+r) if (p+r) else 0.0


def sari(source: str, hypothesis: str, references, max_n=4) -> float:
    src = _tok(source); hyp = _tok(hypothesis); refs = [_tok(r) for r in (references or [])]
    if not refs: # ohne Referenzen ist SARI nicht definiert – 0 zurückgeben
        return 0.0
    score_sum = 0.0; count = 0
    for n in range(1, max_n+1):
        src_n = set(_ngrams(src, n))
        hyp_n = set(_ngrams(hyp, n))
        ref_n = set().union(*[set(_ngrams(r, n)) for r in refs])
        # KEEP
        keep_good = len(hyp_n & src_n & ref_n)
        keep_total = max(1, len(hyp_n & src_n))
        keep_prec = keep_good/keep_total
        keep_rec = keep_good/max(1, len(ref_n & src_n))
        keep_f = _f1(keep_prec, keep_rec)
        # ADD
        add_good = len((hyp_n - src_n) & ref_n)
        add_total = max(1, len(hyp_n - src_n))
        add_prec = add_good/add_total
        add_rec = add_good/max(1, len(ref_n - src_n))
        add_f = _f1(add_prec, add_rec)
        # DELETE
        del_good = len((src_n - ref_n) - hyp_n)
        del_total = max(1, len(src_n - hyp_n))
        del_prec = del_good/del_total
        del_rec = del_good/max(1, len(src_n - ref_n))
        del_f = _f1(del_prec, del_rec)
        score_sum += (keep_f + add_f + del_f)/3.0
        count += 1
    return score_sum/count if count else 0.0