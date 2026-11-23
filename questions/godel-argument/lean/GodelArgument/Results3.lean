import GodelArgument.Statement3
import GodelArgument.Results2

/-!
# Results for the statements taken from Reinhardt (1985) (Amendment 3)

Each theorem has exactly the type of a statement in `Statement3.lean`. Both are derivations in classical
propositional logic from the stated hypotheses about `K`.
-/

namespace GodelArgument

open FFL

/-- S2f. Follows Reinhardt's proof (pp. 329–330), carried out under `K` throughout. From the fixed point,
`s → K s` is known (this is where K4 enters). Then `Con F → ¬s` is known, since `s` would put both `s` and `¬s`
in `F`. Hence `K(Con F) → K¬s`, and `K(Con F) → F(¬s)`, are known; with K4 again, `K(Con F) → s`. Known factivity
gives `K(Con F) → ¬s`. So `¬K(Con F)`, and all of it under `K`. Plain factivity is not used. -/
theorem reinhardtTheorem6 : ReinhardtTheorem6 := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K F c hn h2b h4b hle hkf ⟨s, hs⟩ hc hu
  have h2 : KnowledgeClosedUnderMP 𝓢 K := fun φ ψ => hle.pbl (h2b φ ψ)
  -- lifting a known implication: from K (x → y) to K (K x → K y)
  have lift : ∀ x y : Fm, 𝓢 ⊢ K (x 🡒 y) → 𝓢 ⊢ K (K x 🡒 K y) := by
    intro x y h
    have h4 : 𝓢 ⊢ K (x 🡒 y) 🡒 K (K (x 🡒 y)) := hle.pbl (h4b _)
    have kk : 𝓢 ⊢ K (K (x 🡒 y)) := by cl_prover [h, h4]
    exact known_mp h2 (known_of_base hn hle (h2b x y)) kk
  -- the two halves of the fixed point, known
  have f1 : 𝓢 ⊢ K (s 🡒 K (F (∼s))) :=
    known_mp h2 (known_of_base hn hle (by cl_prover : 𝓑 ⊢ (s 🡘 K (F (∼s))) 🡒 (s 🡒 K (F (∼s))))) hs
  have f2 : 𝓢 ⊢ K (K (F (∼s)) 🡒 s) :=
    known_mp h2 (known_of_base hn hle (by cl_prover : 𝓑 ⊢ (s 🡘 K (F (∼s))) 🡒 (K (F (∼s)) 🡒 s))) hs
  -- known: s → K s
  have ta : 𝓑 ⊢ (s 🡒 K (F (∼s))) 🡒 (K (F (∼s)) 🡒 K (K (F (∼s)))) 🡒 (K (K (F (∼s))) 🡒 K s) 🡒 (s 🡒 K s) := by
    cl_prover
  have a : 𝓢 ⊢ K (s 🡒 K s) :=
    known_of_three hn hle h2 ta f1 (known_of_base hn hle (h4b (F (∼s)))) (lift _ _ f2)
  -- (1) K (c → ¬s)
  have t1 : 𝓑 ⊢ (s 🡒 K s) 🡒 (K s 🡒 F s) 🡒 (s 🡒 K (F (∼s))) 🡒 (K (F (∼s)) 🡒 F (∼s)) 🡒
      (c 🡒 ∼(F s ⋏ F (∼s))) 🡒 (c 🡒 ∼s) := by cl_prover 64
  have k1 : 𝓢 ⊢ K (c 🡒 ∼s) :=
    known_mp h2 (known_mp h2 (known_mp h2 (known_mp h2 (known_mp h2 (known_of_base hn hle t1) a) (hu s)) f1)
      (hkf (F (∼s)))) (known_of_base hn hle (hc s))
  -- (2) K (K c → K ¬s), (3) K (K c → F ¬s), (4) K (K K c → K F ¬s)
  have k2 : 𝓢 ⊢ K (K c 🡒 K (∼s)) := lift _ _ k1
  have t3 : 𝓑 ⊢ (K c 🡒 K (∼s)) 🡒 (K (∼s) 🡒 F (∼s)) 🡒 (K c 🡒 F (∼s)) := by cl_prover
  have k3 : 𝓢 ⊢ K (K c 🡒 F (∼s)) := known_of_two hn hle h2 t3 k2 (hu (∼s))
  have k4 : 𝓢 ⊢ K (K (K c) 🡒 K (F (∼s))) := lift _ _ k3
  have t5 : 𝓑 ⊢ (K c 🡒 K (K c)) 🡒 (K (K c) 🡒 K (F (∼s))) 🡒 (K (F (∼s)) 🡒 s) 🡒 (K c 🡒 K (∼s)) 🡒
      (K (∼s) 🡒 ∼s) 🡒 ∼K c := by cl_prover 64
  exact known_mp h2 (known_mp h2 (known_mp h2 (known_mp h2 (known_mp h2 (known_of_base hn hle t5)
    (known_of_base hn hle (h4b c))) k4) f2) k2) (hkf (∼s))

/-- S2g. Known factivity turns `K(F(φ) → Kφ)` into `K(F(φ) → φ)`; then S2a. -/
theorem reinhardtTheorem1Safe : ReinhardtTheorem1Safe := by
  intro Fm S₀ S _ _ _ _ 𝓑 𝓢 _ _ K F hn hle h2 hkf hg hs
  refine reinhardtTheorem3 Fm S₀ S 𝓑 𝓢 K F hn hle h2 hg (fun φ => ?_)
  have t : 𝓑 ⊢ (F φ 🡒 K φ) 🡒 (K φ 🡒 φ) 🡒 (F φ 🡒 φ) := by cl_prover
  exact known_of_two hn hle h2 t (hs φ) (hkf φ)
#assert_standard_axioms reinhardtTheorem6 reinhardtTheorem1Safe

end GodelArgument
