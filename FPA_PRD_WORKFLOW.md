# PRD Workflow - 10 Finger Scanner App

## 1. Product Overview

The 10 Finger Scanner App is a private mobile application used to register participant sessions, scan all 10 fingerprints using a mobile camera, review scan quality, and generate an Indonesian fingerprint-based indicative report.

The report output includes:

- Multiple Intelligence percentages
- DISC personality type
- Brain dominance
- Learning style
- IQ / EQ / CQ / AQ
- Love language
- Extracurricular suggestions
- Academic and career recommendations
- Indonesian explanation text
- Disclaimer that the result is indicative, not medical, psychological, or educational diagnosis

---

## 2. User Roles

The system has two base roles:

1. Admin
2. Staff

---

## 2.1 Admin Role

Admin has full operational access.

### Admin Can

- Login
- Register staff/user account
- Register scan session
- Fill participant information
- Start fingerprint scanning
- Preview scanned fingers
- Review scan session
- Approve or reject scan session
- Request rescan
- Generate report
- View generated report history
- Download report PDF
- View account profile

---

## 2.2 Staff Role

Staff has limited scanning access.

### Staff Can

- Login
- Register scan session
- Fill participant information
- Start fingerprint scanning
- Preview scanned fingers
- Submit scan session for admin review
- View generated report history
- View account profile

### Staff Cannot

- Register new users
- Approve or reject scan review
- Generate final report if approval is required by Admin
- Edit scoring formula
- Manage system settings

---

## 3. Navigation Structure

## 3.1 Admin Bottom Navigation Bar

Admin has 5 menus:

1. Dashboard
2. Session
3. Review
4. Report History
5. Account Profile

### Admin Navigation Purpose

| Menu | Purpose |
|---|---|
| Dashboard | Show overview of sessions, pending reviews, generated reports, and quick actions |
| Session | Register new participant session and start scanning |
| Review | Verify scan results and approve/reject scan session |
| Report History | View generated reports and download PDF |
| Account Profile | View profile, logout, and account settings |

---

## 3.2 Staff Bottom Navigation Bar

Staff has 4 menus:

1. Dashboard
2. Session
3. Report History
4. Account Profile

### Staff Navigation Purpose

| Menu | Purpose |
|---|---|
| Dashboard | Show overview of assigned/recent sessions |
| Session | Register participant session and scan fingers |
| Report History | View available generated reports |
| Account Profile | View profile and logout |

Staff does not have the Review menu.

---

## 4. Admin Workflow

## 4.1 Main Admin Flow

```text
Login
-> Dashboard
-> Register Session
-> Fill Participant Data
-> Start 10-Finger Scan
-> Preview Scan Result
-> Submit for Review
-> Review Scan Session
-> Approve Scan
-> Generate Report
-> View Report
-> Download PDF
```

---

## 4.2 Admin Detailed Workflow

### Step 1 - Login

Admin opens the app and logs in using registered credentials.

Required fields:

- Email / username
- Password

System validates credentials and redirects Admin to Dashboard.

---

### Step 2 - Dashboard Overview

Admin sees summary information:

- Total scan sessions
- Pending review sessions
- Approved sessions
- Rejected sessions
- Generated reports
- Recent activities

Admin can start a new session from Dashboard or go to the Session menu.

---

### Step 3 - Register Session

Admin creates a new scan session.

Required participant information:

- Participant name
- Age

Optional participant information:

- Gender
- Notes

System-generated fields:

- Session ID
- Created by
- Created timestamp
- Session status

The timestamp is filled automatically by the system.

Initial status:

```text
Draft / Registered
```

---

### Step 4 - Start Finger Scanning

After registering the session, Admin starts scanning.

The app guides Admin through all 10 fingers:

1. Right thumb
2. Right index
3. Right middle
4. Right ring
5. Right little
6. Left thumb
7. Left index
8. Left middle
9. Left ring
10. Left little

Each scan screen should show:

- Current finger name
- Camera preview
- Circle guide overlay
- Quality indicator
- Capture button
- Retry button

Each finger scan status:

- Pending
- Captured
- Need Retry
- Accepted

---

### Step 5 - Preview Scan Result

After scanning all 10 fingers, Admin sees preview screen.

Preview includes:

- 10 fingerprint thumbnails
- Finger name label
- Quality score per finger
- Retry button per finger
- Overall scan quality score

Admin can:

- Retry bad-quality fingers
- Submit session for review

Session status changes to:

```text
Waiting for Review
```

---

### Step 6 - Review Scan Session

Admin opens the Review menu.

Admin sees list of sessions with status:

```text
Waiting for Review
```

For each session, Admin can inspect:

- Participant information
- Scan timestamp
- Staff/admin who performed scan
- 10 captured fingerprints
- Quality score per finger
- Overall quality score
- Processing preview if available

Admin decision options:

- Approve
- Reject
- Request Rescan

---

### Step 7 - Approve or Reject

If approved:

```text
Session status = Approved
Report generation becomes available
```

If rejected:

```text
Session status = Rejected
Reason must be filled
```

If rescan required:

```text
Session status = Need Rescan
Specific fingers can be marked for retry
```

Example rejection reasons:

- Fingerprint image blurry
- Finger not centered
- Too much light reflection
- Incomplete finger scan
- Wrong finger order

---

### Step 8 - Generate Report

After approval, Admin clicks:

```text
Generate Report
```

System runs:

```text
Fingerprint feature extraction
-> Scoring formula
-> Report JSON generation
-> Indonesian explanation generation
-> PDF generation
```

Report status:

```text
Generating
-> Completed
```

---

### Step 9 - View and Download Report

Admin can view report summary and download PDF.

Report includes:

- Participant identity
- Scan quality summary
- Multiple Intelligence
- DISC personality
- Brain dominance
- Learning style
- IQ/EQ/CQ/AQ
- Love language
- Extracurricular suggestions
- Academic/career recommendations
- Disclaimer

---

## 5. Staff Workflow

## 5.1 Main Staff Flow

```text
Login
-> Dashboard
-> Register Session
-> Fill Participant Data
-> Start 10-Finger Scan
-> Preview Scan Result
-> Submit Session
-> Wait for Admin Review
-> View Generated Report History
```

---

## 5.2 Staff Detailed Workflow

### Step 1 - Login

Staff logs in using credentials created by Admin.

---

### Step 2 - Dashboard Overview

Staff sees:

- Sessions created by staff
- Recent scan sessions
- Sessions needing rescan
- Reports available to view

Staff does not see admin-level review controls.

---

### Step 3 - Register Session

Staff creates a participant session.

Required fields:

- Participant name
- Age

Optional fields:

- Gender
- Notes

Automatic fields:

- Timestamp
- Staff ID
- Session ID

---

### Step 4 - Scan Fingers

Staff performs 10-finger scanning using the same scanner flow.

The app guides staff step-by-step through all 10 fingers.

---

### Step 5 - Preview

Staff reviews all captured fingerprints.

Staff can:

- Retry individual fingers
- Submit session

After submit:

```text
Session status = Waiting for Review
```

Staff cannot approve the session.

---

### Step 6 - Report History

Staff can view reports that are already generated and available.

Depending on permission settings, Staff may:

- View report summary
- Download PDF

Or only view report status.

---

## 6. Session Status Lifecycle

Use this status lifecycle:

```text
Draft
-> Registered
-> Scanning
-> Scan Completed
-> Waiting for Review
-> Approved
-> Generating Report
-> Report Generated
```

Alternative branches:

```text
Waiting for Review
-> Rejected

Waiting for Review
-> Need Rescan
-> Scanning
-> Scan Completed
-> Waiting for Review
```

---

## 6.1 Status Definitions

| Status | Meaning |
|---|---|
| Draft | Session created but not completed |
| Registered | Participant data saved |
| Scanning | Finger scanning in progress |
| Scan Completed | All 10 fingers captured |
| Waiting for Review | Scan submitted for Admin review |
| Approved | Admin approved scan quality |
| Rejected | Admin rejected scan session |
| Need Rescan | One or more fingers must be scanned again |
| Generating Report | Report engine is running |
| Report Generated | Final report and PDF are ready |

---

## 7. Screen Workflow

## 7.1 Admin Screens

- Login Screen
- Dashboard Screen
- Session List Screen
- Register Session Screen
- Finger Scan Screen
- Scan Preview Screen
- Review List Screen
- Review Detail Screen
- Generate Report Screen
- Report Detail Screen
- Report History Screen
- Account Profile Screen

---

## 7.2 Staff Screens

- Login Screen
- Dashboard Screen
- Session List Screen
- Register Session Screen
- Finger Scan Screen
- Scan Preview Screen
- Report History Screen
- Report Detail Screen
- Account Profile Screen

---

## 8. Admin User Journey

```text
Admin logs in
-> Opens Dashboard
-> Taps Session
-> Taps Register Session
-> Inputs participant name and age
-> System automatically saves timestamp
-> Admin taps Start Scan
-> App guides Admin through 10 fingers
-> Admin previews all scans
-> Admin submits scan
-> Admin opens Review menu
-> Admin reviews scan quality
-> Admin approves scan
-> Admin generates report
-> Admin views report
-> Admin downloads PDF
```

---

## 9. Staff User Journey

```text
Staff logs in
-> Opens Dashboard
-> Taps Session
-> Taps Register Session
-> Inputs participant name and age
-> System automatically saves timestamp
-> Staff taps Start Scan
-> App guides Staff through 10 fingers
-> Staff previews all scans
-> Staff submits scan
-> Session waits for Admin review
-> Staff checks Report History after report is generated
```

---

## 10. Permissions Matrix

| Feature | Admin | Staff |
|---|---:|---:|
| Login | Yes | Yes |
| Register user/staff | Yes | No |
| Register session | Yes | Yes |
| Fill participant data | Yes | Yes |
| Auto timestamp | Yes | Yes |
| Start scanning | Yes | Yes |
| Preview scan | Yes | Yes |
| Submit scan | Yes | Yes |
| Review scan session | Yes | No |
| Approve scan | Yes | No |
| Reject scan | Yes | No |
| Request rescan | Yes | No |
| Generate report | Yes | No / Optional |
| View report history | Yes | Yes |
| Download report PDF | Yes | Optional |
| Account profile | Yes | Yes |

Recommended MVP rule:

```text
Only Admin can generate final report.
Staff can only create session, scan, submit, and view generated reports.
```

---

## 11. Workflow Acceptance Criteria

## 11.1 Admin Acceptance Criteria

Admin workflow is successful when:

- Admin can login
- Admin can register staff/user
- Admin can create participant session
- Timestamp is automatically generated
- Admin can scan all 10 fingers
- Admin can preview scan result
- Admin can approve/reject scan session
- Admin can generate report after approval
- Admin can view/download generated report

---

## 11.2 Staff Acceptance Criteria

Staff workflow is successful when:

- Staff can login
- Staff can create participant session
- Timestamp is automatically generated
- Staff can scan all 10 fingers
- Staff can preview scan result
- Staff can submit session for review
- Staff can view generated report history

---

## 12. Recommended MVP Workflow

For the first version, use this MVP flow:

```text
Admin:
Login
-> Register Session
-> Scan 10 Fingers
-> Preview
-> Approve
-> Generate Report
-> Download PDF

Staff:
Login
-> Register Session
-> Scan 10 Fingers
-> Preview
-> Submit for Review
-> View Report History
```

This keeps the app simple but already covers the most important operational process.
