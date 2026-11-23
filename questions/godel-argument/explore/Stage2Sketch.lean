import GodelArgumentDraft2
import Foundation.FirstOrder.Incompleteness.Löb
/-! Exploratory only: checks that the draft Stage 2A statements are provable as written. Not a finding.
Compile with the draft statement file copied to `lean/GodelArgumentDraft2.lean` (not committed there). -/
namespace GodelArgument
open FFL

section
variable {Fm S₀ S : Type} [LogicalConnective Fm] [LogicalNeutral Fm] [Entailment S₀ Fm] [Entailment S Fm]
variable {𝓑 : S₀} {𝓢 : S} [Entailment.Cl 𝓑] [Entailment.Cl 𝓢] {K F : Fm → Fm}

lemma nec (hn : ClosedUnderNecessitation 𝓑 K) (hle : 𝓑 ⪯ 𝓢) {φ : Fm} (h : 𝓑 ⊢ φ) : 𝓢 ⊢ K φ := hle.pbl (hn φ h)

omit [Entailment.Cl 𝓑] in
lemma k1 (h2 : KnowledgeClosedUnderMP 𝓢 K) {a c : Fm} (t : 𝓢 ⊢ K (a 🡒 c)) (ha : 𝓢 ⊢ K a) : 𝓢 ⊢ K c := by
  cl_prover [t, h2 a c, ha]

lemma k2 (hn : ClosedUnderNecessitation 𝓑 K) (hle : 𝓑 ⪯ 𝓢) (h2 : KnowledgeClosedUnderMP 𝓢 K) {a b c : Fm}
    (t : 𝓑 ⊢ a 🡒 b 🡒 c) (ha : 𝓢 ⊢ K a) (hb : 𝓢 ⊢ K b) : 𝓢 ⊢ K c :=
  k1 h2 (k1 h2 (nec hn hle t) ha) hb

lemma k3 (hn : ClosedUnderNecessitation 𝓑 K) (hle : 𝓑 ⪯ 𝓢) (h2 : KnowledgeClosedUnderMP 𝓢 K) {a b c d : Fm}
    (t : 𝓑 ⊢ a 🡒 b 🡒 c 🡒 d) (ha : 𝓢 ⊢ K a) (hb : 𝓢 ⊢ K b) (hc : 𝓢 ⊢ K c) : 𝓢 ⊢ K d :=
  k1 h2 (k2 hn hle h2 t ha hb) hc
end

lemma t3 : ReinhardtTheorem3 := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K F hn hle h2 ⟨ψ, hψ⟩ hs
  have kfix : 𝓢 ⊢ K (ψ 🡘 ∼F ψ) := nec hn hle hψ
  have a : 𝓢 ⊢ K (∼F ψ) := k2 hn hle h2 (a := ψ 🡘 ∼F ψ) (b := F ψ 🡒 ψ) (by cl_prover) kfix (hs ψ)
  have b : 𝓢 ⊢ K ψ := k2 hn hle h2 (a := ψ 🡘 ∼F ψ) (b := ∼F ψ) (by cl_prover) kfix a
  exact ⟨ψ, by cl_prover [a, b]⟩

example : KnowerExceedsKnownSoundSystem := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K F hn hle h2 hf hg hs
  obtain ⟨ψ, h⟩ := t3 Fm S₀ S 𝓑 𝓢 K F hn hle h2 hg hs
  exact ⟨ψ, by cl_prover [h, hf (∼F ψ)]⟩

example : AbsoluteSecondIncompleteness := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K F hn hle h2 hkf g2 hs
  exact k3 hn hle h2 (a := K (∼F ⊥) 🡒 F (∼F ⊥)) (b := F (∼F ⊥) 🡒 F ⊥) (c := K (∼F ⊥) 🡒 ∼F ⊥)
    (by cl_prover) (hs _) (nec hn hle g2) (hkf _)

example : KnowingWhichSystemIsContradictory := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K F hn hle h2 hf hkf ⟨ψ, hψ⟩ hs
  have kfix : 𝓢 ⊢ K (ψ 🡘 ∼F ψ) := nec hn hle hψ
  have a : 𝓢 ⊢ K (∼F ψ) := k3 hn hle h2 (a := ψ 🡘 ∼F ψ) (b := K ψ 🡘 F ψ) (c := K ψ 🡒 ψ) (by cl_prover)
    kfix (hs ψ) (hkf ψ)
  have b : 𝓢 ⊢ K ψ := k2 hn hle h2 (a := ψ 🡘 ∼F ψ) (b := ∼F ψ) (by cl_prover) kfix a
  have c : 𝓢 ⊢ K (∼K ψ) := k2 hn hle h2 (a := K ψ 🡘 F ψ) (b := ∼F ψ) (by cl_prover) (hs ψ) a
  cl_prover [b, c, hf (∼K ψ)]

example : NoKnownSelfDiagonal := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K hn hle h2 hf hkf p
  have t : 𝓑 ⊢ (K (∼p) 🡘 p) 🡒 (K (∼p) 🡒 ∼p) 🡒 ∼p := by cl_prover
  cl_prover [nec hn hle t, h2 (K (∼p) 🡘 p) ((K (∼p) 🡒 ∼p) 🡒 ∼p), h2 (K (∼p) 🡒 ∼p) (∼p), hkf (∼p), hf (∼p),
    hf (K (∼p) 🡘 p)]

section arithmetic
open FFL.FirstOrder FFL.FirstOrder.Arithmetic FFL.FirstOrder.ProvabilityAbstraction

example : SecondIncompletenessProvisoCannotBeDropped := by
  refine ⟨𝗣𝗔, id, id, fun φ h => h, inferInstance, fun φ ψ => by simp only [id]; cl_prover,
    fun φ => by simp only [id]; cl_prover, fun φ => by simp only [id]; cl_prover,
    fun φ => by simp only [id]; cl_prover, ?_⟩
  intro h
  have hb : (𝗣𝗔 : ArithmeticTheory) ⊢ ⊥ := by simp only [id] at h; cl_prover [h]
  exact Entailment.not_consistent_iff_inconsistent.mpr (Entailment.inconsistent_iff_provable_bot.mpr hb) inferInstance

noncomputable abbrev PrPA : ArithmeticSentence → ArithmeticSentence := fun σ => (𝗣𝗔 : ArithmeticTheory).standardProvability σ
abbrev PAr : ArithmeticTheory := 𝗣𝗔 ∪ (𝗣𝗔 : ArithmeticTheory).localReflectionOn Set.univ

example : KnownFactivityCannotBeDropped := by
  have hPA : (𝗣𝗔 : ArithmeticTheory) ⪯ PAr := Entailment.Axiomatized.weakerThanOfSubset Set.subset_union_left
  have hI : (𝗜𝚺₁ : ArithmeticTheory) ⪯ PAr := Entailment.WeakerThan.trans (inferInstance : (𝗜𝚺₁ : ArithmeticTheory) ⪯ 𝗣𝗔) hPA
  have d1 : ∀ {σ : ArithmeticSentence}, (𝗣𝗔 : ArithmeticTheory) ⊢ σ → (𝗣𝗔 : ArithmeticTheory) ⊢ PrPA σ :=
    fun h => Entailment.WeakerThan.pbl (𝓢 := (𝗜𝚺₁ : ArithmeticTheory)) (Provability.D1 h)
  obtain ⟨G, hG⟩ : ∃ G : ArithmeticSentence, (𝗣𝗔 : ArithmeticTheory) ⊢ G 🡘 ∼PrPA G :=
    ⟨gödel (𝗣𝗔 : ArithmeticTheory).standardProvability,
      Entailment.WeakerThan.pbl (𝓢 := (𝗜𝚺₁ : ArithmeticTheory)) gödel_spec⟩
  have flip : ∀ a b : ArithmeticSentence, (𝗣𝗔 : ArithmeticTheory) ⊢ a 🡘 ∼b → (𝗣𝗔 : ArithmeticTheory) ⊢ b 🡘 ∼a :=
    fun a b h => by cl_prover [h]
  refine ⟨PAr, PrPA, PrPA, fun φ h => d1 h, hPA, fun φ ψ => hI.pbl Provability.D2, ?_, ⟨G, hG⟩, ?_, ⟨∼G, ?_⟩, ?_⟩
  · intro φ
    have : (𝗣𝗔 : ArithmeticTheory).standardProvability.refl φ ∈ PAr :=
      Set.mem_union_right _ ((Provability.mem_localReflectionOn_iff _).mpr ⟨φ, trivial, rfl⟩)
    exact Entailment.Axiomatized.by_axm this
  · intro φ
    have taut : ∀ a : ArithmeticSentence, (𝗣𝗔 : ArithmeticTheory) ⊢ a 🡘 a := fun a => by cl_prover
    have key : ∀ a : ArithmeticSentence, PAr ⊢ PrPA (a 🡘 a) := fun a => hPA.pbl (d1 (taut a))
    exact key (PrPA φ)
  · have e : (∼∼G : ArithmeticSentence) = G := by simp
    have : (𝗣𝗔 : ArithmeticTheory) ⊢ PrPA (∼∼G) 🡘 ∼G := by rw [e]; exact flip _ _ hG
    exact hPA.pbl (d1 this)
  · have : ℕ↓[ℒₒᵣ] ⊧* PAr := models_localReflectionOn
    exact consistent_of_model PAr ℕ↓[ℒₒᵣ]
end arithmetic
end GodelArgument
