# F-032 — Voice input

**Status:** todo  
**Phase:** D1 (after plan mode + bible + SDD basics)  

## Description

Beginner speaks a problem; STT → text objective → same agent pipeline. Optional TTS for status and permission questions.

## Tech

- Adapter only: `SpeechToTextProvider` interface  
- Web: Web Speech API or server Whisper  
- Engine never depends on a specific STT vendor  
- Permission prompts for large review swarms can be spoken back  

## Do

- Fall back to text if mic denied  
- Keep voice optional  

## Don’t

- Block core agent path on STT outage  
- Implement desktop-only voice first  

## See also

- `docs/VOICE_AND_SDD.md`  

## Touch

- new `src/adapters/speech/`  
- UI/CLI capture only  

## Done note

_(empty)_
