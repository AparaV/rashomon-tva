import math
import numpy as np
import itertools as it

from functools import reduce


def prime_factors(n):
    factors = []

    while n % 2 == 0:
        factors.append(2)
        n = n // 2

    sqrt_n = int(np.sqrt(n))
    for i in range(3, sqrt_n + 1, 2):
        while n % i == 0:
            factors.append(i)
            n = n // i

    if n > 2:
        factors.append(n)

    return factors


def generate_all_factorizations(factors):
    def prod(x):
        res = 1
        for xi in x:
            res *= xi
        return res

    if len(factors) <= 1:
        yield factors
        return

    for f in range(1, len(factors) + 1):
        for which_is in it.combinations(range(len(factors)), f):
            this_prod = prod(factors[i] for i in which_is)
            rest = [factors[i] for i in range(len(factors)) if i not in which_is]

            for remaining in generate_all_factorizations(rest):
                yield [this_prod] + remaining


def factorizations(factors):
    seen = set()
    for f in generate_all_factorizations(factors):
        f = tuple(sorted(f))
        if f in seen:
            continue
        seen.add(f)
        yield f


def factors(n):
    # From https://stackoverflow.com/a/6800214
    return set(
        reduce(
            list.__add__,
            ([i, n // i] for i in range(1, int(n**0.5) + 1) if n % i == 0),
        )
    )


def __num_admissible_poolings_classic__(h, m, R: int):
    if h == 1 or h == (R - 1) ** m:
        return 1

    N = 0
    primes = prime_factors(h)
    for f in factorizations(primes):
        k = len(f)
        if k > m:
            continue
        N_f = math.comb(m, k)
        for fi in f:
            if fi > R - 2:
                N_f = 0
                break
            N_f = N_f * math.comb(R - 2, fi - 1)
        N = N + N_f

    return N


def __num_admissible_poolings_complex__(h, m, R: np.array):
    if h == 1 or h == np.prod(R - 1):
        return 1

    N = 0
    arm_indices = np.arange(m)
    primes = prime_factors(h)
    for f in factorizations(primes):
        k = len(f)
        if k > m:
            continue
        for arm_perm in it.combinations(arm_indices, k):
            N_f = 1
            for idx in range(k):
                arm_idx = arm_perm[idx]
                if f[idx] > R[arm_idx] - 2:
                    N_f = 0
                    break
                N_f = N_f * math.comb(R[arm_idx] - 2, f[idx]-1)
            N += N_f

    return N


def num_admissible_poolings(h, m, R):
    # Lemma 4.7 \ref{lemma:num-sigma-matrix-pools}
    if isinstance(R, int):
        N = __num_admissible_poolings_classic__(h, m, R)
    else:
        N = __num_admissible_poolings_complex__(h, m, R)
    return N


def find_R(sigma):
    R = np.sum(~np.isinf(sigma), axis=1) + 2
    if np.all(R == R[0]):
        return int(R[0])
    return R


def powerset(arr):
    s = list(arr)
    return it.chain.from_iterable(it.combinations(s, r) for r in range(len(s)+1))


def sum_product_k(arr):
    # Adapted from https://www.geeksforgeeks.org/sum-of-products-of-all-possible-k-size-subsets-of-the-given-array/

    n = len(arr)
    cache = [0] * (n + 1)
    k_sum = [0] * (n + 1)

    k_sum[0] = 1
    # Case k = 1
    for i in range(1, n + 1):
        cache[i] = arr[i - 1]
        k_sum[1] += arr[i - 1]

    # Case k = 2 through n
    for k in range(2, n + 1):
        prev_sum = k_sum[k - 1]

        for i in range(1, n + 1):
            # Sum of (i+1)-th to n-th elements in the (k-1)-th row
            prev_sum -= cache[i]
            cache[i] = arr[i - 1] * prev_sum

        k_sum[k] = np.sum(cache)

    return k_sum


def __num_pools_classic__(sigma, R: int):
    m, _ = sigma.shape
    z = np.sum(sigma, axis=1)
    z_sums = sum_product_k(z)

    H = 0
    for i in range(m + 1):
        sign = (-1) ** i
        H += sign * z_sums[i] * (R - 1) ** (m - i)

    return H


def __num_pools_complex__(sigma, R: np.array):
    m, _ = sigma.shape
    R = R - 1
    R_prod = np.prod(R)

    z = np.sum(sigma, axis=1, where=~np.isinf(sigma))
    indices = np.arange(m)
    z_combs = [list(x) for x in powerset(indices)]

    H = 0
    for comb in z_combs:
        sign = (-1) ** len(comb)
        z_sum = np.prod(z[comb])
        splits = R_prod / np.prod(R[comb])
        H += sign * z_sum * splits

    return H


def num_pools(sigma, R=None):
    # Lemma 4.5 \ref{lemma:sigma-ones-pools}

    if np.all(np.isinf(sigma)):
        return 1

    if R is None:
        R = find_R(sigma)
    if isinstance(R, int):
        H = __num_pools_classic__(sigma, R)
    else:
        H = __num_pools_complex__(sigma, R)
    return H
