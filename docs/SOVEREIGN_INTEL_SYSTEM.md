# Sovereign Intel System

## Overview
The Sovereign Intelligence System (GIGACPO) is an automated, institutional-grade market surveillance application specifically hardwired for Silicon Photonics (SiPh), Co-Packaged Optics (CPO), and advanced packaging supply chains, overlaid against Global Macro data.

## Core Directives
1. **Total Local Resilience:** The system relies entirely on offline Natural Language Processing capabilities (VADER, LSA, TF-IDF). No LLM tokens or external AI endpoints are required to generate the daily executive narrative.
2. **Signal over Noise:** Employs multi-layer filtration. First, RSS feeds are strictly blacklisted from Jim Cramer, Motley Fool, etc. Second, 48-hour TTL is enforced. Third, Ticker detection algorithms isolate legitimate financial calls from common terms (e.g., stopping `$ARM` from "arming").
3. **Session High-Fidelity:** Automatically aligns to the exact market state (Pre-Market, Live, After-Hours, or Overnight/Sunday) and ensures all displayed intelligence reflects the appropriate real-time proxy (including Blue Ocean ATS hidden data).

## The Pipeline
- **Trigger:** System invoked manually or via Windows Scheduler.
- **Dependency Guardian:** Intercepts and auto-installs missing packages without stalling.
- **Price Engine:** Scrapes Yahoo JSON arrays for immediate, lightweight quotes utilizing a 15-minute global TTL bypass.
- **Aggregator:** Collects global news and economic indicators spanning multiple Yahoo RSS feeds (Economic, Analysis, Stock Market), scoring articles based on urgency and relevance.
- **Synthesizer:** LSA and TF-IDF merge the narrative into a seamless, dense institutional paragraph.
- **Dispatch:** Email Synopsis formats into a 102KB minified HTML payload that acts as the physical "Cockpit" UI for mobile and desktop screens.

This enables a living, automated ecosystem providing institutional insights 24/7.
