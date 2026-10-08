# Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)

> Source document for [context.md](./context.md) — see that file for the derived technical breakdown, [architecture.md](./architecture.md) for system design, [implementation-plan.md](./implementation-plan.md) for the phased build plan, and [edge-case.md](./edge-case.md) for corner scenarios.

## Background

Food delivery and discovery platforms like Zomato list thousands of restaurants per city, each tagged with structured attributes — location, cuisine, cost, rating, votes. Structured filters (sort by rating, filter by cost) narrow the list mechanically, but they can't reason about *why* a restaurant fits a specific craving, nor explain a recommendation in plain language. A user typing "cozy spot for a late-night date, not too expensive" gets no better than a generic filtered list — the platform has the data to answer that question well, but no way to reason over it.

## The Problem

Given a large, real-world restaurant dataset and a set of user preferences, there is no lightweight way to:

1. Narrow thousands of listings down to a small, relevant candidate set deterministically (without an LLM touching the full dataset — too slow, too expensive, and unnecessary).
2. Rank that candidate set the way a knowledgeable local friend would — weighing rating, cost, cuisine fit, and soft preferences ("family-friendly," "quick service," "good for a date") together.
3. Explain each recommendation in natural language, so the user trusts and understands *why* a restaurant was suggested, not just that it was.
4. Degrade gracefully when the reasoning layer (an LLM) is unavailable, rather than failing outright.

## Objective

Design and implement an application that:

- Takes user preferences (location, budget, cuisine, minimum rating, and free-text "vibe" preferences)
- Uses a real-world dataset of restaurants (Zomato Bangalore listings)
- Filters that dataset deterministically to a small, relevant candidate set
- Leverages an LLM to rank the candidates and generate a personalized, human-readable explanation for each
- Displays clear, trustworthy results to the user — restaurant name, cuisine, rating, estimated cost, and the AI's reasoning
- Falls back to a sensible non-AI ranking (by rating) if the LLM is unavailable, rather than breaking

## Scope

**In scope:**
- A single-city dataset (Bangalore) sourced from a public Zomato dataset on Hugging Face
- Deterministic pre-filtering by location, budget tier, cuisine, and minimum rating
- LLM-based ranking and explanation of the filtered candidates via Groq
- A usable UI (web dashboard) for entering preferences and viewing results
- A REST API exposing the same recommendation pipeline

**Out of scope:**
- Multi-city or real-time/live restaurant data (the dataset is a static snapshot)
- User accounts, order placement, payments, or reservations
- Personalization based on prior order history (only the current session's stated preferences)

## Success Criteria

1. Users can specify location, budget, cuisine, minimum rating, and optional free-text preferences.
2. The system filters the dataset based on those inputs before any LLM call.
3. An LLM ranks and explains recommendations using only the filtered, structured candidate data (never inventing restaurants outside the dataset).
4. Results are displayed with name, cuisine, rating, estimated cost, and an AI-generated explanation for each.
5. If the LLM is unavailable or fails, the system still returns a ranked, useful result set instead of an error.
