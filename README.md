#🚑 Rise360 Legacy xAPI Converter (Community Fix)

A community-created, unofficial tool to restore pre-December-2025 Rise360 xAPI behaviour for LMS compatibility.
Created with assistance from LLM tooling. Shared freely for anyone impacted by the recent Rise360 file-structure changes.

In December 2025, Articulate Rise360 silently changed its xAPI/TinCan output structure, breaking functionality for many LMS environments that depend on:
- The old Rise folder layout
- The presence of tincan.js and lms.js
- The legacy xAPI behaviour and reporting model
- The ability for certificate or completion logic to detect LRS state

This repository contains a converter script that transforms any new Rise360 xAPI export into a structure that behaves like the old Rise exports.

If your LMS suddenly stopped tracking completions, refused uploads, or returned blank screens after the Rise update, this tool is for you.

#⚠️ Disclaimer
- This is not an official tool.
- It is not supported or endorsed by Articulate.
- It is provided as-is, without guarantee.
- Use at your own discretion and responsibility.
- It was created to solve our organisation's needs and is shared publicly in case it helps others.

If this solves your problem, amazing. If not, feel free to fork, modify, and improve.

#🧠 How It Works
The converter:
1. Flattens the new Rise export to match the old Rise layout.
2. Restores missing legacy xAPI components, specifically:
      - lib/tincan.js
      - lib/lms.js
3. Patches index.html and index_lms.html so that the Rise player uses the restored legacy LMSProxy instead of the new parent-frame API.
4. Repairs tincan.xml to launch the correct entry point.
5. Performs multiple checks and rewrites to ensure:
      - Completion tracking works like before
      - Your LMS receives xAPI statements the way it expects
      - Certificate/credential logic that depends on completions works again

The diagnosis script then confirms that everything is wired correctly.
