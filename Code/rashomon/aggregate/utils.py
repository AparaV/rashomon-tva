import numpy as np

from itertools import chain, combinations


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def find_feasible_sum_subsets(S: list[np.ndarray], theta):
    # See this https://stackoverflow.com/q/62311484/5055644
    # NP Hard? https://link.springer.com/chapter/10.1007/978-3-540-24777-7_11

    num_sets = len(S)
    if num_sets == 0:
        return []

    S1 = S[0]
    S1_feasible_idx = np.where(S1 <= theta)[0]

    if num_sets == 1:
        feasible_combs = [[x] for x in S1_feasible_idx]
        return feasible_combs

    # Since the list is sorted, add the first elements of the remaining sets
    # Then use this to check feasibility of indices in S1_feasible_idx
    first_element_sum = np.sum([s[0] for s in S[1:]])
    feasible_combs = []
    for i in S1_feasible_idx:
        theta_i = theta - S1[i]
        # Safe to stop our search on first infeasible index because of sorting
        if first_element_sum > theta_i:
            break
        subproblem_res_i = find_feasible_sum_subsets(S[1:], theta_i)
        for res in subproblem_res_i:
            feasible_combs.append([i] + res)

    return feasible_combs
