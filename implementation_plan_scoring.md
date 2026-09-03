# Lead Scoring System Implementation Plan

This plan outlines how we will add an expert lead scoring system to evaluate barbershops for your WhatsApp scheduler bot.

## Proposed Changes

We will create a new script `score_leads.py` in your `D:\BarberData` directory.

### 1. Data Input
- The script will read your existing `barbers_tromso.csv`.

### 2. Review Scraping
- We will use Playwright to visit the `Google Maps URL` for each barbershop.
- The script will navigate to the "Reviews" tab and extract the text from the top 5-10 recent reviews.

### 3. Scoring Algorithm (1-100)
We will calculate a heuristic score based on the following rules (which mimic lead-generation expertise for SaaS products):

**Base Score:** 50
- **Existing System:** If `Has Booking System` is "No" -> **+30 points** (Prime target). If "Yes" -> **-30 points** (Harder to sell to, they already pay for a system like Timma/Fresha).
- **Phone Type:** If the phone number is a mobile number (starts with +47 4 or +47 9 in Norway) -> **+15 points** (Very easy to deploy WhatsApp Business). If landline -> **+0 points**.
- **Review Sentiment (Keywords):**
  - If reviews mention words like "wait", "queue", "vente", "kø", or "busy" -> **+15 points** (They have a traffic problem that a scheduler solves).
  - If reviews mention "drop-in" or "drop in" -> **+10 points** (A WA bot for drop-in queues is highly valuable).

**Final Score:** Will be capped between 1 (Worst Lead) and 100 (Best Lead).

### 4. Output
- The script will generate a new file `barbers_tromso_scored.csv` containing all original data plus two new columns: `Lead Score (1-100)` and `Review Summary` (a short note on why they scored that way).
- Finally, we will push the new script to your GitHub repository.

## Open Questions for User
> [!IMPORTANT]
> 1. Does the scoring formula above (rewarding mobile numbers, lack of existing systems, and busy queues) align with your sales strategy?
> 2. Because of the `C:` drive being completely full (0 bytes free), I am writing this plan to your `D:` drive instead of the standard Gemini planning interface. Please review this plan and reply with **"Approve"** so I can begin writing and executing the code on your `D:` drive!
