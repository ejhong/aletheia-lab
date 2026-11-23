module

public meta import Lean

/-!
# Axiom audit

`#assert_standard_axioms foo bar` fails the build unless `foo` and `bar` depend on nothing beyond Lean's three
standard axioms. `sorry`, `admit` and `native_decide` all show up here as extra axioms, so this one check covers
them.
-/

public meta section

open Lean Elab Command

/-- Fail unless every listed declaration depends only on `propext`, `Classical.choice` and `Quot.sound`. -/
elab "#assert_standard_axioms " ids:ident+ : command => do
  let allowed : List Name := [``propext, ``Classical.choice, ``Quot.sound]
  for id in ids do
    let name ← liftCoreM <| realizeGlobalConstNoOverloadWithInfo id
    let axioms ← liftCoreM <| collectAxioms name
    let extra := axioms.toList.filter (fun a => !allowed.contains a)
    unless extra.isEmpty do
      throwErrorAt id "{name} depends on axioms outside the standard three: {extra}"
    logInfoAt id m!"{name}: standard axioms only"

end
