10-Finger Camera Scanner and Indicative Intelligence Mapping Report

Version 1.0 \| Draft for product planning

Product concept: private mobile 10-finger camera scanner with REST API backend, MinIO object storage, and Indonesian PDF report output.

# 1. Executive Summary

This PRD defines a private mobile application that captures 10 fingerprints using a phone camera, processes fingerprint images through an online REST API, and generates an Indonesian-language indicative report. The report includes Multiple Intelligence percentages, DISC profile, brain dominance, learning style, IQ/EQ/CQ/AQ, love language, extracurricular suggestions, and academic/career recommendations.

The product is designed as an indicative profiling and development-support tool, not as a medical, psychological, or educational diagnosis.

# 2. Product Goals

- Provide a guided 10-finger scanning flow using a mobile camera, circle overlay, zoom, focus control, and quality validation.

- Generate a consistent, professional Indonesian PDF report similar in structure to the sample reference report.

- Build an explainable scoring engine so each score can be traced back to fingerprint features and scoring rules.

- Store biometric images and generated reports securely using private object storage and backend-controlled access.

- Support operators, consultants, and clients with role-appropriate access to scans and reports.

# 3. Target Users and Roles

| **Role**        | **Primary Needs**                                                      | **Permissions**                         |
|-----------------|------------------------------------------------------------------------|-----------------------------------------|
| Super Admin     | Manage system, users, scoring configuration, templates, and reports.   | Full access.                            |
| Operator        | Create clients, perform scans, retry failed fingers, generate reports. | Create/read assigned scans and reports. |
| Consultant      | Review reports and explain results to parents/clients.                 | Read assigned reports, add notes.       |
| Client / Parent | View and download final report.                                        | Read own report only.                   |

# 4. Core User Journey

1.  Operator logs in to the mobile app.

2.  Operator creates a client profile with name, age, gender, school/institution, and notes.

3.  App shows scan instructions: clean finger, good lighting, place fingertip inside the circle, hold steady.

4.  Operator scans 10 fingers in fixed order with real-time quality feedback.

5.  Operator reviews captured finger thumbnails and retries low-quality scans.

6.  Backend processes images, extracts fingerprint features, calculates report scores, and generates the PDF.

7.  Operator/consultant reviews report summary and downloads the final Indonesian PDF.

# 5. Functional Requirements

| **ID** | **Requirement**                                                                            | **Priority** |
|--------|--------------------------------------------------------------------------------------------|--------------|
| FR-01  | User authentication with role-based access control.                                        | Must         |
| FR-02  | Create and manage client profiles.                                                         | Must         |
| FR-03  | Create scan session and guide user through all 10 fingers.                                 | Must         |
| FR-04  | Camera overlay with circle guide, zoom, focus, lighting feedback, and manual/auto capture. | Must         |
| FR-05  | Quality gate for blur, brightness, contrast, finger position, and ridge visibility.        | Must         |
| FR-06  | Upload raw finger images to backend, then store in private MinIO bucket.                   | Must         |
| FR-07  | Process images with OpenCV pipeline and extract fingerprint features.                      | Must         |
| FR-08  | Generate report JSON from scoring formula and recommendation rules.                        | Must         |
| FR-09  | Generate Indonesian PDF report with professional template and disclaimer.                  | Must         |
| FR-10  | Admin dashboard for reports, scan status, users, and scoring configuration.                | Should       |
| FR-11  | Consultant notes and report review workflow.                                               | Could        |

# 6. Report Output Requirements

The report must contain the following sections:

- Cover page with client name, report ID, date, and visual identity.

- Ringkasan Profil: top intelligence, DISC type, learning style, brain dominance, and dominant quotient.

- Kualitas Pemindaian Sidik Jari: accepted fingers, average quality, and scan validity.

- Multiple Intelligence: 8 percentages and interpretation text.

- DISC Personality: primary and secondary type with explanation and development suggestions.

- Dominasi Otak: left/right brain percentage and interpretation.

- Gaya Belajar: visual, auditory, kinesthetic percentages and learning recommendations.

- IQ/EQ/CQ/AQ: percentages, dominant quotient, and explanation.

- Love Language: dominant love language and relationship/parenting suggestions.

- Rekomendasi Ekstrakurikuler, Akademik, dan Karier.

- Catatan Penting / Disclaimer.

# 7. Fingerprint Feature Requirements

| **Feature**           | **Description**                                     | **Usage**                                      |
|-----------------------|-----------------------------------------------------|------------------------------------------------|
| Pattern type          | Whorl, loop, arch, tented arch, composite.          | Base pattern weight.                           |
| Ridge count           | Estimated ridge count in target fingerprint region. | Normalized ridge factor.                       |
| Core count            | Detected core point count.                          | Advanced feature factor.                       |
| Delta count           | Detected delta point count.                         | Advanced feature factor.                       |
| Minutiae count        | Ridge endings and bifurcations.                     | Advanced feature factor and quality indicator. |
| Ridge density         | Density/complexity of ridge area.                   | Advanced feature factor.                       |
| Orientation stability | Consistency of ridge flow.                          | Quality and feature reliability.               |
| Quality score         | Overall scan quality score from 0 to 100.           | Reject/accept gate and quality factor.         |

# 8. Scoring Model Summary

The product uses an explainable rule-based scoring model. Each finger receives a finger strength score, then the strength is mapped into report categories through configurable weight matrices.

- finger_strength = pattern_weight x ridge_factor x advanced_factor x quality_factor

- category_raw_score = sum(finger_strength\[finger\] x category_weight\[finger\]\[category\])

- category_percentage = category_raw_score / sum(all category raw scores) x 100

- Highest score determines dominant category; second highest determines secondary category where needed.

# 9. Non-Functional Requirements

| **Area**        | **Requirement**                                                                                                                              |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| Security        | All fingerprint images and reports must be private. Mobile app must not receive MinIO secret keys.                                           |
| Privacy         | Biometric data must be protected through consent, access control, audit logging, and retention policy.                                       |
| Performance     | A single finger upload should complete quickly on normal mobile data; report generation target under 2 minutes after all scans are accepted. |
| Reliability     | Failed uploads and failed processing jobs must be retryable.                                                                                 |
| Maintainability | Scoring weights and report templates should be configurable outside core processing code.                                                    |
| Localization    | User-facing report content must be Indonesian.                                                                                               |

# 10. Success Metrics

- At least 90% of scan sessions complete with 10 accepted fingers after guided retries.

- Average scan quality score above 80 for accepted fingers.

- Report PDF generated successfully for at least 98% of completed sessions.

- Operators can complete a full 10-finger scan and report generation flow without technical assistance.

- Consultants can explain report output using visible explanations and recommendation reasons.

# 11. Out of Scope for MVP

- Identity verification or legal biometric authentication.

- Clinical psychological diagnosis.

- Fully automated scientific validation claims.

- Public direct upload from mobile app to object storage.

- Complex ML model training until enough real scan/report data exists.

# 12. MVP Milestones

| **Phase** | **Scope**                                                                     | **Output**                  |
|-----------|-------------------------------------------------------------------------------|-----------------------------|
| Phase 1   | Camera prototype, one-finger scan, backend upload, OpenCV processing preview. | Technical proof of concept. |
| Phase 2   | 10-finger flow, quality gate, retry mechanism, MinIO storage.                 | Complete scan session flow. |
| Phase 3   | Feature extraction and rule-based report engine.                              | Report JSON output.         |
| Phase 4   | Indonesian PDF template and report download.                                  | Final PDF report.           |
| Phase 5   | Admin dashboard and scoring configuration.                                    | Operational back office.    |

# 13. Disclaimer Text for Report

Catatan Penting: Laporan ini merupakan hasil analisis indikatif berdasarkan pola sidik jari dan perhitungan model internal sistem. Hasil yang ditampilkan bertujuan untuk membantu memahami kecenderungan potensi, gaya belajar, karakter umum, dan rekomendasi pengembangan diri. Laporan ini bukan merupakan diagnosis medis, psikologis, pendidikan, ataupun penentu mutlak terhadap kecerdasan, kepribadian, masa depan akademik, maupun karier seseorang. Hasil analisis sebaiknya digunakan sebagai bahan pendukung diskusi bersama orang tua, pendidik, konselor, atau profesional terkait.
