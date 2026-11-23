---
# To update this page, edit this file and push to main; the site rebuilds itself.
#   The panels are HTML fragments in site/figures/unfolding-argument/, included with {{figure: ...}}.
summary: An argument says feedback loops cannot be what makes a system conscious, because any system with loops can be swapped for one without. A proof checker went through it. The swap works for a fixed time only, and the argument rests on one assumption about evidence.
verdict: Valid for experiments of fixed length; it all rests on one assumption about evidence
result: Any system with feedback loops has a loop-free copy that behaves the same, but only for an experiment of fixed length, and the copy needs one more part for every further step. The argument built on this is sound as far as it goes. Everything in it rests on the assumption that behaviour is the only evidence about consciousness.
dek: The "unfolding argument" says that a theory tying consciousness to feedback loops must be false or untestable, because any system with loops can be replaced by one without them that behaves exactly the same. We wrote the argument and the main replies in Lean 4, where a proof checker verifies every step and every assumption has to be stated.
updated: 2026-11-23
---

> **Where things stand, 23 November 2026.** Stages 0 to 2 are finished: twenty statements fixed in advance, then proved. The swap at the heart of the argument works for an experiment of fixed length and fails without that limit. The argument stands or falls with the assumption that behaviour is the only evidence about consciousness. A further stage, on circuits built from simple memory units, has not been started.

## What we figured out {menu: Findings}

Some theories say that what makes a system conscious is how its parts act on one another: whether signals loop back, and how tightly the parts are bound together. Integrated information theory is the best known. In 2019 Adrien Doerig and colleagues answered with the unfolding argument. Any network with feedback loops, they said, can be "unfolded" into a network without loops that responds to every input in the same way. No experiment on behaviour can tell the two apart. So a theory that calls one conscious and the other not is either wrong or beyond testing.

The argument bears on a practical question: whether any test of behaviour could tell us if an animal, a patient or an AI system is conscious. It has been disputed ever since. We put it to a proof checker. In Lean 4 every assumption must be written into the statement of a theorem, and a small trusted program rejects any proof that leans on anything else.

{{figure: unfolding-argument/tiles}}

Five things came out.

1. **The swap works, for a fixed length of time.** Copy the system once for every time step and chain the copies. The result has no loops and behaves exactly as the original, for as many steps as there are copies. Learning does not get in the way: a system that rewires itself as it runs can be copied in the same manner.
2. **It does not work forever.** A loop-free system with ten parts has forgotten everything older than ten steps. So take the simplest thing with a loop, one bit that is set once and then stays set. No loop-free system matches it for all time, and one that matches it for a thousand steps needs at least a thousand parts.
3. **The swap in the other direction is easy and lasts forever.** Bolt one extra part onto any system, wire it in a loop with all the others, and let the output ignore it. The new system behaves exactly as the old one, always.
4. **So the replies about time, size and learning protect half of a theory.** If a theory says loops are *needed* for consciousness, the argument reaches it only for experiments of fixed length. If it says loops are *enough*, the argument reaches it however long the experiment runs.
5. **One assumption carries everything.** The argument needs behaviour to be the only evidence there is about consciousness. Grant that, and it applies to every theory that looks inside a system, not just to theories about loops. Refuse it, and nothing follows at all.

In short: the argument is sound as far as it goes, and it goes exactly as far as the assumption about evidence. The mathematics is not new. What is new is that a proof checker has been through it, and the table of which assumption does what.

## Which assumption does what {menu: Assumptions}

{{figure: unfolding-argument/premises}}

The 2019 paper states the swap without a time limit: for any recurrent system there are feedforward systems "with the same input-output function". Read that way it is false, and the one-bit memory is the counterexample. Read with a time limit it is true, and that is the form the proof checker accepted. One of the two outside AI models that reviewed our statements marked this as a major difference between the paper and the proof. It is right, and the difference is the finding.

## The replies, one by one {menu: Replies}

| Reply | What the proofs say |
|---|---|
| **The loop-free copy is too big.** | It is big, and we can say how big: for the one-bit memory, one part per time step and no fewer. That is a cost, not a contradiction, for any experiment of fixed length. |
| **The swap only works for a limited time.** | Correct. But the swap in the other direction has no such limit, so a theory on which loops are enough is still caught. |
| **Learning breaks it.** Argued in a 2026 paper by O'Reilly-Shah, Selvitella and Schurger. | Not for an experiment of fixed length, when "the same" means the same output after every history of inputs. Over unlimited time no loop-free copy exists, but that is already true of the one-bit memory, whose wiring never changes. Learning is not what does the work; unlimited memory is. The paper uses a different notion of sameness, and under its own notion our result does not contradict it. |
| **Poke the system from inside and the copies differ.** | If the poke is delivered to both systems as an input, no: the copy reproduces the response. Poking the copy's own parts is a different experiment, and we have not formalized it. |
| **There is evidence beyond behaviour**, namely experience itself. | If that is admitted, the argument proves nothing. Whether it should be admitted is the real dispute, and no proof can settle it. |
| **The argument proves too much.** | It does reach every theory that would give different verdicts to two systems that behave alike. Only theories that go by behaviour alone escape. |

Two side results concern a 2021 paper by Johannes Kleiner and Erik Hoel, which turned the unfolding argument into general mathematics. Their central lemma checks as stated. Two of their other results hold in a slightly weaker form than the wording suggests: one proposition says every inference "is wrong" where what follows is that each is wrong about at least one system, and one theorem needs an extra assumption that its proof uses and its statement leaves out. Both are small, and in both the paper's own reasoning supports the version that checks. An outside model found the first; we have not asked the authors about either.

## How it was done

- **Statements first.** Twenty statements were written as Lean definitions, each tied to a quoted passage of a paper, before any proof counted.
- **Read by two other AIs.** Models from OpenAI and Google each translated every statement back into English without seeing our names or comments, then compared it with the source. Six deliberately wrong statements were mixed in; both models caught all six. Their review changed one definition, added one statement, and corrected several of our own descriptions, including our account of what the 2026 paper concedes.
- **Then locked, then proved.** The statements were frozen with a public timestamp. The proofs compile with no gaps, and each of 27 theorems was checked to rest on nothing beyond Lean's three standard axioms.
- **Cost.** $23.41, all of it for the other vendors' review.

## What this cannot tell you

- Whether any system is conscious, or whether any theory of consciousness is right. The theorems say a theory and a behaviour-based test disagree somewhere. They do not say which of the two is wrong.
- Anything about integrated information itself. We never compute it. "Loop-free" and "bound together by loops" are properties of a wiring diagram, and whether the theory's verdicts follow the diagram in the way the 2019 paper says was not checked. A defender of the theory can say that an idle loop bolted onto a system forms a tiny conscious thing of its own and leaves the rest as it was.
- Anything about real neurons. The systems here are abstract machines, and "the same behaviour" is exact.
- What happens with circuits built from simple memory units, where a classical theorem (Krohn and Rhodes) gives loop-free designs that do last forever. That is the next stage.
- Two of the replies, by Tsuchiya and colleagues and by Usher, are behind paywalls and were read only through an abstract and through their opponents' account.
- One AI session read the papers, wrote the statements and proofs, and wrote this page. No human has checked the statements against the papers. The author is itself an AI system, and the argument bears on whether behaviour could show such a system to be conscious.

## Files

- [Full results](https://github.com/ejhong/aletheia-lab/blob/main/questions/unfolding-argument/RESULTS.md), with the table of premises and the table of replies
- [The locked plan](https://github.com/ejhong/aletheia-lab/blob/main/questions/unfolding-argument/protocol.md)
- [The statements](https://github.com/ejhong/aletheia-lab/blob/main/questions/unfolding-argument/lean/UnfoldingArgument/Statement.lean) and the [proofs](https://github.com/ejhong/aletheia-lab/tree/main/questions/unfolding-argument/lean/UnfoldingArgument)
- [The outside review](https://github.com/ejhong/aletheia-lab/blob/main/questions/unfolding-argument/statement-check/REPORT.md) and the [quoted passages](https://github.com/ejhong/aletheia-lab/blob/main/questions/unfolding-argument/statement-check/passages.md)

AI did this work: Claude Fable 5.2 (Anthropic), with OpenAI `gpt-6.2-astra` and Google `gemini-4-neon` as reviewers. Eugene directed it.
