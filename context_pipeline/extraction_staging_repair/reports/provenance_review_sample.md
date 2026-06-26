# Provenance Review Sample

## pure user-authored content
- Unit: `stage3r:source_unit:9fabcb38857ea88827a0216831aa0bbf`
- Offsets: {'start': 0, 'end': 111}
- Origin: `user_authored` / `direct_user_statement`
- Confidence: `high`
- Eligible: `True`

## user framing plus pasted assistant output
- Unit: `stage3r:source_unit:52cf155f3e6c0e1ba59b57aaee25b08b`
- Offsets: {'start': 25, 'end': 113}
- Origin: `assistant_generated` / `pasted_for_analysis`
- Confidence: `high`
- Eligible: `False`

## user framing plus console/log output
- Unit: `stage3r:source_unit:fd5677c8ee589c6cc135b6403beea89d`
- Offsets: {'start': 2160, 'end': 2175}
- Origin: `console_or_log_output` / `execution_trace`
- Confidence: `high`
- Eligible: `False`

## transcript content
- Unit: `stage3r:source_unit:22a875526c1a2b9361400f9f5fb861cf`
- Offsets: {'start': 0, 'end': 4076}
- Origin: `transcript_content` / `source_material`
- Confidence: `medium`
- Eligible: `False`

## assistant proposal
- Unit: `stage3r:source_unit:03098ebeb7904475b6c99d16fb4abf4e`
- Offsets: {'start': 0, 'end': 3745}
- Origin: `assistant_generated` / `generated_response`
- Confidence: `high`
- Eligible: `False`

## explicit user endorsement
- Unit: `stage3r:source_unit:f77f5a4b1e0b0217d184bb3adbf0ece9`
- Offsets: {'start': 321, 'end': 381}
- Origin: `user_authored` / `user_endorsement`
- Confidence: `high`
- Eligible: `True`

## uncertain mixed-origin content
- Unit: `stage3r:source_unit:22a875526c1a2b9361400f9f5fb861cf`
- Offsets: {'start': 0, 'end': 4076}
- Origin: `transcript_content` / `source_material`
- Confidence: `medium`
- Eligible: `False`
