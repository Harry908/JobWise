Feature: JobWise MVP – AI-powered job application assistant
  As a job seeker using a mobile app
  I want to manage a master resume, discover jobs, and generate tailored resumes/cover letters
  So that I can apply faster with professional, ATS-compatible documents

  # Traceability
  # SRS refs: FR-3.1.x (Master Resume), FR-3.2.x (Jobs), FR-3.3.x (AI Generation), FR-3.4.x (Documents), NFR-5.x
  # MoSCoW tags: @must, @should, @could, @wont

  Background:
    Given a registered user on a supported mobile device
    And the device may be online or offline
    And a clean app install with no existing profiles

  @must @profile @FR-3.1.1
  Scenario: Create a new master resume profile
    When the user creates a new profile with required fields
      | field        | value                    |
      | name         | Alex Doe                 |
      | email        | alex@example.com         |
      | phone        | +1-555-555-5555          |
      | location     | Seattle, WA              |
    And the user adds at least one work experience with dates and achievements
    And the user adds at least one education entry
    And the user categorizes at least 3 skills (technical/soft)
    Then the profile is saved locally with a unique id
    And required fields validation passes with no errors

  @must @profile @FR-3.1.2
  Scenario: Edit and version a profile
    Given an existing profile with experiences, skills, and education
    When the user updates the job title and adds a quantified bullet
    Then the app auto-saves the change locally
    And a new profile version is created with a timestamp
    And the user can view prior versions and restore a previous one

  @must @offline @sync @FR-3.1.3
  Scenario: Offline editing with sync and conflict policy
    Given the user is offline
    And the user updates the profile summary and skills
    When the device reconnects to the internet
    Then the profile syncs to the backend successfully
    And if a server-side change occurred more recently
    Then last-write-wins is applied and the final profile reflects the latest timestamp

  @should @jobs @FR-3.2.1
  Scenario: Browse and search job postings
    Given a seeded catalog of static job postings is available locally
    When the user opens the Jobs tab
    Then a list of job cards is shown with title, company, location, date
    When the user searches for "Software Engineer" in "Seattle"
    Then results include only matching jobs within 3 seconds

  @should @jobs @FR-3.2.2
  Scenario: Save a job and track application status
    Given a job detail is opened
    When the user taps Save
    Then the job appears in Saved Jobs with status "interested"
    When the user updates the status to "applied"
    Then the dashboard reflects the new status persistently

  @must @ai @pipeline @FR-3.3.1
  Scenario Outline: Generate a tailored resume via 5-stage pipeline
    Given a master profile exists with experiences, skills, and education
    And a job description is provided for generation
    When Stage 1 analyzes the job description to extract requirements and ATS keywords
    And Stage 2 scores profile sections by relevance on a 0-100 scale
    And Stage 3 rewrites content focusing on the highest scoring experiences and skills
    And Stage 4 validates ATS compatibility, grammar, dates, and section completeness
    And Stage 5 exports the content to PDF using the <template> template with <length> length
    Then the generated resume references only factual content from the master profile
    And the generated document is stored with metadata linking profile and job

    Examples:
      | template | length   |
      | ATS      | one-page |
      | Visual   | two-page |

  @must @ai @keywords @FR-3.3.2 @FR-3.3.4
  Scenario: ATS keyword coverage meets threshold
    Given Stage 1 produced a list of required and preferred keywords
    When the generated resume is validated in Stage 4
    Then at least 90% of required keywords appear naturally in the content
    And zero keyword stuffing is detected (no more than 2 repeats within a bullet)

  @must @ai @match-score @FR-3.3.3
  Scenario: Profile-job match score is calculated
    Given the profile and job are analyzed
    When scoring completes
    Then an overall match percentage between 0 and 100 is displayed
    And top 3 emphasis recommendations are shown to the user

  @should @docs @FR-3.4.1 @FR-3.4.3
  Scenario: Document history and version control
    Given at least two generations were produced for the same job
    When the user opens the document history
    Then the app shows all versions with timestamps and parameters
    And the user can compare two versions and restore a prior version

  @should @pdf @FR-3.4.2
  Scenario: View and share generated PDF
    Given a generated PDF exists
    When the user opens the document viewer
    Then the PDF renders within the app
    And the user can share the PDF via installed apps

  @must @nfr @performance @NFR-5.1
  Scenario: Resume generation performance targets
    Given the device is online and the backend is healthy
    When a generation request is submitted
    Then median end-to-end generation time is under 30 seconds
    And 95th percentile is under 60 seconds

  @must @nfr @reliability @NFR-5.2
  Scenario: Retry and graceful degradation on transient failures
    Given the AI provider returns a transient error
    When the backend retries with exponential backoff up to 3 attempts
    Then the request succeeds or a clear error is returned
    And the mobile app preserves user inputs and offers retry

  @must @nfr @data-integrity @NFR-5.2.3
  Scenario: Data validation and ACID for critical operations
    Given a profile update or document save is initiated
    When the backend processes the transaction
    Then inputs are validated server-side
    And the operation is committed atomically or rolled back on failure

  @should @security @privacy
  Scenario: Basic privacy and data retention
    Given a user deletes a generated document
    When the deletion is confirmed
    Then the document becomes inaccessible in the app immediately
    And the backend flags the document for deletion in archival storage within 24 hours

  @could @future @integration
  Scenario: External job API integration (post-MVP)
    Given valid API credentials
    When the system refreshes job listings from an external provider
    Then new jobs appear with source attribution
    And rate limiting is respected per provider policy
