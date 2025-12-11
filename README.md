**🚑 Rise360 Legacy xAPI Converter (Community Fix)**

This repository contains a **community-created**, **unofficial tool** to convert the new post-December-2025 Rise360 xAPI export structure back into the legacy layout and behaviour required by many LMS platform.
Created with assistance from LLM tooling. Shared freely for anyone impacted by the recent Rise360 file-structure changes.

In December 2025, Articulate Rise360 silently changed its xAPI/TinCan output structure, breaking functionality for many LMS environments that depend on:
- The old Rise folder layout
- The presence of **tincan.js** and **lms.js**
- The legacy xAPI behaviour and reporting model
- The ability for certificate or completion logic to detect LRS state

This repository contains a converter script that transforms any new Rise360 xAPI export into a structure that behaves like the old Rise exports.

If your LMS suddenly stopped tracking completions, refused uploads, or returned blank screens after the Rise update, this tool is for you.

**⚠️ Disclaimer**
- This is not an official tool.
- It is not supported or endorsed by Articulate.
- It is provided as-is, without guarantee.
- Use at your own discretion and responsibility.
- It was created to solve our organisation's needs and is shared publicly in case it helps others.

If this solves your problem, amazing. If not, feel free to fork, modify, and improve.

**🧠 How It Works**

When you run the converter, it will:
1. Flatten the new Rise export into an old-style folder structure
2. Copy the missing legacy xAPI runtime files (tincan.js and lms.js) from your donor package
3. Patch index.html and index_lms.html to restore LMSProxy functionality
4. Re-route tracking calls from Rise’s new API to the older one
5. Update tincan.xml to launch correctly
6. Validate the final package with a diagnostis script

The resulting course:
- Uploads into SCORM Cloud/Legacy LMSs
- Tracks completion in SCORM Cloud **and** LMS platforms expecting the legacy Rise behaviour
- Restores LRS events required for certificates or state-dependent flows


**📦 Folder Structure**
Your repository should contain:
Rise360-XAPI-Converter/
│
├── fix_scorm_package.py        # Main converter script
├── diagnose_package.py         # Validation and troubleshooting tool
│
├── DONOR_PACKAGE_FOLDER/       # Place your OWN pre-Dec-2025 Rise course here
│   └── .keep
│
├── NEW_RISE_FOLDER/            # Place your new (broken) Dec-2025+ Rise export here
│   └── .keep
│
└── OUTPUT_FOLDER/              # The final converted xAPI package will be generated here
    └── .keep

The DONOR_PACKAGE_FOLDER should contain your own pre-December-2025 working Rise360 xAPI export.
This is needed because Articulate removed the tincan.js and lms.js files from new packages, but the logic in those files is still required by many LMSs.

This repo will include empty placeholder directories only. You must replace these with your own course exports.

Folders contain .keep files so GitHub preserves directory structure.

**Nothing in this repo contains real course content.**

**🚀 How to Use**
----
🛠 Setup Steps
----
0. EXTRACT ALL THE CONTENTS OF THIS FOLDER BEFORE RUNNING ANYTHING to your Desktop.
1. Install Python-3.14.2-amd64.exe from the .zip folder. 
2. Run Terminal and type: **python --version** and it should say a version. 
3. If nothing shows or Python can't be found, try installing from the Microsoft Store.
4. Repeat **python --versio**n until you have a version detected.
5. Ensure fix_scorm_package.py and diagnose_package.py and the DONOR_PACKAGE_FOLDER and OUTPUT_FOLDER and NEW_RISE_FOLDER are on your Desktop.
	**DONOR_PACKAGE_FOLDER** is the location where your pre-December2025 update course files will be.
	**OUTPUT_FOLDER** is blank
	**NEW_RISE_FOLDER** is blank, the destination for your Rise360 package contents.
6. Extract desired Rise360 xapi/TinCan package (contents, not folder) into NEW_RISE_FOLDER.
7. Extract pre-December2025 Rise360 package contents into** DONOR_PACKAGE_FOLDER**
8. Everything is set up, move onto running the scripts below.

----
**▶️ Running the Scripts**
----
1. Right-click on your Desktop (NOT on a folder) → “Open in Terminal”
   This ensures Terminal/Powershell starts in the correct location.

2. Run the converter script:

       python fix_scorm_package.py NEW_RISE_FOLDER/ DONOR_PACKAGE_FOLDER/ OUTPUT_FOLDER/

   What this script does:
       • Flattens the new Rise folder structure into the old layout
       • Imports legacy tincan.js and lms.js files
       • Patches index.html to use LMSProxy
       • Updates tincan.xml to use the correct legacy launch file

3. When the conversion completes, run the diagnosis script:

       python diagnose_package.py OUTPUT_FOLDER/

   The terminal will check for missing files, folder issues, and incorrect references.

   A successful result will include:

       === Overall ===
       Looks structurally sound for legacy xAPI tracking.

4. If you see the success message, you're good to go.

5. Open OUTPUT_FOLDER/, select ALL **contents** inside it,
   then right-click → “Compress to” → “ZIP File”.

   Important:
       ZIP **the contents** of OUTPUT_FOLDER, NOT the folder itself.

6. The resulting ZIP file is your final TinCan/xAPI package.
   Upload it to your LMS exactly as you would with a normal Rise360 export.

----
**✅ Screenshots**
----
COMMAND: <img width="740" height="29" alt="image" src="https://github.com/user-attachments/assets/ea78e906-22d3-4536-81dc-5cd12893ab0c" />
PROCESS: <img width="613" height="266" alt="image" src="https://github.com/user-attachments/assets/8526271a-10f3-457c-ac48-a97c0e19eac6" />
DIAGNOSIS: <img width="2000" height="859" alt="image" src="https://github.com/user-attachments/assets/3c8988d1-bc54-40bb-9f85-d69bc98f9264" />

