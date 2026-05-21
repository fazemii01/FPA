Architecture, Data Model, API, UI/UX, and Processing Mechanism

Version 1.0 \| Draft for product planning

Product concept: private mobile 10-finger camera scanner with REST API backend, MinIO object storage, and Indonesian PDF report output.

# 1. Architecture Overview

The application uses a mobile-first capture workflow and server-side processing architecture. The mobile app captures and validates images, while the backend owns storage, image processing, scoring, report generation, and access control.

- Mobile App: Flutter for Android/iOS camera capture and operator workflow.

- Backend API: Python FastAPI REST API.

- Image Processing: OpenCV, NumPy, scikit-image.

- Database: PostgreSQL for metadata, users, sessions, features, and report scores.

- Object Storage: MinIO S3-compatible storage for raw images, processed images, and report PDFs.

- Admin Dashboard: Next.js/React web dashboard.

- Deployment: Docker-based services on VPS/cloud environment.

# 2. System Diagram

Logical flow:

\[Flutter Mobile App\] -\> \[FastAPI REST API\] -\> \[Processing Worker\] -\> \[PostgreSQL + MinIO\] -\> \[Report PDF\] -\> \[Mobile/Admin Dashboard\]

# 3. Confirmed Storage Design

The existing MinIO service can be used as S3-compatible object storage. The S3 API endpoint should use the API port, not the console port.

| **Item**          | **Value / Recommendation**                                                   |
|-------------------|------------------------------------------------------------------------------|
| MinIO Console     | http://194.233.91.132:19001 or configured console domain.                    |
| MinIO S3 API      | http://194.233.91.132:19000 for backend integration.                         |
| Production Target | Use HTTPS domain before production launch.                                   |
| Access Pattern    | Backend-only access. Mobile app never receives storage secret keys.          |
| Bucket Policy     | Private buckets only; use backend-controlled reads or temporary signed URLs. |

# 4. Object Storage Structure

| **Bucket**            | **Object Key Pattern**                                 | **Purpose**                                               |
|-----------------------|--------------------------------------------------------|-----------------------------------------------------------|
| fingerprint-raw       | raw/{scan_session_id}/{finger_name}.jpg                | Original accepted finger images.                          |
| fingerprint-processed | processed/{scan_session_id}/{finger_name}\_{stage}.png | Enhanced, binary, skeleton, and debug processing outputs. |
| report-pdf            | reports/{scan_session_id}/report.pdf                   | Final Indonesian PDF report.                              |

# 5. Mobile App Design

Recommended framework: Flutter. The mobile app handles authentication, client creation, scan session workflow, local quality pre-checks, image upload, and report viewing.

| **Screen**        | **Purpose**                       | **Key UI Elements**                                                      |
|-------------------|-----------------------------------|--------------------------------------------------------------------------|
| Login             | Authenticate operators and users. | Email, password, login button.                                           |
| Dashboard         | Show recent clients and reports.  | Start scan button, recent sessions, pending reports.                     |
| Create Client     | Capture participant information.  | Name, age, gender, school, parent/contact, notes.                        |
| Scan Instructions | Prepare user before scanning.     | Cleaning, lighting, finger placement instructions.                       |
| Finger Scanner    | Capture each finger.              | Camera preview, circle guide, quality ring, finger label, capture/retry. |
| Scan Review       | Review all 10 fingers.            | Thumbnails, quality scores, retry buttons, process button.               |
| Report Summary    | Show top results.                 | Top intelligence, DISC, learning style, PDF download.                    |
| Full Report       | View report sections.             | Tabs/sections and PDF link.                                              |

# 6. Scanner UX Mechanism

1.  Show current finger label, e.g., Right Thumb.

2.  Display camera preview with center circle guide.

3.  Apply camera zoom around 1.5x to 2.5x depending on device capability.

4.  Run real-time pre-checks: finger placement, blur, brightness, contrast, ridge visibility.

5.  Turn quality ring red/yellow/green based on quality score.

6.  Enable capture only when quality is acceptable, or auto-capture after stable green state.

7.  Show preview and allow Accept or Retry.

8.  Upload accepted image to backend and continue to next finger.

# 7. Backend Services

| **Module**     | **Responsibilities**                                                              |
|----------------|-----------------------------------------------------------------------------------|
| auth           | Login, token validation, role-based access control.                               |
| clients        | Client profile CRUD.                                                              |
| scan_sessions  | Create sessions, track 10-finger status, completion state.                        |
| finger_uploads | Receive images, validate MIME/size, store raw images in MinIO.                    |
| processing     | ROI crop, grayscale, CLAHE, Gabor, threshold, morphology, skeletonization.        |
| features       | Pattern type, ridge count, core, delta, minutiae, density, orientation stability. |
| report_engine  | Calculate scores, explanation text, recommendations, report JSON.                 |
| pdf_generator  | Render Indonesian report PDF.                                                     |
| admin          | Users, reports, scoring config, template management.                              |

# 8. Image Processing Pipeline

- Camera capture with circle-based ROI.

- Quality gate: blur, brightness, contrast, finger position, ridge visibility.

- ROI crop and resize to standard image size.

- Grayscale conversion and denoising.

- CLAHE for local contrast enhancement.

- Fingerprint segmentation mask.

- Ridge orientation and frequency estimation.

- Gabor filtering for ridge enhancement.

- Adaptive/Sauvola thresholding.

- Morphological cleanup.

- Skeletonization using thinning algorithm.

- Feature extraction: pattern, ridge count, core, delta, minutiae, density, orientation stability.

# 9. Report Engine Formula

The rule-based scoring model is designed to be explainable and configurable.

- pattern_weight: value based on fingerprint pattern type.

- ridge_factor = clamp(ridge_count / average_ridge_count, 0.70, 1.30).

- advanced_factor = weighted combination of core, delta, minutiae, ridge density, and orientation stability factors.

- quality_factor = clamp(quality_score / 100, 0.75, 1.00).

- finger_strength = pattern_weight x ridge_factor x advanced_factor x quality_factor.

- category_raw_score = sum(finger_strength x category_weight).

- category_percentage = category_raw_score / total_raw_score x 100.

# 10. API Specification

| **Method** | **Endpoint**                                  | **Purpose**                                 |
|------------|-----------------------------------------------|---------------------------------------------|
| POST       | /api/auth/login                               | Authenticate user and return JWT.           |
| GET        | /api/auth/me                                  | Return current user profile and role.       |
| POST       | /api/clients                                  | Create client profile.                      |
| GET        | /api/clients                                  | List clients.                               |
| POST       | /api/scan-sessions                            | Create new scan session.                    |
| GET        | /api/scan-sessions/{id}                       | Get scan session details and finger status. |
| POST       | /api/scan-sessions/{id}/fingers/{finger_name} | Upload one finger image.                    |
| POST       | /api/scan-sessions/{id}/process               | Start processing and report generation.     |
| GET        | /api/reports/{id}                             | Get report JSON.                            |
| GET        | /api/reports/{id}/pdf                         | Download or view PDF report.                |
| PUT        | /api/admin/scoring-config                     | Update scoring configuration.               |

# 11. Database Model

| **Table**            | **Important Fields**                                                                                                                           |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| users                | id, name, email, password_hash, role, status, created_at.                                                                                      |
| clients              | id, name, age, gender, school, parent_name, phone, notes.                                                                                      |
| scan_sessions        | id, client_id, operator_id, status, average_quality_score, created_at, completed_at.                                                           |
| finger_scans         | id, scan_session_id, finger_name, raw_object_key, processed_object_key, quality_score, status.                                                 |
| fingerprint_features | id, finger_scan_id, pattern_type, ridge_count, core_count, delta_count, minutiae_count, ridge_density, orientation_stability, finger_strength. |
| reports              | id, scan_session_id, status, summary_json, pdf_object_key, created_at.                                                                         |
| report_scores        | id, report_id, section, category, score, interpretation, explanation.                                                                          |
| recommendations      | id, report_id, type, title, reason, rank.                                                                                                      |
| audit_logs           | id, actor_id, action, resource_type, resource_id, metadata, created_at.                                                                        |

# 12. Security and Privacy Design

- Use HTTPS for mobile-to-backend and backend-to-storage communication in production.

- Keep MinIO buckets private; no public access for fingerprint images.

- Store only object keys in PostgreSQL, not binary images.

- Use short-lived signed URLs only when client-side viewing is necessary.

- Encrypt backups and restrict object storage credentials to backend service only.

- Record audit logs for report access, image access, and admin configuration changes.

- Include explicit user consent before fingerprint capture.

- Define retention policy for raw images, processed images, and reports.

# 13. Report PDF Design Direction

- Language: Indonesian.

- Visual style: professional educational report, clean white background, blue/orange accents, clear page headings.

- Use charts/cards for percentage sections.

- Include explanation and recommendation under each score section.

- Include disclaimer page or disclaimer box in final section.

- Generate PDF from HTML template using backend PDF renderer.

# 14. Processing Job Mechanism

9.  User completes all 10 accepted finger uploads.

10. Backend marks scan session as ready_for_processing.

11. Processing job loads raw images from MinIO.

12. For each finger, backend runs OpenCV pipeline and stores processed outputs.

13. Feature extraction output is saved in fingerprint_features.

14. Report engine calculates report_scores and recommendation records.

15. PDF generator renders report and uploads it to report-pdf bucket.

16. Scan session status changes to completed, and report becomes available.

# 15. Deployment Plan

| **Service**    | **Technology**             | **Deployment Note**                                                    |
|----------------|----------------------------|------------------------------------------------------------------------|
| mobile-app     | Flutter                    | Android first, iOS later if needed.                                    |
| api            | FastAPI + Uvicorn/Gunicorn | Docker container behind reverse proxy.                                 |
| worker         | Python worker/Celery/RQ    | Runs CPU-heavy image processing and report jobs.                       |
| database       | PostgreSQL                 | Persistent volume and scheduled backups.                               |
| object-storage | MinIO                      | Existing service on ports 19000/19001; use HTTPS domain in production. |
| dashboard      | Next.js/React              | Admin/consultant web interface.                                        |
| reverse-proxy  | Nginx/Caddy/Traefik        | TLS termination and routing.                                           |

# 16. Open Risks and Mitigations

| **Risk**                                                | **Mitigation**                                                                     |
|---------------------------------------------------------|------------------------------------------------------------------------------------|
| Phone camera image quality varies by device.            | Use strict quality gate, circle ROI, zoom control, retry workflow.                 |
| Fingerprint feature extraction may fail on poor images. | Require re-scan below quality threshold; keep debug processed images for analysis. |
| Report claims may be perceived as diagnostic.           | Use indicative language and clear Indonesian disclaimer.                           |
| Biometric data privacy risk.                            | Private buckets, HTTPS, access control, audit logs, retention policy.              |
| Scoring model may need tuning.                          | Use configurable weight matrices and collect validation samples over time.         |

# 17. Initial Implementation Roadmap

| **Sprint** | **Deliverable**                                                       |
|------------|-----------------------------------------------------------------------|
| Sprint 1   | FastAPI skeleton, auth, PostgreSQL schema, MinIO integration.         |
| Sprint 2   | Flutter login, dashboard, client creation, one-finger camera capture. |
| Sprint 3   | 10-finger scan flow, quality gate, upload, session review.            |
| Sprint 4   | OpenCV processing service and feature extraction storage.             |
| Sprint 5   | Report engine, JSON output, explanation text, recommendation rules.   |
| Sprint 6   | Indonesian PDF template and report download.                          |
| Sprint 7   | Admin dashboard and scoring configuration.                            |
