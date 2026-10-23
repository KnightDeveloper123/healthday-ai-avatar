# ADR-008: Rule-based language layer for the MVP

**Status:** Accepted (revisit after Phase 4 and Phase 16 evaluation)

## Context
Input mixes English, Hindi, Marathi, Roman-script Hindi/Marathi and code-switching.
Generic language-ID libraries are weak on Roman Hindi/Marathi and short text.

## Options
1. Rule-based (script ranges + curated lexicons)
2. Off-the-shelf language-ID model
3. BHASHINI language detection (availability unverified)

## Decision
Start with rules (option 1), behind `analyze_text`. Evaluate 2 and 3 when the eval set
shows where rules fail.

## Consequences
No dependencies, fully testable, transparent. Accuracy is limited on unlisted words,
Hindi vs Marathi in Devanagari without markers, and very short inputs.