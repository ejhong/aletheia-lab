/-! Exploratory only. A trial of proofs for the draft statements of Amendment 4 (tier 2B), compiled on 2026-11-23
before the lock against a copy of `statement-check/Statement4.draft.lean`, to make sure no draft statement is false
as written. Not a finding. The proofs of record are in `lean/GodelArgument/Results4.lean`. -/
import GodelArgument.Statement4
import GodelArgument.Audit
import Foundation.Propositional.Entailment.Cl

/-!
# Results for the concrete logic of knowledge with quantifiers (Amendment 4, tier 2B)

Each theorem has exactly the type of a statement in `Statement4.lean`. The logic is defined there, and the
derivations are built from its axioms and modus ponens. The Foundation import is there only to reach Mathlib's
tactics; no Foundation definition or theorem is used.
-/

namespace GodelArgument.QEL

open Form

/-! ## Building derivations

Axioms must be sentences, so each use of an axiom carries a proof that the formula has no free variable. Every
derivation below is made from the axioms alone, where every line is a sentence, and is then weakened to an
arbitrary theory. -/

/-- Discharges "this formula is a sentence" for the concrete formulas used below, which mention only the
variables 0 and 1. -/
macro "closed_tac" defs:(ppSpace colGt term:max)* : tactic =>
  `(tactic| (intro x hx
             simp only [Form.Free, Form.neg, Form.and, Form.iff, Form.ex, U, diagAll, diagQ, $[$defs:term],*] at hx
             tauto))

lemma ofSig {T : Set Form} {φ : Form} (h : Sig φ) (hc : Closed φ) : Proves T φ := .ax (.inl ⟨h, hc⟩)

lemma ofBase {T : Set Form} {φ : Form} (h : BaseAx φ) (hc : Closed φ) : Proves T φ := ofSig (.base h) hc

lemma ofKSig {T : Set Form} {φ : Form} (h : Sig φ) (hc : Closed φ) : Proves T (K φ) :=
  .ax (.inr ⟨φ, h, hc, rfl⟩)

/-- What the logic proves outright, every theory proves. -/
lemma weaken {T : Set Form} {φ : Form} (h : Proves ∅ φ) : Proves T φ := by
  induction h with
  | ax hax => exact .ax hax
  | hyp hm => exact absurd hm (Set.notMem_empty _)
  | mp _ _ ih₁ ih₂ => exact .mp ih₁ ih₂

/-- Whatever the logic proves outright is a sentence. -/
lemma closed_of_proves {φ : Form} (h : Proves ∅ φ) : Closed φ := by
  induction h with
  | ax hax =>
    rcases hax with ⟨_, hc⟩ | ⟨ψ, _, hc, rfl⟩
    · exact hc
    · exact fun x hx => hc x hx
  | hyp hm => exact absurd hm (Set.notMem_empty _)
  | mp _ _ ih₁ _ => exact fun x hx => ih₁ x (Or.inr hx)

/-- Modus ponens under a universal quantifier. -/
lemma allMP {x : ℕ} {φ ψ : Form} (h : Proves ∅ (all x (imp φ ψ))) (h' : Proves ∅ (all x φ)) :
    Proves ∅ (all x ψ) := by
  have hc : Closed (imp (all x (imp φ ψ)) (imp (all x φ) (all x ψ))) := by
    intro y hy
    have := closed_of_proves h y
    simp only [Form.Free] at hy this
    tauto
  exact .mp (.mp (ofBase (.dist x φ ψ) hc) h) h'

/-- An axiom schema, under a universal quantifier. -/
lemma allBase {x : ℕ} {φ : Form} (h : BaseAx φ) (hc : Closed (all x φ)) : Proves ∅ (all x φ) :=
  ofSig (.gen x (.base h)) hc

/-- An axiom schema, known, under a universal quantifier: `K∀x φ` is an axiom, and `K∀x φ → ∀x Kφ` is one. -/
lemma allK {x : ℕ} {φ : Form} (h : BaseAx φ) (hc : Closed (all x φ)) : Proves ∅ (all x (K φ)) := by
  have hc' : Closed (imp (K (all x φ)) (all x (K φ))) := by
    intro y hy
    have := hc y
    simp only [Form.Free] at hy this
    tauto
  exact .mp (ofBase (.kall x φ) hc') (ofKSig (.gen x (.base h)) hc)

/-- `∀x (φ → ψ)` gives `∃x φ → ∃x ψ`. -/
lemma exMono {x : ℕ} {φ ψ : Form} (h : Proves ∅ (all x (imp φ ψ))) : Proves ∅ (imp (ex x φ) (ex x ψ)) := by
  have hcl := closed_of_proves h
  have ht : Tautology (imp (imp φ ψ) (imp (neg ψ) (neg φ))) := by
    intro v ⟨hf, hi⟩; simp only [Form.neg, hi]; tauto
  have hc1 : Closed (all x (imp (imp φ ψ) (imp (neg ψ) (neg φ)))) := by
    intro y hy
    have := hcl y
    simp only [Form.Free, Form.neg] at hy this
    tauto
  have h1 : Proves ∅ (all x (imp (neg ψ) (neg φ))) := allMP (allBase (.taut ht) hc1) h
  have hc2 : Closed (imp (all x (imp (neg ψ) (neg φ))) (imp (all x (neg ψ)) (all x (neg φ)))) := by
    intro y hy
    have := hcl y
    simp only [Form.Free, Form.neg] at hy this
    tauto
  have h2 : Proves ∅ (imp (all x (neg ψ)) (all x (neg φ))) := .mp (ofBase (.dist x _ _) hc2) h1
  have ht2 : Tautology (imp (imp (all x (neg ψ)) (all x (neg φ))) (imp (ex x φ) (ex x ψ))) := by
    intro v ⟨hf, hi⟩; simp only [Form.ex, Form.neg, hi]; tauto
  have hc3 : Closed (imp (imp (all x (neg ψ)) (all x (neg φ))) (imp (ex x φ) (ex x ψ))) := by
    intro y hy
    have := hcl y
    simp only [Form.Free, Form.neg, Form.ex] at hy this
    tauto
  exact .mp (ofBase (.taut ht2) hc3) h2

/-- K2 applied to a theorem that is an implication. -/
lemma k2_of_proves {φ ψ : Form} (h : Proves ∅ (imp φ ψ)) : Proves ∅ (imp (K (imp φ ψ)) (imp (K φ) (K ψ))) := by
  refine ofBase (.k2 φ ψ) ?_
  intro y hy
  have := closed_of_proves h y
  simp only [Form.Free] at hy this
  tauto

/-! ## S3a -/

/-- S3a. By induction on derivations. An axiom of the first kind is known by an axiom of the second kind; an
axiom `Kψ` is known by K4; modus ponens is carried under `K` by K2. -/
theorem necessitationIsDerived : NecessitationIsDerived := by
  intro φ h
  induction h with
  | ax hax =>
    rcases hax with ⟨hs, hc⟩ | ⟨ψ, hs, hc, rfl⟩
    · exact ofKSig hs hc
    · exact .mp (ofBase (.k4 ψ) (fun x hx => hc x (by simpa [Form.Free] using hx))) (ofKSig hs hc)
  | hyp hm => exact absurd hm (Set.notMem_empty _)
  | mp h₁ _ ih₁ ih₂ => exact .mp (.mp (k2_of_proves h₁) ih₁) ih₂

/-! ## The diagonal instance -/

/-- `K¬U(e,e) ↔ U(e,e)`: the matrix of `diagAll` with `x` replaced by `e`. -/
def diagInst : Form := iff (K (neg (U 1 1))) (U 1 1)

/-- Universal instantiation of `diagAll` at `x := e`. -/
lemma instDiag : BaseAx (imp diagAll diagInst) := by
  have hff : FreeFor 1 0 (iff (K (neg (U 0 0))) (U 1 0)) := by
    simp [U, Form.iff, Form.and, Form.neg, Form.FreeFor]
  have hs : subst 0 1 (iff (K (neg (U 0 0))) (U 1 0)) = diagInst := by
    simp [diagInst, U, Form.iff, Form.and, Form.neg, Form.subst]
  have := BaseAx.inst 0 1 (iff (K (neg (U 0 0))) (U 1 0)) hff
  rwa [hs] at this

/-! ## S3b -/

/-- Reinhardt's proof (pp. 327–328), carried out under `∀e`. Write `u` for `U(e,e)`. Instantiating `x := e`
under `K` gives `K(K¬u ↔ u)`; known factivity gives `K(K¬u → ¬u)`; so `K¬u`; factivity then gives both `¬u` and
`K¬u ↔ u`, hence `u`. So `∀e ¬K diagAll`. -/
lemma all_not_known_diag : Proves ∅ (all 1 (neg (K diagAll))) := by
  let u : Form := U 1 1
  let fk : Form := imp (K (neg u)) (neg u)
  let t : Form := imp diagInst (imp fk (neg u))
  have ht : Tautology t := by
    intro v ⟨hf, hi⟩; simp only [t, fk, u, diagInst, Form.iff, Form.and, Form.neg, hi]; tauto
  have L1 : Proves ∅ (all 1 (K (imp diagAll diagInst))) := allK instDiag (by closed_tac diagInst)
  have L2 : Proves ∅ (all 1 (imp (K (imp diagAll diagInst)) (imp (K diagAll) (K diagInst)))) :=
    allBase (.k2 _ _) (by closed_tac diagInst)
  have L3 : Proves ∅ (all 1 (imp (K diagAll) (K diagInst))) := allMP L2 L1
  have L4 : Proves ∅ (all 1 (K t)) := allK (.taut ht) (by closed_tac t fk u diagInst)
  have L5 : Proves ∅ (all 1 (K fk)) := allK (.k3 _) (by closed_tac fk u)
  have L6 : Proves ∅ (all 1 (imp (K t) (imp (K diagInst) (K (imp fk (neg u)))))) :=
    allBase (.k2 _ _) (by closed_tac t fk u diagInst)
  have L7 : Proves ∅ (all 1 (imp (K (imp fk (neg u))) (imp (K fk) (K (neg u))))) :=
    allBase (.k2 _ _) (by closed_tac fk u)
  have L8 : Proves ∅ (all 1 fk) := allBase (.k3 _) (by closed_tac fk u)
  have L9 : Proves ∅ (all 1 (imp (K diagInst) diagInst)) := allBase (.k3 _) (by closed_tac diagInst)
  let big : Form := imp (imp (K diagAll) (K diagInst)) (imp (K t) (imp (K fk)
    (imp (imp (K t) (imp (K diagInst) (K (imp fk (neg u)))))
    (imp (imp (K (imp fk (neg u))) (imp (K fk) (K (neg u))))
    (imp fk (imp (imp (K diagInst) diagInst) (neg (K diagAll))))))))
  have hbig : Tautology big := by
    intro v ⟨hf, hi⟩; simp only [big, fk, u, diagInst, Form.iff, Form.and, Form.neg, hi]; tauto
  have L0 : Proves ∅ (all 1 big) := allBase (.taut hbig) (by closed_tac big t fk u diagInst)
  exact allMP (allMP (allMP (allMP (allMP (allMP (allMP L0 L3) L4) L5) L6) L7) L8) L9

/-- S3b. From `∀e ¬K diagAll` by a tautology. -/
theorem knowingWhichSetRefuted : KnowingWhichSetRefuted := by
  intro T
  have hdn : Tautology (imp (all 1 (neg (K diagAll))) (neg (ex 1 (K diagAll)))) := by
    intro v ⟨hf, hi⟩; simp only [Form.ex, Form.neg, hi]; tauto
  exact weaken (.mp (ofBase (.taut hdn) (by closed_tac)) all_not_known_diag)

/-! ## S3c, S3d, S3e -/

/-- The logic proves: the thesis implies `∃e (q(e) ∧ ¬K q(e))`. Reinhardt's proof (p. 326): instantiate at
`x := e` and use "what is known is so". -/
lemma thesis_imp_unknown : Proves ∅ (imp (ex 1 diagAll) (ex 1 (and diagQ (neg (K diagQ))))) := by
  have ht : Tautology (imp (imp diagAll diagInst) (imp (imp (K diagQ) diagQ)
      (imp diagAll (and diagQ (neg (K diagQ)))))) := by
    intro v ⟨hf, hi⟩; simp only [diagInst, diagQ, Form.iff, Form.and, Form.neg, hi]; tauto
  exact exMono (allMP (allMP (allBase (.taut ht) (by closed_tac diagInst))
    (allBase instDiag (by closed_tac diagInst))) (allBase (.k3 _) (by closed_tac)))

/-- S3c. -/
theorem thesisGivesUnknownTruth : ThesisGivesUnknownTruth :=
  fun _ h => .mp (weaken thesis_imp_unknown) h

/-- S3d. As S3c, with "what is known is so" used a second time, for `¬q(e)`. -/
theorem thesisGivesAbsolutelyUndecidable : ThesisGivesAbsolutelyUndecidable := by
  intro T h
  have ht : Tautology (imp (imp diagAll diagInst) (imp (imp (K diagQ) diagQ) (imp (imp (K (neg diagQ)) (neg diagQ))
      (imp diagAll (and (neg (K diagQ)) (neg (K (neg diagQ)))))))) := by
    intro v ⟨hf, hi⟩; simp only [diagInst, diagQ, Form.iff, Form.and, Form.neg, hi]; tauto
  have h1 : Proves ∅ (all 1 (imp diagAll (and (neg (K diagQ)) (neg (K (neg diagQ)))))) :=
    allMP (allMP (allMP (allBase (.taut ht) (by closed_tac diagInst)) (allBase instDiag (by closed_tac diagInst)))
      (allBase (.k3 _) (by closed_tac))) (allBase (.k3 _) (by closed_tac))
  exact .mp (weaken (exMono h1)) h

/-- S3e. Necessitation (S3a) applied to the implication behind S3c, then K2. -/
theorem knownThesisGivesKnownUnknownTruth : KnownThesisGivesKnownUnknownTruth :=
  fun _ h => .mp (weaken (.mp (k2_of_proves thesis_imp_unknown)
    (necessitationIsDerived _ thesis_imp_unknown))) h

/-! ## S3f: consistency, by reading `K φ` as `φ` -/

/-- An interpretation: a domain and a meaning for each relation symbol. -/
structure Model where
  D : Type
  rel : ℕ → D → D → Prop

def eval (𝔐 : Model) : (ℕ → 𝔐.D) → Form → Prop
  | s, atom r a b => 𝔐.rel r (s a) (s b)
  | _, fls => False
  | s, imp φ ψ => eval 𝔐 s φ → eval 𝔐 s ψ
  | s, all x φ => ∀ d, eval 𝔐 (Function.update s x d) φ
  | s, K φ => eval 𝔐 s φ

lemma eval_congr (𝔐 : Model) (φ : Form) : ∀ s s' : ℕ → 𝔐.D, (∀ x, Free x φ → s x = s' x) →
    (eval 𝔐 s φ ↔ eval 𝔐 s' φ) := by
  induction φ with
  | atom r a b => intro s s' h; simp [eval, h a (Or.inl rfl), h b (Or.inr rfl)]
  | fls => intro s s' _; simp [eval]
  | imp φ ψ ih₁ ih₂ =>
    intro s s' h
    simp only [eval]
    rw [ih₁ s s' (fun x hx => h x (Or.inl hx)), ih₂ s s' (fun x hx => h x (Or.inr hx))]
  | all y φ ih =>
    intro s s' h
    simp only [eval]
    refine forall_congr' (fun d => ih _ _ (fun x hx => ?_))
    by_cases hxy : x = y
    · subst hxy; simp
    · simp [Function.update_of_ne hxy, h x ⟨hxy, hx⟩]
  | K φ ih => intro s s' h; simpa [eval] using ih s s' h

lemma subst_of_not_free (x y : ℕ) (φ : Form) : ¬ Free x φ → subst x y φ = φ := by
  induction φ with
  | atom r a b =>
    intro h
    have ha : ¬ a = x := fun e => h (Or.inl e.symm)
    have hb : ¬ b = x := fun e => h (Or.inr e.symm)
    simp [subst, ha, hb]
  | fls => intro _; rfl
  | imp φ ψ ih₁ ih₂ =>
    intro h
    simp only [subst]
    rw [ih₁ (fun hx => h (Or.inl hx)), ih₂ (fun hx => h (Or.inr hx))]
  | all z φ ih =>
    intro h
    by_cases hz : z = x
    · simp [subst, hz]
    · simp only [subst, hz, ↓reduceIte]
      rw [ih (fun hx => h ⟨fun e => hz e.symm, hx⟩)]
  | K φ ih => intro h; simp only [subst]; rw [ih h]

lemma eval_subst (𝔐 : Model) (x y : ℕ) (φ : Form) : ∀ s : ℕ → 𝔐.D, FreeFor y x φ →
    (eval 𝔐 s (subst x y φ) ↔ eval 𝔐 (Function.update s x (s y)) φ) := by
  induction φ with
  | atom r a b =>
    intro s _
    simp only [subst, eval]
    by_cases ha : a = x <;> by_cases hb : b = x <;> simp [ha, hb, Function.update_of_ne]
  | fls => intro s _; simp [subst, eval]
  | imp φ ψ ih₁ ih₂ =>
    intro s h
    simp only [subst, eval]
    rw [ih₁ s h.1, ih₂ s h.2]
  | all z φ ih =>
    intro s h
    by_cases hz : z = x
    · subst hz
      simp only [subst, ↓reduceIte, eval]
      refine forall_congr' (fun d => ?_)
      simp [Function.update_idem]
    · rcases h with h | h | ⟨hzy, h⟩
      · exact absurd h hz
      · rw [subst_of_not_free x y (all z φ) (fun hf => h hf.2)]
        simp only [eval]
        refine forall_congr' (fun d => eval_congr 𝔐 φ _ _ (fun w hw => ?_))
        have hwx : w ≠ x := fun e => h (e ▸ hw)
        by_cases hwz : w = z
        · subst hwz; simp
        · simp [Function.update_of_ne hwz, Function.update_of_ne hwx]
      · simp only [subst, hz, ↓reduceIte, eval]
        refine forall_congr' (fun d => ?_)
        rw [ih _ h, Function.update_of_ne (Ne.symm hzy), Function.update_comm hz d (s y) s]
  | K φ ih => intro s h; simpa [subst, eval] using ih s h

lemma sound_base {φ} (h : BaseAx φ) (𝔐 : Model) (s : ℕ → 𝔐.D) : eval 𝔐 s φ := by
  induction h generalizing s with
  | taut ht => exact ht (eval 𝔐 s) ⟨fun h => h, fun _ _ => Iff.rfl⟩
  | inst x y φ hff => intro hall; exact (eval_subst 𝔐 x y φ s hff).mpr (hall _)
  | dist x φ ψ => intro h₁ h₂ d; exact h₁ d (h₂ d)
  | vac x φ hnf =>
    intro hφ d
    refine (eval_congr 𝔐 φ _ _ (fun w hw => ?_)).mp hφ
    have : w ≠ x := fun e => hnf (e ▸ hw)
    simp [Function.update_of_ne this]
  | k2 φ ψ => intro h₁ h₂; exact h₁ h₂
  | k3 φ => intro h; exact h
  | k4 φ => intro h; exact h
  | kall x φ => intro h; exact h

lemma sound_sig {φ} (h : Sig φ) (𝔐 : Model) : ∀ s : ℕ → 𝔐.D, eval 𝔐 s φ := by
  induction h with
  | base hb => exact fun s => sound_base hb 𝔐 s
  | gen x _ ih => exact fun s d => ih _

theorem sound {φ} (h : Proves ∅ φ) (𝔐 : Model) : ∀ s : ℕ → 𝔐.D, eval 𝔐 s φ := by
  induction h with
  | ax hax =>
    rcases hax with ⟨hs, _⟩ | ⟨ψ, hs, _, rfl⟩
    · exact sound_sig hs 𝔐
    · exact sound_sig hs 𝔐
  | hyp hm => exact absurd hm (Set.notMem_empty _)
  | mp _ _ ih₁ ih₂ => exact fun s => ih₁ s (ih₂ s)

/-- S3f. In a one-element interpretation with `K` erased every theorem is true, and falsehood is not. -/
theorem logicIsConsistent : LogicIsConsistent :=
  fun h => sound h ⟨Unit, fun _ _ _ => True⟩ (fun _ => ())


end GodelArgument.QEL
