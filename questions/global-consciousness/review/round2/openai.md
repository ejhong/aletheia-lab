<!-- {"vendor": "openai", "model": "gpt-6.2-astra", "utc": "2026-11-23T15:53:29.607346+00:00", "input_tokens": 4116, "output_tokens": 8076, "cost_usd_list_price": 0.356} -->

### (a) Errors of sign, algebra or logic

1. **“This follows the project's practice of standardising each device by its own measured variance, using only data from outside the event windows.”**  
   The formula measures mean square about 100. For an egg with mean \(\mu\ne100\), it estimates \(\operatorname{Var}(X)+(\mu-100)^2\), not variance alone.

2. **“Positive means more variance in the network's composite than chance gives, which is the direction the project reports.”**  
   The Wilson–Hilferty score is positive when \(\chi^2/df>(1-2/(9df))^3\), a threshold **below** 1. It indicates a mean square above the approximate null median, not necessarily above the null expectation; a mean offset can also raise it.

3. **“One test decides: the combined score of the events against the standard normal, one-sided in the project's direction.”**  
   Even with independent chance trials, events sharing estimated control scales have dependent scores: an underestimated scale raises scores in multiple windows. The standard-normal \(p\)-values and the stated \(1.96/\sqrt n\) interval are therefore nominal, not guaranteed by independent hardware.

4. **“`Z_all ≥ 3.09` (one-sided p ≤ 0.001)”**  
   At \(Z=3.09\), the standard-normal upper-tail probability is \(0.00100078\). The exact cutoff for \(p\le0.001\) is \(\Phi^{-1}(0.999)=3.0902323\ldots\).

5. **“This needs no assumption about the devices, only that an event day and its control day are alike under chance.”**  
   Independent sign flips require the **joint distribution of the scored differences** to be invariant under those flips. Even exchangeable raw days do not ensure this: the event's scale includes its control, the control's scale excludes itself, and scales are shared across pairs.

6. **“It has less power: at the benchmark, 58 pairs give an expected score of 1.8 where the main test gives 2.5.”**  
   For independent pairs with unit marginal variances and within-pair correlation \(\rho\), the expected standardized difference is \(0.33\sqrt{58}/\sqrt{2(1-\rho)}\). The value 1.8 assumes \(\rho=0\); lower power does not follow from the benchmark alone.

7. **“The second part, `Σ over seconds of [Z² − (Σ z²)/N]`, divided by `√(Σ over seconds of 2(N − 1)/N)`, measures eggs moving together and is blind to any one egg's variance.”**  
   Only its **expectation** is blind to a variance change in an independent, centered egg. Increasing that egg's variance increases the variance of its cross-products, while the stated denominator stays fixed.

8. **“`Z_all = Σ Z_event / √n` over the `n` evaluable events.”**  
   The eligibility rules allow \(n=0\), in which case the formula is \(0/0\): neither event verdict nor the interval is defined. The control combined score is likewise undefined if no control is evaluable.

### (b) Confidently wrong factual statements

1. **“This is squared, yielding a Chisquare-distributed quantity with one degree of freedom …”**  
   The quoted distributional claim is approximate, not exact: a composite of finitely many bit sums is discrete, so its square cannot have the continuous \(\chi^2_1\) distribution.

### (c) Contradictory instructions

None found.
