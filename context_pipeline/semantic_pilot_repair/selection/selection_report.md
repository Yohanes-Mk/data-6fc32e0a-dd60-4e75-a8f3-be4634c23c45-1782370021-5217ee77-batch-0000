# Repair Selection Report

Selected 8 distinct Stage 4A-sampled conversations for deep repair. Coverage categories may overlap when one conversation satisfies more than one repair need.

- `claude:conversations:conversation:14f3c888-fb33-40af-9039-e8cf89a97bb5` primary `false_project` coverage `false_project`: Stage 4A produced project candidate failing strict project test; false_project_score=1
- `claude:conversations:conversation:2838a734-4192-4c0c-93b5-d72976f21da8` primary `false_project` coverage `false_project, mixed_or_extreme`: Stage 4A produced project candidate failing strict project test; false_project_score=1; Also satisfies mixed/extreme repair coverage based on Stage 4A extreme-complexity selection.
- `claude:conversations:conversation:94f53cfc-057a-4aa6-a827-4ec3bb332f9a` primary `plausible_real_project` coverage `plausible_real_project`: Stage 4A project candidate had at least three strict project signals; plausible_project_score=1
- `claude:conversations:conversation:b8366901-9272-45e8-af3f-864fe1629fc8` primary `plausible_real_project` coverage `plausible_real_project`: Stage 4A project candidate had at least three strict project signals; plausible_project_score=1
- `claude:conversations:conversation:e2fc5641-6bd8-41c3-80d2-1e1e71b1e491` primary `attachment_heavy` coverage `attachment_heavy`: Highest available attachment count among Stage 4A sampled conversations; attachment_count=92
- `claude:conversations:conversation:c69f5e03-ed66-4419-a30a-a3a6a98c5909` primary `assistant_tool_heavy` coverage `assistant_tool_heavy`: Highest available tool-call count among remaining sampled conversations; tool_call_count=144
- `claude:conversations:conversation:244ba1ae-0ab9-43dc-b4a4-03cfbbb79859` primary `project_document_linked_proxy` coverage `project_document_linked_proxy`: Stage 4A project-document packets have project IDs rather than conversation IDs; this sampled conversation is retained as the deterministic proxy for project-document-linked repair coverage.; Proxy status is documented as a limitation rather than an invented join.
- `claude:conversations:conversation:248a80bc-eacc-4090-8173-7634a9c47edf` primary `deterministic_fill` coverage `deterministic_fill`: Filled remaining repair slot deterministically from Stage 4A sample

Project-document limitation: Stage 4A project-document packets have project IDs rather than conversation IDs, so the repair uses an explicit proxy conversation category and preserves this as a limitation rather than inventing a conversation link.
