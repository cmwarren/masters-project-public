from __future__ import division
import sys
import re
import codecs
import glob
import numpy as np
from scipy import stats
from itertools import groupby
sys.path.append('hyperwords')
from representations.embedding import Embedding


def gb(collection):
    keyfunc = lambda x: x[0]
    groups = groupby(sorted(collection, key=keyfunc), keyfunc)
    return {k: set([v for k_, v in g]) for k, g in groups}


def alignment_eval(src_vecs, trg_vecs, align_file, src_test_file, trg_test_file, b_reverse, b_print=False):
    Es = Embedding(src_vecs, True)
    Et = Embedding(trg_vecs, True)

    poss_aligns=[[int(x) for x in l.strip().split()[:3]] for l in open(align_file).readlines()]
    sure_aligns=[[int(x) for x in l.strip().split()[:3]] for l in open(align_file).readlines() if l.strip().split()[-1]!="P"]

    ssents=[l.strip().split(">")[1].split("<")[0].split() for l in codecs.open(src_test_file,'r',"utf8",errors='ignore').readlines()]
    tsents=[l.strip().split(">")[1].split("<")[0].split() for l in codecs.open(trg_test_file,'r',"utf8",errors='ignore').readlines()] #swap 3 and 4

    if b_reverse:
        # Reverse the evaluation source/target
        poss_aligns = [(sid, twid, swid) for sid, swid, twid in poss_aligns]
        sure_aligns = [(sid, twid, swid) for sid, swid, twid in sure_aligns]
        Es, Et = Et, Es
        ssents, tsents = tsents, ssents

    poss_aligns = gb([(sid-1, (swid-1, twid-1)) for sid, swid, twid in poss_aligns])
    sure_aligns = gb([(sid-1, (swid-1, twid-1)) for sid, swid, twid in sure_aligns])

    size_a = 0.0
    size_s = 0.0
    size_a_and_s = 0.0
    size_a_and_p = 0.0

    for sid, (ssent, tsent) in enumerate(zip(ssents, tsents)):
        alignment = set()
        twords = [tword.split("_")[0].lower() for tword in tsent]
        tvecs = [Et.represent(tword) if tword in Et.wi else None for tword in twords]
        for swid, sword in enumerate(ssent):
            sword = sword.split("_")[0].lower()
            if sword in Es.wi:
                svec = Es.represent(sword)
                sims = [svec.dot(tvec) if tvec is not None else -1.0 for tvec in tvecs]
                alignment.add((swid, np.argmax(sims)))
                #print(sword,twords[np.argmax(sims)])

        sure = sure_aligns[sid]
        poss = poss_aligns[sid]

        size_a += float(len(alignment))
        size_s += float(len(sure))
        s_a=alignment & sure
        p_a=alignment & poss
        size_a_and_s += float(len(s_a))
        size_a_and_p += float(len(p_a))

    if b_print:
        print '{0:.4f}'.format((size_a_and_s + size_a_and_p) / (size_a + size_s))

    return (size_a_and_s + size_a_and_p) / (size_a + size_s)


def main():
    return alignment_eval(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[-1] == 'R', True)

if __name__ == "__main__":
    main()
