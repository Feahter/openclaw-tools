#!/usr/bin/env node

function usage() {
  console.error(`Usage: search.mjs "query" [-n 5] [--deep] [--topic general|news] [--days 7]`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const query = args[0];
let n = 5;
let searchDepth = "basic";
let topic = "general";
let days = null;

for (let i = 1; i < args.length; i++) {
  const a = args[i];
  if (a === "-n") {
    n = Number.parseInt(args[i + 1] ?? "5", 10);
    i++;
    continue;
  }
  if (a === "--deep") {
    searchDepth = "advanced";
    continue;
  }
  if (a === "--topic") {
    topic = args[i + 1] ?? "general";
    i++;
    continue;
  }
  if (a === "--days") {
    days = Number.parseInt(args[i + 1] ?? "7", 10);
    i++;
    continue;
  }
  console.error(`Unknown arg: ${a}`);
  usage();
}

import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import { join } from "path";

function getApiKey() {
  // 先从环境变量读取
  let apiKey = (process.env.TAVILY_API_KEY ?? "").trim();
  if (apiKey) return apiKey;
  
  // 从 credentials 文件读取
  const credPath = join(homedir(), ".openclaw", "credentials", "tavily.json");
  if (existsSync(credPath)) {
    try {
      const cred = JSON.parse(readFileSync(credPath, "utf-8"));
      apiKey = cred.tavily ?? cred.apiKey ?? cred.key ?? "";
      if (apiKey) return apiKey;
    } catch (e) {
      // 忽略解析错误
    }
  }
  
  console.error("Missing TAVILY_API_KEY");
  process.exit(1);
}

const apiKey = getApiKey();

const body = {
  api_key: apiKey,
  query: query,
  search_depth: searchDepth,
  topic: topic,
  max_results: Math.max(1, Math.min(n, 20)),
  include_answer: true,
  include_raw_content: false,
};

if (topic === "news" && days) {
  body.days = days;
}

const resp = await fetch("https://api.tavily.com/search", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(body),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  throw new Error(`Tavily Search failed (${resp.status}): ${text}`);
}

const data = await resp.json();

// Print AI-generated answer if available
if (data.answer) {
  console.log("## Answer\n");
  console.log(data.answer);
  console.log("\n---\n");
}

// Print results
const results = (data.results ?? []).slice(0, n);
console.log("## Sources\n");

for (const r of results) {
  const title = String(r?.title ?? "").trim();
  const url = String(r?.url ?? "").trim();
  const content = String(r?.content ?? "").trim();
  const score = r?.score ? ` (relevance: ${(r.score * 100).toFixed(0)}%)` : "";
  
  if (!title || !url) continue;
  console.log(`- **${title}**${score}`);
  console.log(`  ${url}`);
  if (content) {
    console.log(`  ${content.slice(0, 300)}${content.length > 300 ? "..." : ""}`);
  }
  console.log();
}
