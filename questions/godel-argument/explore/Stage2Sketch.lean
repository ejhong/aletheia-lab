import Foundation.FirstOrder.Incompleteness.Examples
import Foundation.FirstOrder.Incompleteness.Löb
import Foundation.FirstOrder.Incompleteness.Reflection.Local
/-! Exploratory only: checks that draft Stage 2A statements are provable as written. Not a finding. -/
namespace GodelArgument.Sketch2
open FFL

section
variable {Fm S₀ S : Type} [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]

def KnowsTheoremsOf (𝓑 : S₀) (𝓢 : S) (K : Fm → Fm) : Prop := ∀ φ, 𝓑 ⊢ φ → 𝓢 ⊢ K φ
def ClosedUnderMP (𝓢 : S) (K : Fm → Fm) : Prop := ∀ φ ψ, 𝓢 ⊢ K (φ 🡒 ψ) 🡒 K φ 🡒 K ψ
def Factive (𝓢 : S) (K : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ K φ 🡒 φ
def KnowsItsFactivity (𝓢 : S) (K : Fm → Fm) : Prop := ∀ φ, 𝓢 ⊢ K (K φ 🡒 φ)
def HasGödelSentence (𝓑 : S₀) (F : Fm → Fm) : Prop := ∃ ψ, 𝓑 ⊢ ψ 🡘 ∼F ψ

variable {𝓑 : S₀} {𝓢 : S} [Entailment.Cl 𝓑] [Entailment.Cl 𝓢] {K F : Fm → Fm}

/-- one, two, three premises under K -/
lemma k1 (hn : KnowsTheoremsOf 𝓑 𝓢 K) (h2 : ClosedUnderMP 𝓢 K) {a c : Fm}
    (t : 𝓑 ⊢ a 🡒 c) (ha : 𝓢 ⊢ K a) : 𝓢 ⊢ K c := by
  have := h2 a c; have := hn _ t; cl_prover [this, h2 a c, ha]

lemma k2 (hn : KnowsTheoremsOf 𝓑 𝓢 K) (h2 : ClosedUnderMP 𝓢 K) {a b c : Fm}
    (t : 𝓑 ⊢ a 🡒 b 🡒 c) (ha : 𝓢 ⊢ K a) (hb : 𝓢 ⊢ K b) : 𝓢 ⊢ K c := by
  have h1 : 𝓢 ⊢ K (b 🡒 c) := k1 hn h2 t ha
  cl_prover [h1, h2 b c, hb]

lemma k3 (hn : KnowsTheoremsOf 𝓑 𝓢 K) (h2 : ClosedUnderMP 𝓢 K) {a b c d : Fm}
    (t : 𝓑 ⊢ a 🡒 b 🡒 c 🡒 d) (ha : 𝓢 ⊢ K a) (hb : 𝓢 ⊢ K b) (hc : 𝓢 ⊢ K c) : 𝓢 ⊢ K d := by
  have h1 : 𝓢 ⊢ K (c 🡒 d) := k2 hn h2 t ha hb
  cl_prover [h1, h2 c d, hc]

example (hn : KnowsTheoremsOf 𝓑 𝓢 K) (h2 : ClosedUnderMP 𝓢 K) (hg : HasGödelSentence 𝓑 F)
    (hs : ∀ φ, 𝓢 ⊢ K (F φ 🡒 φ)) : ∃ ψ, 𝓢 ⊢ K ψ ⋏ K (∼F ψ) := by
  obtain ⟨ψ, hψ⟩ := hg
  have kfix : 𝓢 ⊢ K (ψ 🡘 ∼F ψ) := hn _ hψ
  have a : 𝓢 ⊢ K (∼F ψ) := k2 hn h2 (a := ψ 🡘 ∼F ψ) (b := F ψ 🡒 ψ) (by cl_prover) kfix (hs ψ)
  have b : 𝓢 ⊢ K ψ := k2 hn h2 (a := ψ 🡘 ∼F ψ) (b := ∼F ψ) (by cl_prover) kfix a
  exact ⟨ψ, by cl_prover [a, b]⟩

-- Theorem 4 with proviso
example (hn : KnowsTheoremsOf 𝓑 𝓢 K) (h2 : ClosedUnderMP 𝓢 K) (hkf : KnowsItsFactivity 𝓢 K)
    (g2 : 𝓑 ⊢ F (∼F ⊥) 🡒 F ⊥) (hs : ∀ φ, 𝓢 ⊢ K (K φ 🡒 F φ)) : 𝓢 ⊢ K (∼K (∼F ⊥)) := by
  have kg2 : 𝓢 ⊢ K (F (∼F ⊥) 🡒 F ⊥) := hn _ g2
  exact k3 hn h2 (a := K (∼F ⊥) 🡒 F (∼F ⊥)) (b := F (∼F ⊥) 🡒 F ⊥) (c := K (∼F ⊥) 🡒 ∼F ⊥)
    (by cl_prover) (hs _) kg2 (hkf _)

-- pointwise SSMT
example (hn : KnowsTheoremsOf 𝓑 𝓢 K) (h2 : ClosedUnderMP 𝓢 K) (hf : Factive 𝓢 K) (hkf : KnowsItsFactivity 𝓢 K)
    (hg : HasGödelSentence 𝓑 F) (hs : ∀ φ, 𝓢 ⊢ K (K φ 🡘 F φ)) : 𝓢 ⊢ ⊥ := by
  obtain ⟨ψ, hψ⟩ := hg
  have kfix : 𝓢 ⊢ K (ψ 🡘 ∼F ψ) := hn _ hψ
  have a : 𝓢 ⊢ K (∼F ψ) := k3 hn h2 (a := ψ 🡘 ∼F ψ) (b := K ψ 🡘 F ψ) (c := K ψ 🡒 ψ) (by cl_prover)
    kfix (hs ψ) (hkf ψ)
  have b : 𝓢 ⊢ K ψ := k2 hn h2 (a := ψ 🡘 ∼F ψ) (b := ∼F ψ) (by cl_prover) kfix a
  have c : 𝓢 ⊢ K (∼K ψ) := k2 hn h2 (a := K ψ 🡘 F ψ) (b := ∼F ψ) (by cl_prover) (hs ψ) a
  cl_prover [b, c, hf (∼K ψ)]

-- diagonal core
example (hn : KnowsTheoremsOf 𝓑 𝓢 K) (h2 : ClosedUnderMP 𝓢 K) (hf : Factive 𝓢 K) (hkf : KnowsItsFactivity 𝓢 K)
    (p : Fm) : 𝓢 ⊢ ∼K (K (∼p) 🡘 p) := by
  have t : 𝓑 ⊢ (K (∼p) 🡘 p) 🡒 (K (∼p) 🡒 ∼p) 🡒 ∼p := by cl_prover
  have kt := hn _ t
  have := h2 (K (∼p) 🡘 p) ((K (∼p) 🡒 ∼p) 🡒 ∼p)
  have := h2 (K (∼p) 🡒 ∼p) (∼p)
  cl_prover [kt, h2 (K (∼p) 🡘 p) ((K (∼p) 🡒 ∼p) 🡒 ∼p), h2 (K (∼p) 🡒 ∼p) (∼p), hkf (∼p), hf (∼p), hf (K (∼p) 🡘 p)]
end

section nonvacuity
open FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

abbrev PAr : ArithmeticTheory := 𝗣𝗔 ∪ (𝗣𝗔 : ArithmeticTheory).localReflectionOn Set.univ
noncomputable abbrev PrPA : ArithmeticSentence → ArithmeticSentence := fun σ => (𝗣𝗔 : ArithmeticTheory).standardProvability σ

example : KnowsTheoremsOf (𝗜𝚺₁ : ArithmeticTheory) PAr id ∧ ClosedUnderMP PAr id ∧ Factive PAr id ∧
    KnowsItsFactivity PAr id ∧ HasGödelSentence (𝗜𝚺₁ : ArithmeticTheory) PrPA ∧
    (∀ φ, PAr ⊢ id (PrPA φ 🡒 φ)) ∧ Entailment.Consistent PAr := by
  have hle : (𝗜𝚺₁ : ArithmeticTheory) ⪯ PAr :=
    Entailment.WeakerThan.trans (inferInstance : (𝗜𝚺₁ : ArithmeticTheory) ⪯ 𝗣𝗔)
      (Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_left)
  refine ⟨fun φ h => hle.pbl h, fun φ ψ => by simp only [id]; cl_prover, fun φ => by simp only [id]; cl_prover,
    fun φ => by simp only [id]; cl_prover, ⟨gödel (𝗣𝗔 : ArithmeticTheory).standardProvability, gödel_spec⟩, ?_, ?_⟩
  · intro φ
    have : (𝗣𝗔 : ArithmeticTheory).standardProvability.refl φ ∈ PAr :=
      Set.mem_union_right _ ((Provability.mem_localReflectionOn_iff _).mpr ⟨φ, trivial, rfl⟩)
    exact Entailment.Axiomatized.by_axm this
  · have : ℕ↓[ℒₒᵣ] ⊧* PAr := models_localReflectionOn
    exact consistent_of_model PAr ℕ↓[ℒₒᵣ]

-- Theorem 4 witness: the degenerate system that proves everything
example : KnowsTheoremsOf (𝗣𝗔 : ArithmeticTheory) (𝗣𝗔 : ArithmeticTheory) id ∧ ClosedUnderMP (𝗣𝗔 : ArithmeticTheory) id ∧
    KnowsItsFactivity (𝗣𝗔 : ArithmeticTheory) id ∧
    ((𝗣𝗔 : ArithmeticTheory) ⊢ (fun _ : ArithmeticSentence => (⊤ : ArithmeticSentence)) (∼(⊤ : ArithmeticSentence)) 🡒 ⊤) ∧
    (∀ φ : ArithmeticSentence, (𝗣𝗔 : ArithmeticTheory) ⊢ id (id φ 🡒 (⊤ : ArithmeticSentence))) ∧
    Entailment.Consistent (𝗣𝗔 : ArithmeticTheory) := by
  refine ⟨fun φ h => h, fun φ ψ => by simp only [id]; cl_prover, fun φ => by simp only [id]; cl_prover,
    by cl_prover, fun φ => by simp only [id]; cl_prover, inferInstance⟩
end nonvacuity
end GodelArgument.Sketch2
