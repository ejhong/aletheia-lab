module

public import PowerSeeking.Statement
public import PowerSeeking.Coherence
public import PowerSeeking.PowerSeeking
public import PowerSeeking.Shutdown
import PowerSeeking.Audit

/-!
# Power-seeking, coherence, and the shutdown problem (#67)

Root module importing all three proof families and auditing every headline theorem inside the build
to verify that each depends solely on Lean's three standard axioms (`propext`, `Classical.choice`,
`Quot.sound`).
-/

#assert_standard_axioms
  PowerSeeking.theorem_S1a_VNMRepresentation
  PowerSeeking.theorem_S1b_IntransitiveMoneyPump
  PowerSeeking.theorem_S1c_IncompleteNoMoneyPump
  PowerSeeking.theorem_S1d_HistoryUtilityTriviality
  PowerSeeking.theorem_S2a_SimpleRetargetability
  PowerSeeking.theorem_S2b_MultiplyRetargetable
  PowerSeeking.theorem_S2c_OptimalPolicyPowerSeeking
  PowerSeeking.theorem_S2d_CounterexampleDropSymmetry
  PowerSeeking.theorem_S2e_CounterexampleDropOptimality
  PowerSeeking.theorem_S2f_CounterexampleDominatedOptions
  PowerSeeking.theorem_S3a_ShutdownManipulationDichotomy
  PowerSeeking.theorem_S3b_ShutdownIndifferenceCorrigibility
  PowerSeeking.theorem_S3c_TransitiveIndifferenceImpossibility
  PowerSeeking.theorem_S3d_IncompletePreferencesEscape
