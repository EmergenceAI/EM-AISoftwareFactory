---
name: create-bug-from-video
description: Create bug reports in Jira from screen recording videos. Extracts keyframes and audio, analyzes the UI and narration to identify the bug, confirms understanding with the user, then files a structured bug report with the video attached. Use when given a video file (.mov, .mp4, .webm) showing a bug.
---

# Create Bug Report from Video

Create comprehensive bug reports in Jira by analyzing screen recording videos. Extracts visual frames and audio transcription to understand the bug, confirms with the user, then files in Jira with the video attached.

## When to Use This Skill

Use this skill when:
- User provides a screen recording video (.mov, .mp4, .webm) of a bug
- User asks to file a bug from a video
- User says "create a bug from this video" or similar

## Usage

```bash
/create-bug-from-video path/to/recording.mov
/create-bug-from-video ~/Downloads/bug-demo.mp4
```

## Process

### Step 1: Validate Video File

```bash
# Check file exists and get metadata
VIDEO_PATH="{user-provided-path}"

if [ ! -f "$VIDEO_PATH" ]; then
    echo "File not found: $VIDEO_PATH"
    exit 1
fi

# Get video info
ffprobe -v quiet -print_format json -show_format -show_streams "$VIDEO_PATH"
```

Report to user:
```
Video: bug-demo.mov
Duration: 1m 54s
Resolution: 2818x3044
Has audio: Yes
```

### Step 2: Extract Keyframes

Choose the keyframe interval based on video duration:
- Under 30 seconds: every 5 seconds
- 30 seconds to 5 minutes: every 10 seconds
- Over 5 minutes: every 20-30 seconds

```bash
mkdir -p /tmp/bug_video_frames

# Extract keyframes (adjust fps=1/N based on duration), scale down for analysis
ffmpeg -i "$VIDEO_PATH" \
  -vf "fps=1/5,scale=1409:-1" \
  /tmp/bug_video_frames/frame_%03d.png -y
```

Read each extracted frame using the Read tool to visually analyze the UI state.

### Step 3: Extract and Transcribe Audio

Audio transcription is critical — narration often explains context that frames alone cannot convey. Try hard before falling back.

```bash
# Extract audio
ffmpeg -i "$VIDEO_PATH" -q:a 0 -map a /tmp/bug_video_audio.wav -y
```

**Attempt 1:** Run whisper CLI directly:
```bash
whisper /tmp/bug_video_audio.wav --model base --language en --output_format txt --output_dir /tmp
```

**Attempt 2:** If Attempt 1 fails (typically SSL errors downloading the model), bypass SSL verification and use the Python API:
```bash
python3 -c "
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import whisper
model = whisper.load_model('base')
result = model.transcribe('/tmp/bug_video_audio.wav', language='en')
print(result['text'])
"
```

**Attempt 3:** If whisper is not installed at all, check for alternative transcription tools:
```bash
# Check for alternative tools
which mlx_whisper 2>/dev/null || which faster-whisper 2>/dev/null
```

**Only after all attempts fail:**
- Fall back to visual-only analysis
- Note to user: "Could not transcribe audio after multiple attempts — analyzing from visual frames only"

**If transcription succeeds:**
- Include the transcript in the bug analysis AND in the final Jira description
- Audio narration often reveals the user's intent and expected behavior more clearly than frames alone

### Step 4: Analyze and Identify the Bug

From the keyframes (and transcription if available), identify:

1. **What product/feature** is being shown (e.g., dashboard name, page, workflow)
2. **What the user is doing** (e.g., clicking, typing a question, navigating)
3. **What appears to go wrong** (e.g., error message, incorrect response, missing data)
4. **What the expected behavior should be** based on context

Use the video filename as an additional hint — it often describes the bug (e.g., `chat_bug_severity_policy_knowledge_retrieval.mov`).

### Step 5: Confirm Understanding with User

Present your analysis and ask the user to confirm or correct:

```
From the video, here's what I see:

**Product/Area:** [identified area]
**What happens:** [description of the bug observed]
**Expected behavior:** [what should have happened]

Does this capture the bug correctly?
```

Options:
- "Yes, that's the bug"
- "Close but needs correction" → user clarifies
- "Different issue entirely" → user describes the actual bug

Iterate until the user confirms the bug description is accurate.

### Step 6: Gather Additional Context

Ask the user for any details not visible in the video:

```
A few more details:

1. Priority? [High / Medium / Low]
2. Did this work before? [Y/n/unknown]
3. Any additional context not shown in the video?
```

### Step 7: Auto-Detect Environment

**Gather automatically (no user input):**

```bash
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "untagged")
COMMIT=$(git rev-parse --short HEAD)
BRANCH=$(git branch --show-current)
REPORTER_NAME=$(git config user.name)
REPORTER_EMAIL=$(git config user.email)
OS=$(uname -s)
DATE=$(date +"%Y-%m-%d")
```

### Step 8: Get Jira Components

```
Invoke mcp__atlassian__jira_get_project_components with project_key: "SEMI"
```

Ask user to select components from the available list.

### Step 9: Show Preview

Show the complete bug report for review before filing:

```markdown
═══════════════════════════════════════════════════
PREVIEW: Bug Report for Jira (from video analysis)
═══════════════════════════════════════════════════

Project: SEMI
Priority: {priority}
Components: {components}
Labels: bug, needs-triage

────────────────────────────────────────────────────
Bug: {summary}
────────────────────────────────────────────────────

## Expected Behavior
{expected}

## Actual Behavior
{actual}

## Steps to Reproduce
{steps from video analysis}

## Environment
- Version / Commit / Branch / OS / Reporter / Date

## Video Evidence
{video filename} ({file size})
Will be uploaded automatically after issue creation.

────────────────────────────────────────────────────
Create this bug in Jira? [Y/n/e]
```

### Step 10: Create in Jira and Upload Video

**Create the issue:**
```
Invoke mcp__atlassian__jira_create_issue with:
  project_key: "SEMI"
  summary: "{bug summary}"
  issue_type: "Bug"
  description: {full bug report markdown}
  components: "{selected components}"
  additional_fields: {"labels": ["bug", "needs-triage"]}
```

**Upload the video as attachment:**
```
Invoke mcp__atlassian__jira_update_issue with:
  issue_key: "{created issue key}"
  fields: {}
  attachments: "{video file path}"
```

### Step 11: Output Summary

```markdown
Bug created and video attached!

**Issue:** SEMI-1234
**URL:** https://emergenceai.atlassian.net/browse/SEMI-1234
**Priority:** High
**Components:** Frontend, Backend
**Video:** bug-demo.mov (attached)
```

## Cleanup

Remove temporary files after completion:

```bash
rm -rf /tmp/bug_video_frames /tmp/bug_video_audio.wav /tmp/bug_video_audio.txt
```

## Requirements

- **ffmpeg** and **ffprobe** must be installed (`brew install ffmpeg`)
- **whisper** is optional — used for audio transcription if available and working
- Jira MCP tools must be configured for issue creation and attachment upload

## Success Criteria

- [x] Validates video file exists and gets metadata
- [x] Extracts keyframes for visual analysis
- [x] Attempts audio transcription (graceful fallback if unavailable)
- [x] Analyzes frames to identify the bug
- [x] Confirms understanding with the user before filing
- [x] Auto-detects environment info
- [x] Shows preview before creating
- [x] Creates bug in Jira
- [x] Uploads video as attachment automatically
- [x] Cleans up temp files

## Integration with Other Skills

```bash
# Create bug from video
/create-bug-from-video ~/Downloads/bug.mov → SEMI-1234 created

# Investigate the code
/research-codebase "How does {feature} work?"

# Create fix plan
/create-plan SEMI-1234

# Implement fix
/implement-plan SEMI-1234
```

## Notes

- Video analysis is best-effort — always confirm with the user before filing
- The video filename often contains useful context about the bug
- If the user provides additional text description alongside the video, use both
- Adjust keyframe interval based on video duration (5s for short, 10s for medium, 20-30s for long)
- Audio transcription is high-priority — narration often carries the most important context about what the bug is and why it matters. Do not give up after a single failure; try the SSL workaround and alternative tools before falling back to visual-only analysis
