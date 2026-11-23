/-! Exploratory only. A trial of proofs for the draft Stage 2A statements, compiled on 2026-11-23 before the lock
against a copy of `statement-check/Statement2.draft.lean`, to make sure no draft statement is false as written.
Not a finding. The proofs of record are in `lean/GodelArgument/Results2.lean`, written against the locked file. -/
import GodelArgument.Statement2
import GodelArgument.Audit
import Foundation.FirstOrder.Incompleteness.Löb

/-!
# Stage 2A results

Each theorem has exactly the type of a statement in `Statement2.lean`. The first five are short derivations in
classical propositional logic from the stated hypotheses about `K`; nothing from arithmetic is used. The last two
exhibit systems built from Peano arithmetic, using Foundation's provability predicate, Gödel sentence and local
reflection.
-/

namespace GodelArgument

open FFL

/-! ## Reasoning under `K` -/

/-- What the base proves is known in any system that includes it. -/
lemma known_of_base {Fm S₀ S : Type} [Entailment S₀ Fm] [Entailment S Fm] {𝓑 : S₀} {𝓢 : S} {K : Fm → Fm}
    (hn : ClosedUnderNecessitation 𝓑 K) (hle : 𝓑 ⪯ 𝓢) {φ : Fm} (h : 𝓑 ⊢ φ) : 𝓢 ⊢ K φ :=
  hle.pbl (hn φ h)

/-- Modus ponens under `K`. -/
lemma known_mp {Fm S : Type} [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S Fm] {𝓢 : S}
    [Entailment.Cl 𝓢] {K : Fm → Fm} (h2 : KnowledgeClosedUnderMP 𝓢 K) {a c : Fm}
    (t : 𝓢 ⊢ K (a 🡒 c)) (ha : 𝓢 ⊢ K a) : 𝓢 ⊢ K c := by
  cl_prover [t, h2 a c, ha]

/-- From two known premises, a known conclusion, when the base proves the step. -/
lemma known_of_two {Fm S₀ S : Type} [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]
    {𝓑 : S₀} {𝓢 : S} [Entailment.Cl 𝓢] {K : Fm → Fm}
    (hn : ClosedUnderNecessitation 𝓑 K) (hle : 𝓑 ⪯ 𝓢) (h2 : KnowledgeClosedUnderMP 𝓢 K) {a b c : Fm}
    (t : 𝓑 ⊢ a 🡒 b 🡒 c) (ha : 𝓢 ⊢ K a) (hb : 𝓢 ⊢ K b) : 𝓢 ⊢ K c :=
  known_mp h2 (known_mp h2 (known_of_base hn hle t) ha) hb

/-- From three known premises, a known conclusion, when the base proves the step. -/
lemma known_of_three {Fm S₀ S : Type} [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm]
    [Entailment S Fm] {𝓑 : S₀} {𝓢 : S} [Entailment.Cl 𝓢] {K : Fm → Fm}
    (hn : ClosedUnderNecessitation 𝓑 K) (hle : 𝓑 ⪯ 𝓢) (h2 : KnowledgeClosedUnderMP 𝓢 K) {a b c d : Fm}
    (t : 𝓑 ⊢ a 🡒 b 🡒 c 🡒 d) (ha : 𝓢 ⊢ K a) (hb : 𝓢 ⊢ K b) (hc : 𝓢 ⊢ K c) : 𝓢 ⊢ K d :=
  known_mp h2 (known_of_two hn hle h2 t ha hb) hc

/-! ## The five derivations -/

/-- S2a. Under `K`: from the Gödel sentence `ψ ↔ ¬F(ψ)` and `F(ψ) → ψ`, first `¬F(ψ)`, then `ψ`. Only the
instance `φ := ψ` of the hypothesis is used. -/
theorem reinhardtTheorem3 : ReinhardtTheorem3 := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K F hn hle h2 ⟨ψ, hψ⟩ hs
  have kfix : 𝓢 ⊢ K (ψ 🡘 ∼F ψ) := known_of_base hn hle hψ
  have a : 𝓢 ⊢ K (∼F ψ) :=
    known_of_two hn hle h2 (a := ψ 🡘 ∼F ψ) (b := F ψ 🡒 ψ) (by cl_prover) kfix (hs ψ)
  have b : 𝓢 ⊢ K ψ := known_of_two hn hle h2 (a := ψ 🡘 ∼F ψ) (b := ∼F ψ) (by cl_prover) kfix a
  exact ⟨ψ, by cl_prover [a, b]⟩

/-- S2a′. S2a, then factivity applied to `K(¬F(ψ))`. -/
theorem knowerExceedsKnownSoundSystem : KnowerExceedsKnownSoundSystem := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K F hn hle h2 hf hg hs
  obtain ⟨ψ, h⟩ := reinhardtTheorem3 Fm S₀ S 𝓑 𝓢 K F hn hle h2 hg hs
  exact ⟨ψ, by cl_prover [h, hf (∼F ψ)]⟩

/-- S2b. Under `K`: if `Con F` were known, `F` would hold of `Con F`, hence of falsehood, so `Con F` would be
false; but what is known is so. Only the instance `φ := Con F` of the hypothesis is used. -/
theorem absoluteSecondIncompleteness : AbsoluteSecondIncompleteness := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K F hn hle h2 hkf g2 hs
  exact known_of_three hn hle h2 (a := K (∼F ⊥) 🡒 F (∼F ⊥)) (b := F (∼F ⊥) 🡒 F ⊥) (c := K (∼F ⊥) 🡒 ∼F ⊥)
    (by cl_prover) (hs _) (known_of_base hn hle g2) (hkf _)

/-- S2c. Under `K`, for the Gödel sentence `ψ` of `F`: `¬F(ψ)`, hence `ψ`, hence also `¬Kψ`. So `Kψ` and
`K¬Kψ` are both provable, and factivity turns the second into `¬Kψ`. Only the instance `φ := ψ` is used. -/
theorem knowingWhichSystemIsContradictory : KnowingWhichSystemIsContradictory := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K F hn hle h2 hf hkf ⟨ψ, hψ⟩ hs
  have kfix : 𝓢 ⊢ K (ψ 🡘 ∼F ψ) := known_of_base hn hle hψ
  have a : 𝓢 ⊢ K (∼F ψ) :=
    known_of_three hn hle h2 (a := ψ 🡘 ∼F ψ) (b := K ψ 🡘 F ψ) (c := K ψ 🡒 ψ) (by cl_prover) kfix (hs ψ) (hkf ψ)
  have b : 𝓢 ⊢ K ψ := known_of_two hn hle h2 (a := ψ 🡘 ∼F ψ) (b := ∼F ψ) (by cl_prover) kfix a
  have c : 𝓢 ⊢ K (∼K ψ) := known_of_two hn hle h2 (a := K ψ 🡘 F ψ) (b := ∼F ψ) (by cl_prover) (hs ψ) a
  cl_prover [b, c, hf (∼K ψ)]

/-- S2d. Suppose `K(K¬p ↔ p)`. Under `K`, with known factivity for `¬p`, this gives `¬p`; so `K¬p`. By
factivity the equivalence itself holds, so `p`; and `K¬p` gives `¬p`. -/
theorem noKnownSelfDiagonal : NoKnownSelfDiagonal := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K hn hle h2 hf hkf p
  have t : 𝓑 ⊢ (K (∼p) 🡘 p) 🡒 (K (∼p) 🡒 ∼p) 🡒 ∼p := by cl_prover
  cl_prover [known_of_base hn hle t, h2 (K (∼p) 🡘 p) ((K (∼p) 🡒 ∼p) 🡒 ∼p), h2 (K (∼p) 🡒 ∼p) (∼p), hkf (∼p),
    hf (∼p), hf (K (∼p) 🡘 p)]

/-! ## Hypotheses that cannot be dropped -/

section arithmetic

open FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

/-- S2b′. Witness: Peano arithmetic, with `K` and `F` both the identity ("`F` holds of φ" is φ itself). The
conclusion of S2b then reads `¬¬⊥`, which a consistent system does not prove. -/
theorem secondIncompletenessProvisoCannotBeDropped : SecondIncompletenessProvisoCannotBeDropped := by
  refine ⟨𝗣𝗔, id, id, fun φ h => h, inferInstance, fun φ ψ => by simp only [id]; cl_prover,
    fun φ => by simp only [id]; cl_prover, fun φ => by simp only [id]; cl_prover,
    fun φ => by simp only [id]; cl_prover, ?_⟩
  intro h
  have hb : (𝗣𝗔 : ArithmeticTheory) ⊢ ⊥ := by simp only [id] at h; cl_prover [h]
  exact Entailment.not_consistent_iff_inconsistent.mpr (Entailment.inconsistent_iff_provable_bot.mpr hb)
    inferInstance

/-- "Peano arithmetic proves σ", as a sentence of arithmetic: Foundation's standard provability predicate. -/
noncomputable abbrev provablePA : ArithmeticSentence → ArithmeticSentence :=
  fun σ => (𝗣𝗔 : ArithmeticTheory).standardProvability σ

/-- Peano arithmetic together with every sentence "if Peano arithmetic proves σ then σ". -/
abbrev PAWithReflection : ArithmeticTheory := 𝗣𝗔 ∪ (𝗣𝗔 : ArithmeticTheory).localReflectionOn Set.univ

/-- Peano arithmetic with reflection is true in the natural numbers, hence consistent
(Foundation's `models_localReflectionOn`). -/
lemma consistent_PAWithReflection : Entailment.Consistent PAWithReflection := by
  have : ℕ↓[ℒₒᵣ] ⊧* PAWithReflection := models_localReflectionOn
  exact consistent_of_model PAWithReflection ℕ↓[ℒₒᵣ]

/-- S2e. Necessitation and closure under modus ponens are derivability conditions D1 and D2; factivity is the
reflection schema; the Gödel sentence is Foundation's `gödel`; `p` is the negation of the Gödel sentence;
consistency is `models_localReflectionOn`. That this `K` does not know its own factivity then follows from S2d. -/
theorem knownFactivityCannotBeDropped : KnownFactivityCannotBeDropped := by
  unfold KnownFactivityCannotBeDropped
  intro K F 𝓢
  have hPA : (𝗣𝗔 : ArithmeticTheory) ⪯ 𝓢 := Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_left
  have hI : (𝗜𝚺₁ : ArithmeticTheory) ⪯ 𝓢 :=
    Entailment.WeakerThan.trans (inferInstance : (𝗜𝚺₁ : ArithmeticTheory) ⪯ 𝗣𝗔) hPA
  have d1 : ∀ {σ : ArithmeticSentence}, (𝗣𝗔 : ArithmeticTheory) ⊢ σ → (𝗣𝗔 : ArithmeticTheory) ⊢ K σ :=
    fun h => Entailment.WeakerThan.pbl (𝓢 := (𝗜𝚺₁ : ArithmeticTheory)) (Provability.D1 h)
  obtain ⟨G, hG⟩ : ∃ G : ArithmeticSentence, (𝗣𝗔 : ArithmeticTheory) ⊢ G 🡘 ∼K G :=
    ⟨gödel (𝗣𝗔 : ArithmeticTheory).standardProvability,
      Entailment.WeakerThan.pbl (𝓢 := (𝗜𝚺₁ : ArithmeticTheory)) gödel_spec⟩
  have flip : ∀ a b : ArithmeticSentence,
      (𝗣𝗔 : ArithmeticTheory) ⊢ a 🡘 ∼b → (𝗣𝗔 : ArithmeticTheory) ⊢ b 🡘 ∼a := fun a b h => by cl_prover [h]
  have taut : ∀ a : ArithmeticSentence, (𝗣𝗔 : ArithmeticTheory) ⊢ a 🡘 a := fun a => by cl_prover
  have hnec : ClosedUnderNecessitation (𝗣𝗔 : ArithmeticTheory) K := fun φ h => d1 h
  have hmp : KnowledgeClosedUnderMP 𝓢 K := fun φ ψ => hI.pbl Provability.D2
  have hfact : Factive 𝓢 K := by
    intro φ
    have : (𝗣𝗔 : ArithmeticTheory).standardProvability.refl φ ∈ 𝓢 :=
      Set.mem_union_right _ ((Provability.mem_localReflectionOn_iff _).mpr ⟨φ, trivial, rfl⟩)
    exact Entailment.Axiomatized.by_axm this
  have hcon : Entailment.Consistent 𝓢 := by
    have : ℕ↓[ℒₒᵣ] ⊧* 𝓢 := models_localReflectionOn
    exact consistent_of_model 𝓢 ℕ↓[ℒₒᵣ]
  have hp : 𝓢 ⊢ K (K (∼∼G) 🡘 ∼G) := by
    have e : (∼∼G : ArithmeticSentence) = G := by simp
    have : (𝗣𝗔 : ArithmeticTheory) ⊢ K (∼∼G) 🡘 ∼G := by rw [e]; exact flip _ _ hG
    exact hPA.pbl (d1 this)
  refine ⟨hnec, hPA, hmp, hfact, ⟨G, hG⟩, ?_, ⟨∼G, hp⟩, hcon, ?_⟩
  · intro φ
    have key : ∀ a : ArithmeticSentence, 𝓢 ⊢ K (a 🡘 a) := fun a => hPA.pbl (d1 (taut a))
    exact key (K φ)
  · intro hkf
    have hno := noKnownSelfDiagonal ArithmeticSentence ArithmeticTheory ArithmeticTheory 𝗣𝗔 𝓢 K hnec hPA hmp hfact
      hkf (∼G)
    have hb : 𝓢 ⊢ ⊥ := by cl_prover [hno, hp]
    exact Entailment.not_consistent_iff_inconsistent.mpr (Entailment.inconsistent_iff_provable_bot.mpr hb) hcon

end arithmetic


end GodelArgument
