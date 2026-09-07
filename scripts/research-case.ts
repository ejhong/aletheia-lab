#!/usr/bin/env node
import { parseArgs } from "node:util";
import { researchCase } from "./lib/case-research.ts";

const { values, positionals } = parseArgs({ options: {
  prepare: { type: "boolean", default: false }, reconsider: { type: "string" },
}, allowPositionals: true, strict: true });
if (positionals.length !== 1)
  throw new Error('Usage: node scripts/research-case.ts <case> [--prepare] [--reconsider "what warrants another report"]');
const key = positionals[0];
console.log(values.prepare
  ? `Preparing the complete research brief for ${key}; no model call or spending reservation.`
  : `Commissioning a web investigation of ${key}; the report is working material, not a published finding.`);
const result = await researchCase(process.cwd(), key, values);
console.log(JSON.stringify(result, null, 2));
if (result.outcome === "failed") process.exitCode = 1;
