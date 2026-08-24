# F-035 — Safe fix waves

**Status:** todo  
**Phase:** C2  

## Description

After FIND (F-034), fix only prioritized issues in small waves. One cluster per wave. Mandatory verify. Avoid “fix all bugs → 100 new bugs.”

## Tech

- Fix tasks reference finding ids  
- Narrow file allowlist per task  
- F-029 verification after each wave  

## Do

- User picks which findings to fix (or policy: severity≥X)  
- Stop wave on verify fail  

## Don’t

- Opportunistic large refactors during fix  
- Mix find and fix in same agent without phase boundary  

## See also

- `docs/REVIEW_AND_FIX.md`  

## Touch

- runtime task types  
- harness verify  
- code-review / implementation skills  

## Done note

_(empty)_
