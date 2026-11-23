import GodelArgumentDraft5
import GodelArgument.Results2
/-! Exploratory only. A trial of proofs for the draft statements of Amendment 5 (tier 2C), compiled before the
lock against a copy of `statement-check/Statement5.draft.lean`, to make sure no draft statement is false as
written. Not a finding. -/
namespace GodelArgument
open FFL

example : PenroseArgumentValid := by
  intro Fm S _ _ _ 𝓢 _ T K σ S₀ S' G P Q hTin hK b1 b2 b3 b4 b6 b7
  have l3 : 𝓢 ⊢ σ 🡒 G := by cl_prover [hTin, b1, b2, b3]
  have l5 : 𝓢 ⊢ K (σ 🡒 G) := hK _ l3
  cl_prover [hTin, b1, b2, b4, b6, b7, l5]

example : UnrestrictedTInInconsistent := by
  intro Fm S _ _ _ 𝓢 _ T hin hout ⟨lam, hl⟩
  cl_prover [hin lam, hout lam, hl]

example : UnrestrictedKIntroInconsistent := by
  intro Fm S _ _ _ 𝓢 _ T K hK hkt hout ⟨kap, hk⟩
  have h1 : 𝓢 ⊢ kap := by cl_prover [hkt kap, hout kap, hk]
  have h2 : 𝓢 ⊢ K kap := hK _ h1
  cl_prover [h1, h2, hk]

example : KnownValiditiesInconsistent := by
  intro Fm S _ _ _ 𝓢 _ T K lam hl h1 h2 h3 h4
  cl_prover [hl, h1, h2, h3, h4]

example : PenroseArgumentUnderDeterminateness := by
  intro Fm S _ _ _ 𝓢 _ T K D σ S₀ S' G P Q hdt hdk hdi hdK d2 d5 b1 b2 b3 b4 b6 b7
  have dσ : 𝓢 ⊢ D σ := by cl_prover [hdi σ S', d2]
  have dσG : 𝓢 ⊢ D (σ 🡒 G) := by cl_prover [hdK (σ 🡒 G), d5]
  have hTin : 𝓢 ⊢ σ 🡒 T σ := by cl_prover [hdt σ, dσ]
  have l3 : 𝓢 ⊢ σ 🡒 G := by cl_prover [hTin, b1, b2, b3]
  have l5 : 𝓢 ⊢ K (σ 🡒 G) := hdk _ l3 dσG
  cl_prover [hTin, b1, b2, b4, b6, b7, l5]

example : StepsIndeterminateIfThesisIs := by
  intro Fm S _ _ _ 𝓢 _ T K D σ X G hdi hdk hn
  cl_prover [hdi σ X, hdi σ G, hdk (σ 🡒 G), hn]

example : RestrictedThesisGivesUnprovableKnowledge := by
  intro Fm S _ _ _ 𝓢 _ T K D σ S₀ S' G P Q hdt hdk dσ dσG b1 b2 b3 b4 b6
  have hTin : 𝓢 ⊢ σ 🡒 T σ := by cl_prover [hdt σ, dσ]
  have l3 : 𝓢 ⊢ σ 🡒 G := by cl_prover [hTin, b1, b2, b3]
  have l5 : 𝓢 ⊢ K (σ 🡒 G) := hdk _ l3 dσG
  cl_prover [hTin, b1, b2, b4, b6, l5]
end GodelArgument
