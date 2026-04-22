# Sovereign Intel System

## Overview
The Sovereign Intelligence System (GIGACPO) is an automated, institutional-grade market surveillance application specifically hardwired for Silicon Photonics (SiPh), Co-Packaged Optics (CPO), and advanced packaging supply chains, overlaid against Global Macro data.

## Core Directives
1. **Total Local Resilience:** The system relies entirely on offline Natural Language Processing capabilities (VADER, LSA, TF-IDF). No LLM tokens or external AI endpoints are required to generate the daily executive narrative.
2. **Signal over Noise:** Employs multi-layer filtration. First, RSS feeds are strictly blacklisted from Jim Cramer, Motley Fool, etc. Second, 48-hour TTL is enforced. Third, Ticker detection algorithms isolate legitimate financial calls from common terms (e.g., stopping `$ARM` from "arming").
3. **Universal Session Fidelity (V23.86):** Employs **Time-Anchored Windowing** to force-prioritize data fields by clock hour, bypassing stale Yahoo state reporting. Enforces **Atomic Overrides** to ensure price and percentage always represent the same session state.
4. **Diagnostic Transparency (V23.86):** High-fidelity work logs provide real-time status of cache TTLs, fetch batches, and NLP ranking decisions.

## The Pipeline
- **Trigger:** System invoked manually or via Windows Scheduler.
- **Dependency Guardian:** Intercepts and auto-installs missing packages without stalling.
- **Price Engine:** Scrapes Yahoo JSON arrays using time-anchored windowing and bid/ask midpoint fallbacks for low-liquidity extended hours.
- **Aggregator:** Collects global news and economic indicators, automatically mapping indices to Futures (`ES=F`) during extended hours.
- **Synthesizer:** LSA and TF-IDF merge the narrative, injecting session-aware price flairs into headlines.
- **Dispatch:** Email Synopsis formats into a 102KB minified HTML payload with atomic session rendering.

This enables a living, automated ecosystem providing institutional insights 24/7.
