# Medical Incident Reporting Dashboard

A data analysis and visualization project that generates an interactive dashboard for medical incident reports (אירועים חריגים). The dashboard analyzes reporting delays, regulatory compliance, and geographic distribution across Israeli healthcare districts.

## Prerequisites

- Python 3.10 or higher
- The input data file: `project_data.xlsx`

## Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Place the data file:**

All three scripts expect the Excel file at this path:

```
/Users/barnaor/Downloads/project_data.xlsx
```

If your file is in a different location, update the path in the script you want to run:
- `dashboard.py` — line 25 (`DATA_PATH`)
- `main.py` — line 24
- `presentation_graphs.py` — line 22

## Running the Dashboard

```bash
python dashboard.py
```

This generates all output files into the `output/` folder:

| File | Description |
|------|-------------|
| `dashboard_shareable.html` | **Self-contained dashboard** — open this in a browser. Contains all visualizations embedded in a single file. |
| `1_interactive_dashboard.html` | Interactive charts with dropdown filters for event type and district |
| `2_drilldown_heatmap.html` | Heatmap with selectable axes (profession, role, event type, age, gender) |
| `3_regulation_compliance.png` | Compliance rates — events (24h rule) vs. near-events (3-day rule) |
| `4_profession_delays.png` | Reporting delays broken down by profession and role |
| `5_external_reporting.png` | External reporting requirements (legal, insurance, ministry) |
| `6_event_types.png` | Distribution of main event types |
| `7_time_distribution.png` | Histogram of reporting delay times |
| `8_district_speed.png` | Average reporting speed by district |
| `9_district_volume.png` | Report volume by district |

To view the dashboard, open `output/dashboard_shareable.html` in any web browser.

## Additional Scripts

- `main.py` — generates a 4-chapter presentation analysis with static charts (matplotlib/seaborn)
- `presentation_graphs.py` — generates impact-focused presentation graphs (donut charts, statistics)

Both scripts output charts as images via `plt.show()`.

## Data Requirements

The Excel file (`project_data.xlsx`) should contain a sheet named `גיליון1` with the following columns:

- `מקצוע המדווח (לא תפקיד)*` — reporting profession
- `תפקיד המדווח` — reporting role
- `מתאריך האירוע לתאריך שליחת הדיווח` — days from event to report submission
- `מחוז*` — district
- `סוג אירוע ראשי*` — main event type
- `תאריך האירוע*` — event date
- `אירוע / כמעט אירוע` — event or near-event classification