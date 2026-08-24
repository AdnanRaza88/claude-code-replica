# Voice input + Spec-Driven Development (SDD)

## Voice (beginners)

**Goal:** User talks like to a person. No IDE literacy required.

**Flow:**

1. Capture audio (browser MediaRecorder or OS STT later)  
2. Speech-to-text → plain text objective  
3. Same pipeline as typed objective (orchestrator → specs → build)  
4. Optional text-to-speech for status (“Planning…”, “Building UI…”, “Need your OK to spawn 6 review agents”)

**Tech direction (not implementing now):**

- Web: Web Speech API or Whisper-compatible endpoint  
- CLI: local whisper.cpp / system STT optional  
- Keep STT behind adapter; engine only sees text + optional `input_modality=voice`

**Do not:**

- Require voice for power users  
- Block agent work on TTS failures  

**Feature packet:** `features/F-032-voice-input/SPEC.md`

## Spec-Driven Development

**Goal:** No big parallel code until short specs exist.

**Artifacts (minimal set):**

| Doc | Role |
|-----|------|
| Intent | 5–10 lines: what user wants |
| PRD-lite | Goals, non-goals, acceptance |
| TRD-lite | Stack, modules, interfaces |
| Task graph | Parallel waves + dependencies |
| Bible | Theme + constraints (see PARALLEL_COHERENCE) |

**Flow:**

1. User request (voice/text)  
2. Plan mode (F-018): produce specs only, no write/bash by default  
3. User confirms or edits specs (UI/CLI)  
4. Lock bible  
5. Parallel implementation waves  
6. Verify against acceptance  

**Feature packet:** `features/F-033-spec-driven/SPEC.md`
