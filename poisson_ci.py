# -*- coding: utf-8 -*-
"""ポアソン分布の平均の正確な信頼区間（Garwood の方法）を、scipy を使わずに求める。
n 回の観測から、平均 λ の両側 (1-alpha) 信頼区間 [L, U] を返す。
L は P(X >= n | L) = alpha/2、U は P(X <= n | U) = alpha/2 を満たす。"""
import math

def cdf(k, lam):
    if k < 0:
        return 0.0
    term = math.exp(-lam); s = term
    for i in range(1, k + 1):
        term *= lam / i; s += term
    return s

def _solve(f, lo, hi):
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def ci(n, alpha=0.05):
    a = alpha / 2
    L = 0.0 if n == 0 else _solve(lambda lam: a - (1 - cdf(n - 1, lam)), 0.0, 10 * n + 10)
    U = _solve(lambda lam: cdf(n, lam) - a, 0.0, 10 * n + 20)
    return L, U

if __name__ == "__main__":
    for n in (1, 3, 14):
        print(n, [round(x, 3) for x in ci(n)])
