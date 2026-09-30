#!/usr/bin/env python3
"""Official JAH Equation Archive generator.

Each equation is solved ONCE, at generation time, and published officially
as a JAH-EQ-######## record. The calculator site then RETRIEVES the record
instead of solving again. A solve history ("Record") is kept client-side.

Deterministic: record i is a pure function of i (seeded RNG), so any range
can be (re)generated identically. Chunks of 150 -> data/equations/eq-cNNNNN.jsonl.gz
Index -> data/index/eq.idx.json.gz (JSONL: id, title, type, chunk).
"""
import gzip, json, math, os, random, sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EQDIR = os.path.join(ROOT, 'data', 'equations')
IDXDIR = os.path.join(ROOT, 'data', 'index')
STATEDIR = os.path.join(ROOT, 'code', 'equations')
STATE = os.path.join(STATEDIR, 'state.json')
CHUNK = 150

TYPES = ['linear', 'quadratic', 'system2', 'trig', 'power', 'log', 'exp',
         'evaluate', 'percent', 'derivative', 'integral', 'geometry']


def fmt_num(x):
    """Nice display: integer, simple fraction, else 4 decimals. Proper \u2212 minus."""
    if isinstance(x, Fraction):
        if x.denominator == 1:
            t = str(x.numerator)
        else:
            t = f"{x.numerator}/{x.denominator}"
    elif isinstance(x, float):
        if x.is_integer():
            t = str(int(x))
        else:
            r = round(x, 4)
            t = str(int(r)) if float(r).is_integer() else str(r)
    else:
        t = str(x)
    return t.replace('-', '\u2212') if t.startswith('-') else t


def fr(a, b):
    return Fraction(a, b)


def _coefx(a):
    if a == 1:
        return 'x'
    if a == -1:
        return '\u2212x'
    return f'{fmt_num(a)}x'


def gen_linear(r):
    a = r.choice([v for v in range(-9, 10) if v not in (0, 1)])
    x = r.randint(-12, 12)
    b = r.randint(-20, 20)
    c = a * x + b
    sol = fr(c - b, a)
    return {
        'type': 'linear',
        'title': f'Solve {_poly_str([(a, 1), (b, 0)])} = {fmt_num(c)}',
        'equation': f'{_poly_str([(a, 1), (b, 0)])} = {fmt_num(c)}',
        'steps': [
            f'{_poly_str([(a, 1), (b, 0)])} = {fmt_num(c)}',
            f'{_coefx(a)} = {fmt_num(c)} \u2212 ({fmt_num(b)}) = {fmt_num(c - b)}',
            f'x = {fmt_num(c - b)} / {fmt_num(a)} = {fmt_num(sol)}',
        ],
        'solution': f'x = {fmt_num(sol)}',
        'check': f'Substitute x = {fmt_num(sol)}: holds \u2713',
    }


def gen_quadratic(r):
    r1 = r.randint(-9, 9)
    r2 = r.randint(-9, 9)
    while r2 == r1:
        r2 = r.randint(-9, 9)
    a = r.choice([1, 1, 1, 2, -1, 3])
    b = -a * (r1 + r2)
    c = a * r1 * r2
    disc = b * b - 4 * a * c
    sdisc = math.isqrt(disc)
    x1 = fr(-b + sdisc, 2 * a)
    x2 = fr(-b - sdisc, 2 * a)
    terms = [(a, 2), (b, 1), (c, 0)]
    terms = [(cf, p) for cf, p in terms if cf != 0]
    eq = _poly_str(terms) + ' = 0'
    eqx = eq.replace('x\u00b2', 'x\u00b2')
    return {
        'type': 'quadratic',
        'title': f'Solve {eqx}',
        'equation': eqx,
        'steps': [
            eqx,
            f'Discriminant D = b\u00b2 \u2212 4ac = {b}\u00b2 \u2212 4({a})({c}) = {disc}',
            f'\u221aD = {sdisc}',
            f'x = (\u2212b \u00b1 \u221aD) / 2a = ({-b} \u00b1 {sdisc}) / {2 * a}',
            f'x = {fmt_num(x1)} or x = {fmt_num(x2)}',
        ],
        'solution': f'x = {fmt_num(x1)} or x = {fmt_num(x2)}',
        'check': f'Roots verify: a(x\u2212x1)(x\u2212x2) expands back \u2713',
    }


def gen_system2(r):
    x0 = r.randint(-9, 9)
    y0 = r.randint(-9, 9)
    a = r.randint(1, 6); b = r.randint(1, 6)
    c = r.randint(1, 6); d = r.randint(1, 6)
    while a * d - b * c == 0:
        c = r.randint(1, 6); d = r.randint(1, 6)
    e = a * x0 + b * y0
    f = c * x0 + d * y0
    det = a * d - b * c
    xs = fr(d * e - b * f, det)
    ys = fr(a * f - c * e, det)
    return {
        'type': 'system2',
        'title': f'Solve the system: {a}x + {b}y = {e}; {c}x + {d}y = {f}',
        'equation': f'{a}x + {b}y = {e} and {c}x + {d}y = {f}',
        'steps': [
            f'(1) {a}x + {b}y = {e}',
            f'(2) {c}x + {d}y = {f}',
            f'Determinant = {a}({d}) \u2212 {b}({c}) = {det}',
            f'x = ({d}({e}) \u2212 {b}({f})) / {det} = {fmt_num(xs)}',
            f'y = ({a}({f}) \u2212 {c}({e})) / {det} = {fmt_num(ys)}',
        ],
        'solution': f'x = {fmt_num(xs)}, y = {fmt_num(ys)}',
        'check': f'{a}({fmt_num(xs)}) + {b}({fmt_num(ys)}) = {e} \u2713',
    }


def gen_trig(r):
    fn = r.choice(['sin', 'cos', 'tan'])
    ang = r.choice([0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 270, 300, 330])
    rad = math.radians(ang)
    val = {'sin': math.sin(rad), 'cos': math.cos(rad), 'tan': math.tan(rad)}[fn]
    if abs(val) > 1e9:
        return gen_trig(r)
    disp = fmt_num(round(val, 4))
    return {
        'type': 'trig',
        'title': f'Evaluate {fn}({ang}\u00b0)',
        'equation': f'{fn}({ang}\u00b0) = ?',
        'steps': [
            f'{fn}({ang}\u00b0)',
            f'Convert: {ang}\u00b0 = {fmt_num(round(rad, 4))} radians',
            f'{fn}({fmt_num(round(rad, 4))}) = {disp}',
        ],
        'solution': f'{fn}({ang}\u00b0) = {disp}',
        'check': f'Unit-circle value \u2713',
    }


def gen_power(r):
    base = r.randint(2, 9)
    n = r.choice([2, 2, 2, 3, 3, 4])
    k = base ** n
    return {
        'type': 'power',
        'title': f'Solve x^{n} = {k}',
        'equation': f'x^{n} = {k}',
        'steps': [
            f'x^{n} = {k}',
            f'x = {n}th root of {k}',
            f'{base}^{n} = {k}, so x = {base}',
        ],
        'solution': f'x = {base}',
        'check': f'{base}^{n} = {k} \u2713',
    }


def gen_log(r):
    b = r.choice([2, 2, 3, 5, 10, 10])
    k = r.randint(1, 4)
    x = b ** k
    return {
        'type': 'log',
        'title': f'Solve log{b}(x) = {k}',
        'equation': f'log{b}(x) = {k}',
        'steps': [
            f'log{b}(x) = {k}',
            f'x = {b}^{k}',
            f'x = {x}',
        ],
        'solution': f'x = {x}',
        'check': f'log{b}({x}) = {k} \u2713',
    }


def gen_exp(r):
    b = r.choice([2, 2, 3, 5, 10])
    m = r.randint(1, 5)
    k = b ** m
    return {
        'type': 'exp',
        'title': f'Solve {b}^x = {k}',
        'equation': f'{b}^x = {k}',
        'steps': [
            f'{b}^x = {k}',
            f'{b}^x = {b}^{m}',
            f'x = {m}',
        ],
        'solution': f'x = {m}',
        'check': f'{b}^{m} = {k} \u2713',
    }


def gen_evaluate(r):
    # nested ((a op b) op c) with recorded intermediate steps
    a = r.randint(2, 25); b = r.randint(2, 25); c = r.randint(2, 12)
    op1 = r.choice(['+', '-', '*'])
    op2 = r.choice(['+', '-', '*', '/'])
    ops = {'+': lambda x, y: x + y, '-': lambda x, y: x - y,
           '*': lambda x, y: x * y, '/': lambda x, y: x / y}
    if op2 == '/':
        # make divisible: c divides (a op1 b)
        v1 = ops[op1](a, b)
        c = r.choice([d for d in range(2, 13) if v1 % d == 0] or [1])
    v1 = ops[op1](a, b)
    v2 = ops[op2](v1, c)
    sym = {'+': '+', '-': '\u2212', '*': '\u00d7', '/': '\u00f7'}
    expr = f'({a} {sym[op1]} {b}) {sym[op2]} {c}'
    return {
        'type': 'evaluate',
        'title': f'Evaluate {expr}',
        'equation': f'{expr} = ?',
        'steps': [
            expr,
            f'{a} {sym[op1]} {b} = {fmt_num(v1)}',
            f'{fmt_num(v1)} {sym[op2]} {c} = {fmt_num(v2)}',
        ],
        'solution': f'{expr} = {fmt_num(v2)}',
        'check': f'Order of operations: parentheses first \u2713',
    }


def gen_percent(r):
    p = r.choice([5, 10, 15, 20, 25, 30, 40, 50, 75])
    n = r.randint(1, 40) * 10
    v = p * n / 100
    return {
        'type': 'percent',
        'title': f'What is {p}% of {n}?',
        'equation': f'{p}% of {n} = ?',
        'steps': [
            f'{p}% of {n}',
            f'= {p}/100 \u00d7 {n}',
            f'= {fmt_num(v)}',
        ],
        'solution': f'{p}% of {n} = {fmt_num(v)}',
        'check': f'{fmt_num(v)} / {n} = {p}% \u2713',
    }


def _poly_terms(r, degree):
    terms = []
    for p in range(degree, -1, -1):
        coef = r.randint(1, 9) * r.choice([1, -1])
        if coef:
            terms.append((coef, p))
    if not terms:
        terms = [(r.randint(1, 9), 0)]
    return terms


def _poly_str(terms):
    parts = []
    for coef, p in terms:
        a = abs(coef)
        if p == 0:
            t = str(a)
        elif p == 1:
            t = f'{a}x' if a != 1 else 'x'
        else:
            t = f'{a}x^{p}' if a != 1 else f'x^{p}'
        if not parts:
            parts.append(('\u2212' if coef < 0 else '') + t)
        else:
            parts.append((' \u2212 ' if coef < 0 else ' + ') + t)
    return ''.join(parts)


def gen_derivative(r):
    deg = r.choice([2, 2, 3, 3, 4])
    terms = _poly_terms(r, deg)
    dterms = [(c * p, p - 1) for c, p in terms if p > 0]
    steps = [f'f(x) = {_poly_str(terms)}', 'Apply the power rule d/dx[x^n] = n\u00b7x^(n\u22121):']
    for c, p in terms:
        if p > 0:
            steps.append(f'd/dx[{_poly_str([(c, p)])}] = {c * p}x^{p - 1}' if p - 1 > 1 else
                         f'd/dx[{_poly_str([(c, p)])}] = {c * p}x' if p - 1 == 1 else
                         f'd/dx[{_poly_str([(c, p)])}] = {c * p}')
        else:
            steps.append(f'd/dx[{c}] = 0 (constant)')
    sol = _poly_str(dterms) if dterms else '0'
    steps.append(f"f'(x) = {sol}")
    return {
        'type': 'derivative',
        'title': f"Differentiate f(x) = {_poly_str(terms)}",
        'equation': f"d/dx[{_poly_str(terms)}] = ?",
        'steps': steps,
        'solution': f"f'(x) = {sol}",
        'check': 'Power rule applied term by term \u2713',
    }


def gen_integral(r):
    deg = r.choice([1, 2, 2, 3])
    terms = _poly_terms(r, deg)
    iterms = [(fr(c, p + 1), p + 1) for c, p in terms]
    steps = [f'\u222b({_poly_str(terms)}) dx', 'Power rule \u222bx^n dx = x^(n+1)/(n+1):']
    for c, p in terms:
        nc = fr(c, p + 1)
        steps.append(f'\u222b{_poly_str([(c, p)])} dx = {fmt_num(nc)}x^{p + 1}')
    def _fterm(coef_fr, p):
        neg = coef_fr < 0
        a = abs(coef_fr)
        cs = fmt_num(a)
        if p == 0:
            t = cs
        elif p == 1:
            t = 'x' if cs == '1' else cs + 'x'
        else:
            t = f'x^{p}' if cs == '1' else cs + f'x^{p}'
        return neg, t
    parts = [_fterm(cfr, p) for cfr, p in iterms]
    sol = ''
    for k, (neg, t) in enumerate(parts):
        if k == 0:
            sol += ('\u2212' if neg else '') + t
        else:
            sol += (' \u2212 ' if neg else ' + ') + t
    sol += ' + C'
    steps.append(f'= {sol}')
    return {
        'type': 'integral',
        'title': f"Integrate \u222b({_poly_str(terms)}) dx",
        'equation': f"\u222b({_poly_str(terms)}) dx = ?",
        'steps': steps,
        'solution': sol,
        'check': 'Differentiating the answer returns the integrand \u2713',
    }


def gen_geometry(r):
    shape = r.choice(['circle', 'circle', 'triangle', 'rectangle', 'box', 'sphere'])
    if shape == 'circle':
        rad = r.randint(1, 15)
        area = math.pi * rad ** 2
        return {'type': 'geometry', 'title': f'Area of a circle, radius {rad}',
                'equation': f'A = \u03c0r\u00b2, r = {rad}',
                'steps': [f'A = \u03c0 \u00d7 {rad}\u00b2', f'A = \u03c0 \u00d7 {rad**2}', f'A \u2248 {round(area, 4)}'],
                'solution': f'A = {rad**2}\u03c0 \u2248 {round(area, 4)}',
                'check': f'\u03c0 \u00d7 {rad}\u00b2 \u2713'}
    if shape == 'triangle':
        b = r.randint(2, 20); h = r.randint(2, 20)
        area = fr(b * h, 2)
        return {'type': 'geometry', 'title': f'Area of a triangle, base {b}, height {h}',
                'equation': f'A = \u00bdb\u00b7h, b = {b}, h = {h}',
                'steps': [f'A = \u00bd \u00d7 {b} \u00d7 {h}', f'A = {fmt_num(area)}'],
                'solution': f'A = {fmt_num(area)}',
                'check': f'\u00bd \u00d7 {b} \u00d7 {h} \u2713'}
    if shape == 'rectangle':
        w = r.randint(2, 25); h = r.randint(2, 25)
        return {'type': 'geometry', 'title': f'Area of a {w} \u00d7 {h} rectangle',
                'equation': f'A = w\u00b7h = {w} \u00d7 {h}',
                'steps': [f'A = {w} \u00d7 {h}', f'A = {w * h}'],
                'solution': f'A = {w * h}',
                'check': f'{w} \u00d7 {h} = {w * h} \u2713'}
    if shape == 'box':
        l = r.randint(2, 12); w = r.randint(2, 12); h = r.randint(2, 12)
        return {'type': 'geometry', 'title': f'Volume of a {l} \u00d7 {w} \u00d7 {h} box',
                'equation': f'V = l\u00b7w\u00b7h = {l} \u00d7 {w} \u00d7 {h}',
                'steps': [f'V = {l} \u00d7 {w} \u00d7 {h}', f'V = {l * w * h}'],
                'solution': f'V = {l * w * h}',
                'check': f'{l} \u00d7 {w} \u00d7 {h} \u2713'}
    rad = r.randint(1, 10)
    vol = 4 / 3 * math.pi * rad ** 3
    return {'type': 'geometry', 'title': f'Volume of a sphere, radius {rad}',
            'equation': f'V = \u2154\u03c0r\u00b3, r = {rad}',
            'steps': [f'V = \u2154\u03c0 \u00d7 {rad}\u00b3', f'V = \u2154\u03c0 \u00d7 {rad**3}', f'V \u2248 {round(vol, 4)}'],
            'solution': f'V = {rad**3}\u00b7\u2154\u03c0 \u2248 {round(vol, 4)}',
            'check': f'\u2154\u03c0 \u00d7 {rad}\u00b3 \u2713'}


GENS = {'linear': gen_linear, 'quadratic': gen_quadratic, 'system2': gen_system2,
        'trig': gen_trig, 'power': gen_power, 'log': gen_log, 'exp': gen_exp,
        'evaluate': gen_evaluate, 'percent': gen_percent, 'derivative': gen_derivative,
        'integral': gen_integral, 'geometry': gen_geometry}

STAMP = 'Official JAH Equation Archive \u2014 solved once, published officially, retrieved thereafter.'


def generate_record(i):
    r = random.Random(1000003 + i * 7919)
    t = TYPES[(i - 1) % len(TYPES)]
    # mix it up: every 13th record picks randomly for variety
    if i % 13 == 0:
        t = r.choice(TYPES)
    rec = GENS[t](r)
    rec['id'] = f'JAH-EQ-{i:08d}'
    rec['n'] = i
    rec['stamp'] = STAMP
    return rec


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {'next_index': 1}


def save_state(st):
    json.dump(st, open(STATE, 'w'), indent=1)


def append_index(records, chunk_no):
    # Single-member gzip, written atomically: appending a new gzip member per
    # chunk breaks DecompressionStream in browsers ("trailing junk").
    idx_path = os.path.join(IDXDIR, 'eq.idx.json.gz')
    lines = []
    if os.path.exists(idx_path):
        with gzip.open(idx_path, 'rt', encoding='utf-8') as f:
            lines = [l for l in f.read().split('\n') if l]
    seen = set()
    for l in lines:
        try: seen.add(json.loads(l)['id'])
        except Exception: pass
    for rec in records:
        if rec['id'] in seen: continue
        seen.add(rec['id'])
        lines.append(json.dumps({'id': rec['id'], 't': rec['title'],
                                 'y': rec['type'], 'c': chunk_no},
                                ensure_ascii=False))
    tmp = idx_path + '.tmp'
    with gzip.open(tmp, 'wt', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    os.replace(tmp, idx_path)


def run(count):
    st = load_state()
    start = st['next_index']
    records = [generate_record(i) for i in range(start, start + count)]
    # Group records by their true chunk so partial chunks from earlier runs
    # keep holding their records; new records just top up / extend.
    bychunk = {}
    for rec in records:
        bychunk.setdefault((rec['n'] - 1) // CHUNK + 1, []).append(rec)
    for chunk_no in sorted(bychunk):
        path = os.path.join(EQDIR, f'eq-c{chunk_no:05d}.jsonl.gz')
        block = bychunk[chunk_no]
        newlines = [json.dumps(rec, ensure_ascii=False) for rec in block]
        if os.path.exists(path):
            # Append to the existing (partial) chunk, atomically.
            with gzip.open(path, 'rt', encoding='utf-8') as f:
                existing = [l for l in f.read().split('\n') if l]
            existing_ns = set()
            for l in existing:
                try:
                    existing_ns.add(json.loads(l)['n'])
                except Exception:
                    pass
            for rec in block:
                if rec['n'] in existing_ns:
                    raise SystemExit(f'duplicate record n={rec["n"]} in {path}')
            lines = existing + newlines
            tmp = path + '.tmp'
            with gzip.open(tmp, 'wt', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')
            os.replace(tmp, path)
        else:
            with gzip.open(path, 'wt', encoding='utf-8') as f:
                f.write('\n'.join(newlines) + '\n')
        append_index(block, chunk_no)
    st['next_index'] = start + count
    save_state(st)
    print(f'wrote {count} equations: JAH-EQ-{start:08d}..JAH-EQ-{start+count-1:08d}')


if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
