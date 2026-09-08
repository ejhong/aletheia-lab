#!/usr/bin/env node
import fs from "node:fs";
import { prepareCaseExperiment, runCaseExperimentRound } from "./lib/case-experiment.ts";

const [command, first, second, approvalFile, ...extra] = process.argv.slice(2);
if (extra.length || !first || !second) throw new Error("Usage: experiment-case.ts prepare <case> <experiment-id> | run <experiment-id> <1|2> <authorization-text-file>");
if (command === "prepare" && !approvalFile) {
  console.log(JSON.stringify(prepareCaseExperiment(process.cwd(), first, second), null, 2));
} else if (command === "run" && approvalFile) {
  console.log(JSON.stringify(await runCaseExperimentRound(process.cwd(), first, Number(second), fs.readFileSync(approvalFile, "utf8")), null, 2));
} else throw new Error("Unknown experiment command; prepare is free, run requires a recorded authorization and an available live allowance");
