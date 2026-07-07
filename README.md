# LA_Practice_APP

Learning Analytics Progression Dashboard for the Faculty of Economic and Management Sciences (EMS), University of the Western Cape.

The app turns assessment and progression data into decision-ready views for four audiences: the Dean and Deputy Deans, the Faculty Manager, module lecturers, and students. It tracks, as early as possible and again at the end of the assessment cycle, which students are not submitting assessments, which are failing, and how each student compares with their class and programme average.

## Pages

| Page | Audience | Purpose |
|---|---|---|
| Home | Everyone | What the app does and how to navigate it |
| Dean and Deputy Deans' View | Dean, Deputy Deans | Faculty-wide risk, equity and early-intervention picture |
| Faculty Manager View | Faculty Manager | Module and monitoring-point level operational detail, downloadable at-risk lists |
| Lecturer View | Module lecturers | Class progress, submission status, and a contact list for their module |
| Student View | Students | Personal progress against class and programme averages |
| Data Quality | Data owners | Live completeness, validity and consistency checks |
| Data Definitions | Everyone | Data dictionary and the methodology behind every flag and average |

## Data

The app reads two data files from `data/`:

- `programme_tracking.csv` — one row per student, with year-to-date credit completion, module and assessment counts, and an overall progression risk tier.
- `student_module_level.csv` — one row per student per assessment, with marks, submission status, class and programme benchmarks, and alert flags.

Replace these files with a refreshed extract to update the dashboard; column names must stay the same. Full field definitions are in the Data Definitions page.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploying to Streamlit Community Cloud

1. Push this repository to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), create a new app pointing to `app.py` in this repository.
3. If you want the AI-generated narratives (see below), add `ANTHROPIC_API_KEY` under the app's Secrets settings.

## AI-generated narratives (optional)

Each view includes a short narrative summary. By default this is generated from the same filtered statistics shown on the page, using plain rules, so the app works fully with no external dependency.

If an Anthropic API key is configured, a "Generate narrative with Claude" toggle becomes active on each page, which sends the current filtered summary statistics (not raw student data) to Claude to produce a more natural, audience-specific write-up.

To enable it:

- **Locally**: copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your key.
- **Streamlit Community Cloud**: add `ANTHROPIC_API_KEY` under the app's Secrets settings.

## Branding

Colours follow UWC brand guidance:

| Colour | Hex | Use |
|---|---|---|
| University Blue | `#0a1a5c` | Titles, headers, sidebar, primary data colour |
| University Gold | `#bd9a50` | Highlights, selected emphasis, secondary data colour |
| Mid Blue | `#385ba3` | Alternative series where contrast is needed |
| Light Grey | `#d1d1d1` | Neutral categories, gridlines, support text |
| Mid Grey | `#3c3c3e` | Neutral categories, gridlines, support text |
| Cream | `#faf6ed` | Subtle background panels |

## Repository structure

```
LA_Practice_APP/
├── app.py                     # Home page
├── pages/                     # One file per dashboard view (Streamlit multipage)
├── utils/
│   ├── data_loader.py         # Data loading, caching, shared sidebar filters
│   ├── styling.py             # Brand colours, header, footer, badges
│   └── narrative.py           # Rule-based and optional Claude-generated narratives
├── data/                      # Source data extracts
├── assets/                    # UWC logo
├── .streamlit/
│   ├── config.toml            # Theme colours
│   └── secrets.toml.example   # Template for the optional API key
├── requirements.txt
└── README.md
```

## Ownership

Institutional Planning, Business Intelligence, University of the Western Cape.
