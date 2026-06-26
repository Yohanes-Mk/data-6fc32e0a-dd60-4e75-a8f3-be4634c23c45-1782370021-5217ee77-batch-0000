# Comparison With Stage 4A

- Original candidates: 62
- Repaired candidates: 21
- Original candidates retained: 0
- Revised/kept with revision: 26
- Reclassified: 5
- Discarded: 31
- False project rate: 5/10 (50.0%)
- Assistant-noise count: 18
- Tool-noise count: 13
- Evidence-reference count change: 62 -> 37
- Low-confidence change: 0 -> 0
- Relationship-specificity change: Stage 4A used Counter({'related_to': 14}); repair uses {'informed_by': 6, 'supports': 2, 'depends_on': 4}

The original Stage 4A approach is not reusable as-is. Its structural pipeline can be reused, but candidate creation must operate at conversation-bundle level with strict project tests, assistant/tool noise filters, and real quality review.
