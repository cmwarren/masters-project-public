from __future__ import division
import sys
import numpy as np
sys.path.append('hyperwords')
from representations.embedding import Embedding


def wiktionary_eval(src_vecs, trg_vecs, wiktionary_file, b_reverse, b_print=False, b_include_oov=False,
                     eval_dir=None, src_lang_code=None, trg_lang_code=None, precision_at_N=1):
    OOV = None
    INV = None

    if eval_dir is not None and src_lang_code is not None and trg_lang_code is not None:
        # These extra params are to do with outputting OOV and INV words during evaluation
        oov_filename = './' + eval_dir + '/wiktionary-eval/oov-' + src_lang_code + '-' + trg_lang_code + '.txt'
        inv_filename = './' + eval_dir + '/wiktionary-eval/inv-' + src_lang_code + '-' + trg_lang_code + '.txt'
        OOV = set() # Use sets, so that the words get de-duped
        INV = set()

    Es = Embedding(src_vecs, True)
    Et = Embedding(trg_vecs, True)

    BX = [(l.split("|||")[-1].strip(), l.split("|||")[0].strip()) for l in open(wiktionary_file).readlines()]
    if b_reverse:
        # Reverse the evaluation source/target
       BX = [(t, s) for s, t in BX]
       Es, Et = Et, Es

    BD=[]
    for s,t in BX:
        if s in Es.wi and t in Et.wi:
            BD.append((s,t))
            if INV is not None:
                INV.add(s + ' ||| ' + t)
        else:
            if b_include_oov:
                BD.append((s,t))
            if OOV is not None:
                OOV.add(s + ' ||| ' + t)

    p1, tot = 0, 0
    for s, t in BD:
        vs = Es.represent(s)
        scores = vs.dot(Et.m.T)
        if precision_at_N == 1:
            cand = Et.iw[np.nanargmax(scores)]
            if t==cand:
                p1+=1
        else:
            is_match = False
            indices = np.argsort(scores)[-precision_at_N:]  # positions
            for index in indices:
                cand = Et.iw[index]
                if t==cand:
                    is_match = True
                    break
            if is_match:
                p1 += 1
        tot += 1

    if b_print:
        print '{0:.4f}'.format(p1/tot)

    if eval_dir is not None and src_lang_code is not None and trg_lang_code is not None:
        inv_f = open(inv_filename, 'w')
        for inv in INV:
            inv_f.write(inv + '\n')
        inv_f.close()

        oov_f = open(oov_filename, 'w')
        for oov in OOV:
            oov_f.write(oov + '\n')
        oov_f.close()

    return p1/tot

def main():
    if len(sys.argv) > 5:
        return wiktionary_eval(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[-1] == 'R', b_print=True,
                               b_include_oov=False,
                               eval_dir=sys.argv[4], src_lang_code=sys.argv[5], trg_lang_code=sys.argv[6])
    else:
        return wiktionary_eval(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[-1] == 'R', b_print=True,
                               b_include_oov=False)


if __name__ == "__main__":
    main()