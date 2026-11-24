import PowerSeeking.Statement
open PowerSeeking

-- TradeChain of a transitive relation is contained in the relation
theorem tc_sub {α} (R : α → α → Prop) (ht : ∀ x y z, R x y → R y z → R x z) :
    ∀ {x y}, TradeChain R x y → R x y := by
  intro x y h
  induction h with
  | step h => exact h
  | trans h _ ih => exact ht _ _ _ h ih

-- S1c part 1: the "no money pump" conjunct follows from transitivity + strict money monotonicity alone
example (le : (Fin 2 × ℝ) → (Fin 2 × ℝ) → Prop)
    (ht : ∀ s t u, le s t → le t u → le s u)
    (hm : ∀ g m₁ m₂, m₁ < m₂ → StrictPref le (g, m₁) (g, m₂)) :
    ∀ g m₀ m₁, TradeChain le (g, m₀) (g, m₁) → m₀ ≤ m₁ := by
  intro g m₀ m₁ h
  by_contra hlt
  exact (hm g m₁ m₀ (lt_of_not_ge hlt)).2 (tc_sub le ht h)

-- ... and a COMPLETE relation satisfies the same no-pump property
example : ∀ g (m₀ m₁ : ℝ), TradeChain (fun s t : Fin 2 × ℝ => s.2 ≤ t.2) (g, m₀) (g, m₁) → m₀ ≤ m₁ := by
  intro g m₀ m₁ h
  exact tc_sub (fun s t : Fin 2 × ℝ => s.2 ≤ t.2) (fun _ _ _ a b => le_trans a b) h

-- S1c part 2: no strict cycle is automatic for any relation
example {α} (le : α → α → Prop) (ht : ∀ p q r, le p q → le q r → le p r) (p : α) :
    ¬ TradeChain (StrictPref le) p p := by
  intro h
  have : StrictPref le p p := tc_sub _ (fun x y z hxy hyz =>
    ⟨ht _ _ _ hxy.1 hyz.1, fun hzx => hyz.2 (ht _ _ _ hzx hxy.1)⟩) h
  exact this.2 this.1

-- S1d: indicator of consistency is a witness
theorem cons_append {Obs Act} : ∀ (π : List (Obs × Act) → Obs → Act) (h : List (Obs × Act)) o a,
    ConsistentWith π (h ++ [(o, a)]) ↔ ConsistentWith π h ∧ a = π h o
  | π, [], o, a => by simp [ConsistentWith]
  | π, (o', a') :: rest, o, a => by
      simp only [List.cons_append, ConsistentWith]
      rw [cons_append]; tauto

example : S1d_HistoryUtilityTriviality := by
  intro Obs Act π
  classical
  refine ⟨fun h => if ConsistentWith π h then 1 else 0, ?_⟩
  intro h o a hc hne
  have h1 : ¬ ConsistentWith π (h ++ [(o, a)]) := by rw [cons_append]; tauto
  have h2 : ConsistentWith π (h ++ [(o, π h o)]) := by rw [cons_append]; exact ⟨hc, rfl⟩
  simp [h1, h2]

-- S1b: three applications of the hypothesis
example : S1b_IntransitiveMoneyPump := by
  intro G blt lt a b c hab hbc hca hε m₀
  obtain ⟨e1, he1, h1⟩ := hε a b m₀ hab
  obtain ⟨e2, he2, h2⟩ := hε b c (m₀ - e1) hbc
  obtain ⟨e3, he3, h3⟩ := hε c a (m₀ - e1 - e2) hca
  exact ⟨m₀ - e1 - e2 - e3, (sub_lt_self _ he3).trans ((sub_lt_self _ he2).trans (sub_lt_self _ he1)), .trans h1 (.trans h2 (.step h3))⟩

-- S3d: small witness
example : S3d_IncompletePreferencesEscape := by
  refine ⟨fun x y => x = y ∨ (x = .short false ∧ y = .short true) ∨ (x = .long false ∧ y = .long true),
    ?_, ?_, ?_, ?_, ?_⟩
  · intro x; simp
  · intro x y z h1 h2; rcases h1 with h1 | h1 | h1 <;> rcases h2 with h2 | h2 | h2 <;> simp_all
  · simp [StrictPref]
  · simp [StrictPref]
  · intro b₁ b₂; simp [StrictPref]
