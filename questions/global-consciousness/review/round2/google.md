<!-- {"vendor": "google", "model": "gemini-4-neon", "utc": "2026-11-23T15:53:32.035897+00:00", "input_tokens": 4542, "output_tokens": 31920, "cost_usd_list_price": 0.4924} -->

**(a) Errors of sign, algebra or logic**

- > "The second part, `Σ over seconds of [Z² − (Σ z²)/N]`, divided by `√(Σ over seconds of 2(N − 1)/N)`, measures eggs moving together and is blind to any one egg's variance."

  Correction: Only the *expectation* of this statistic is invariant to individual egg variances (remaining 0, so a miscalibrated egg creates no mean bias). Its *variance* is not: if one egg has true variance $v \neq 1$ while the other $N - 1$ have variance $1$, the denominator assumes variance $2(N - 1)/N$ per second whereas the true variance is $[2(N - 1)/N][1 + 2(v - 1)/N]$, leaving the standardized score over- or under-dispersed by that factor.

**(b) Factual statements confident are wrong**

Nothing found.

**(c) Instructions that contradict each other**

Nothing found.
