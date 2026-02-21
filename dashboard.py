"""
Medical Incident Reporting Dashboard
=====================================
6 visualizations with interactive features:
- Clickable map with district filtering
- Heatmaps, gauges, and varied chart types
- Regulation compliance analysis
- Data: January-June 2025 only
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from bidi.algorithm import get_display
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ============================================================================
# CONFIGURATION
# ============================================================================
OUTPUT_DIR = '/Users/barnaor/PycharmProjects/PythonProject/output'
DATA_PATH = '/Users/barnaor/Downloads/project_data.xlsx'

# Column names
W = 'מקצוע המדווח (לא תפקיד)*'
ROLE = 'תפקיד המדווח'
AE = 'מתאריך האירוע לתאריך שליחת הדיווח'
DISTRICT = 'מחוז*'
EVENT_TYPE = 'סוג אירוע ראשי*'
EVENT_DATE = 'תאריך האירוע*'
EVENT_OR_NEAR = 'אירוע / כמעט אירוע'
LEGAL = 'להעביר ליועמ"ש'
INSURANCE = 'צורך בדיווח לחברת ביטוח?'
HEALTH_MINISTRY = 'צורך בדיווח למשרד הבריאות?'
FOLLOW_UP = 'נדרש המשך טיפול של מנהל הסיכונים?'
ANONYMOUS = 'דיווח אנונימי ?'
BIRTH_YEAR = 'שנת לידה הנפגע/הנשוא'
GENDER = 'פריט אב-מין הנפגע/ הנשוא'

# Colors
COLORS = {
    'danger': '#E74C3C',
    'warning': '#F39C12',
    'success': '#27AE60',
    'info': '#3498DB',
    'primary': '#2C3E50',
    'light': '#ECF0F1',
    'event': '#E74C3C',
    'near_event': '#3498DB',
    'purple': '#9B59B6'
}

# District data with actual population (מספר מבוטחים)
DISTRICT_DATA = {
    'מחוז ירושלים': {'lat': 31.7683, 'lon': 35.2137, 'name': 'ירושלים', 'population': 333000},
    'מחוז צפון': {'lat': 32.8191, 'lon': 35.5678, 'name': 'צפון', 'population': 200000},
    'מחוז דרום': {'lat': 31.2529, 'lon': 34.7915, 'name': 'דרום', 'population': 200000},
    'מחוז מרכז': {'lat': 32.0853, 'lon': 34.7818, 'name': 'מרכז', 'population': 267000},
    'ירושלים': {'lat': 31.7683, 'lon': 35.2137, 'name': 'ירושלים', 'population': 333000},
    'צפון': {'lat': 32.8191, 'lon': 35.5678, 'name': 'צפון', 'population': 200000},
    'דרום': {'lat': 31.2529, 'lon': 34.7915, 'name': 'דרום', 'population': 200000},
    'מרכז': {'lat': 32.0853, 'lon': 34.7818, 'name': 'מרכז', 'population': 267000}
}

def fix_hebrew(text):
    """Fix Hebrew text for matplotlib RTL display"""
    return get_display(str(text))

def create_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    create_output_dir()

    # Load data
    print("Loading data...")
    df = pd.read_excel(DATA_PATH, sheet_name='גיליון1')

    # Clean data
    df_clean = df[(df[AE].isna()) | ((df[AE] >= 0) & (df[AE] <= 365))].copy()

    # FILTER: January-June 2025 only
    print("Filtering data to January-June 2025...")
    df_clean = df_clean[df_clean[EVENT_DATE].notna()].copy()
    df_clean = df_clean[
        (df_clean[EVENT_DATE].dt.year == 2025) &
        (df_clean[EVENT_DATE].dt.month >= 1) &
        (df_clean[EVENT_DATE].dt.month <= 6)
    ].copy()

    # Fill empty EVENT_OR_NEAR with "כמעט אירוע"
    df_clean[EVENT_OR_NEAR] = df_clean[EVENT_OR_NEAR].fillna('כמעט אירוע')
    df_clean.loc[df_clean[EVENT_OR_NEAR] == '', EVENT_OR_NEAR] = 'כמעט אירוע'

    df_ae_valid = df_clean[AE].dropna()
    total_records = len(df_clean)

    print(f"Records after filtering (Jan-June 2025): {total_records}")

    # Calculate average reports per month (for stats bar)
    monthly_counts = df_clean.groupby(df_clean[EVENT_DATE].dt.to_period('M')).size()
    avg_reports_per_month = round(monthly_counts.mean())

    # Style setup for matplotlib
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 16

    # ========================================================================
    # GRAPH 1: INTERACTIVE DASHBOARD WITH EVENT TYPE + DISTRICT FILTERS
    # ========================================================================
    print("\n1. Creating interactive dashboard with event type and district filters...")

    # Prepare data
    df_interactive = df_clean.copy()
    df_interactive['month'] = df_interactive[EVENT_DATE].dt.strftime('%Y-%m')

    main_districts = ['מחוז ירושלים', 'מחוז צפון', 'מחוז דרום', 'מחוז מרכז',
                      'ירושלים', 'צפון', 'דרום', 'מרכז']
    df_interactive = df_interactive[df_interactive[DISTRICT].isin(main_districts)].copy()

    df_interactive['district_name'] = df_interactive[DISTRICT].map(
        lambda x: DISTRICT_DATA.get(x, {}).get('name', x)
    )
    df_interactive['population'] = df_interactive[DISTRICT].map(
        lambda x: DISTRICT_DATA.get(x, {}).get('population', 200000)
    )

    # Get unique districts
    unique_districts = sorted(df_interactive['district_name'].dropna().unique().tolist())

    # Calculate compliance rate
    df_compliance = df_interactive[[EVENT_OR_NEAR, AE]].dropna()
    events_compliant = ((df_compliance[EVENT_OR_NEAR] == 'אירוע') & (df_compliance[AE] <= 1)).sum()
    events_total_comp = (df_compliance[EVENT_OR_NEAR] == 'אירוע').sum()
    near_compliant = ((df_compliance[EVENT_OR_NEAR] == 'כמעט אירוע') & (df_compliance[AE] <= 3)).sum()
    near_total_comp = (df_compliance[EVENT_OR_NEAR] == 'כמעט אירוע').sum()
    total_compliant = events_compliant + near_compliant
    total_with_delay = events_total_comp + near_total_comp
    compliance_rate = round(total_compliant / total_with_delay * 100) if total_with_delay > 0 else 0

    # Create all filter combinations: Event Type x District
    event_type_filters = [
        ('כל הסוגים', None),
        ('אירוע בלבד', 'אירוע'),
        ('כמעט אירוע בלבד', 'כמעט אירוע')
    ]
    district_filters = [('כל המחוזות', None)] + [(d, d) for d in unique_districts]

    # Generate all combinations
    filter_configs = []
    for evt_name, evt_val in event_type_filters:
        for dist_name, dist_val in district_filters:
            df_f = df_interactive.copy()
            if evt_val:
                df_f = df_f[df_f[EVENT_OR_NEAR] == evt_val]
            if dist_val:
                df_f = df_f[df_f['district_name'] == dist_val]
            filter_configs.append((evt_name, dist_name, evt_val, dist_val, df_f))

    fig_dashboard = make_subplots(
        rows=2, cols=2,
        specs=[
            [{"type": "scatter"}, {"type": "scattermap"}],
            [{"type": "indicator"}, {"type": "bar"}]
        ],
        subplot_titles=(
            '<b>מגמת דיווחים לאורך זמן</b>',
            '<b>מפת דיווחים לפי מחוז (מנורמל לאוכלוסייה)</b>',
            '<b>שיעור עמידה ברגולציה</b>',
            '<b>ממוצע ימי דיווח לפי מקצוע</b>'
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.08
    )

    trace_indices = {'timeline_event': [], 'timeline_near': [], 'map': [], 'gauge': [], 'bar': []}

    for filter_idx, (evt_name, dist_name, evt_val, dist_val, df_filtered) in enumerate(filter_configs):
        is_visible = filter_idx == 0  # Only first combination is visible initially

        # Timeline data
        if len(df_filtered) > 0:
            monthly_data = df_filtered.groupby(['month', EVENT_OR_NEAR]).size().unstack(fill_value=0)
        else:
            monthly_data = pd.DataFrame()

        # Determine which lines to show based on event type filter
        show_event_line = evt_val != 'כמעט אירוע'
        show_near_line = evt_val != 'אירוע'

        # Event timeline
        if show_event_line and len(monthly_data) > 0 and 'אירוע' in monthly_data.columns:
            event_x = monthly_data.index.tolist()
            event_y = monthly_data['אירוע'].values.tolist()
        else:
            event_x, event_y = [], []

        fig_dashboard.add_trace(
            go.Scatter(
                x=event_x, y=event_y,
                name='אירוע',
                mode='lines+markers',
                line=dict(color=COLORS['event'], width=3),
                marker=dict(size=10),
                legendgroup='events',
                showlegend=(filter_idx == 0 and show_event_line),
                visible=is_visible
            ),
            row=1, col=1
        )
        trace_indices['timeline_event'].append(len(fig_dashboard.data) - 1)

        # Near-event timeline
        if show_near_line and len(monthly_data) > 0 and 'כמעט אירוע' in monthly_data.columns:
            near_x = monthly_data.index.tolist()
            near_y = monthly_data['כמעט אירוע'].values.tolist()
        else:
            near_x, near_y = [], []

        fig_dashboard.add_trace(
            go.Scatter(
                x=near_x, y=near_y,
                name='כמעט אירוע',
                mode='lines+markers',
                line=dict(color=COLORS['near_event'], width=3),
                marker=dict(size=10),
                legendgroup='near_events',
                showlegend=(filter_idx == 0 and show_near_line),
                visible=is_visible
            ),
            row=1, col=1
        )
        trace_indices['timeline_near'].append(len(fig_dashboard.data) - 1)

        # Map data
        if len(df_filtered) > 0:
            district_stats = df_filtered.groupby('district_name').agg({
                'population': 'first'
            }).reset_index()
            district_counts = df_filtered.groupby('district_name').size().reset_index(name='count')
            district_stats = district_stats.merge(district_counts, on='district_name', how='left').fillna(0)
            district_stats['reports_per_1000'] = (district_stats['count'] / district_stats['population'] * 1000).round(2)
            district_stats['lat'] = district_stats['district_name'].map(
                lambda x: DISTRICT_DATA.get(x, DISTRICT_DATA.get('מחוז ' + x, {})).get('lat', 31.5)
            )
            district_stats['lon'] = district_stats['district_name'].map(
                lambda x: DISTRICT_DATA.get(x, DISTRICT_DATA.get('מחוז ' + x, {})).get('lon', 35.0)
            )
            # Size based on normalized value (reports_per_1000) - bigger = more normalized reports
            max_norm = district_stats['reports_per_1000'].max() if district_stats['reports_per_1000'].max() > 0 else 1
            sizes = [max(20, min(60, (r / max_norm) * 60)) for r in district_stats['reports_per_1000']]
            # Color based on absolute count
            max_count = district_stats['count'].max() if district_stats['count'].max() > 0 else 1
            colors_map = [COLORS['success'] if c / max_count <= 0.33 else COLORS['warning'] if c / max_count <= 0.66 else COLORS['danger']
                          for c in district_stats['count']]
        else:
            district_stats = pd.DataFrame(columns=['district_name', 'lat', 'lon', 'count', 'population', 'reports_per_1000'])
            sizes, colors_map = [], []

        fig_dashboard.add_trace(
            go.Scattermap(
                lat=district_stats['lat'].tolist() if len(district_stats) > 0 else [],
                lon=district_stats['lon'].tolist() if len(district_stats) > 0 else [],
                mode='markers+text',
                marker=dict(size=sizes, color=colors_map, opacity=0.8),
                text=district_stats['district_name'].tolist() if len(district_stats) > 0 else [],
                textposition='top center',
                textfont=dict(size=14, color='black'),
                hovertemplate=[
                    f"<b>{row['district_name']}</b><br>" +
                    f"דיווחים: {int(row['count'])}<br>" +
                    f"מבוטחים: {int(row['population']):,}<br>" +
                    f"דיווחים ל-1000: {row['reports_per_1000']:.2f}<extra></extra>"
                    for _, row in district_stats.iterrows()
                ] if len(district_stats) > 0 else [],
                showlegend=False,
                visible=is_visible
            ),
            row=1, col=2
        )
        trace_indices['map'].append(len(fig_dashboard.data) - 1)

        # Gauge - compliance for this filter
        df_comp_f = df_filtered[[EVENT_OR_NEAR, AE]].dropna() if len(df_filtered) > 0 else pd.DataFrame()
        if len(df_comp_f) > 0:
            if evt_val == 'אירוע':
                comp_rate = round(((df_comp_f[AE] <= 1).sum() / len(df_comp_f)) * 100)
            elif evt_val == 'כמעט אירוע':
                comp_rate = round(((df_comp_f[AE] <= 3).sum() / len(df_comp_f)) * 100)
            else:
                ev_comp = ((df_comp_f[EVENT_OR_NEAR] == 'אירוע') & (df_comp_f[AE] <= 1)).sum()
                near_comp = ((df_comp_f[EVENT_OR_NEAR] == 'כמעט אירוע') & (df_comp_f[AE] <= 3)).sum()
                comp_rate = round((ev_comp + near_comp) / len(df_comp_f) * 100)
        else:
            comp_rate = 0

        fig_dashboard.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=comp_rate,
                number={'suffix': '%', 'font': {'size': 36}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1},
                    'bar': {'color': COLORS['success'] if comp_rate >= 70 else COLORS['warning'] if comp_rate >= 50 else COLORS['danger']},
                    'bgcolor': 'white',
                    'steps': [
                        {'range': [0, 50], 'color': '#ffebee'},
                        {'range': [50, 70], 'color': '#fff8e1'},
                        {'range': [70, 100], 'color': '#e8f5e9'}
                    ],
                    'threshold': {'line': {'color': 'black', 'width': 2}, 'thickness': 0.75, 'value': 70}
                },
                visible=is_visible
            ),
            row=2, col=1
        )
        trace_indices['gauge'].append(len(fig_dashboard.data) - 1)

        # Bar chart - profession delays for this filter
        prof_delay = df_filtered.groupby(W)[AE].mean().dropna().sort_values().head(8)
        if len(prof_delay) > 0:
            colors_prof = [COLORS['success'] if v <= 1 else COLORS['warning'] if v <= 3 else COLORS['danger']
                           for v in prof_delay.values]
            fig_dashboard.add_trace(
                go.Bar(
                    y=prof_delay.index.tolist(),
                    x=prof_delay.values,
                    orientation='h',
                    marker_color=colors_prof,
                    text=[f'{v:.1f}' for v in prof_delay.values],
                    textposition='outside',
                    textfont=dict(size=12),
                    showlegend=False,
                    visible=is_visible
                ),
                row=2, col=2
            )
            trace_indices['bar'].append(len(fig_dashboard.data) - 1)
        else:
            # Empty bar if no data
            fig_dashboard.add_trace(
                go.Bar(y=[], x=[], orientation='h', showlegend=False, visible=is_visible),
                row=2, col=2
            )
            trace_indices['bar'].append(len(fig_dashboard.data) - 1)

    # Create filter buttons - two separate dropdowns
    total_traces = len(fig_dashboard.data)
    n_event_types = len(event_type_filters)
    n_districts = len(district_filters)

    # Event type dropdown buttons
    event_buttons = []
    for evt_idx, (evt_name, evt_val) in enumerate(event_type_filters):
        # Show all combinations for this event type (across all districts)
        # Default to first district (all districts)
        target_idx = evt_idx * n_districts  # Index of first district with this event type
        visibility = [False] * total_traces
        for key in trace_indices:
            if target_idx < len(trace_indices[key]):
                visibility[trace_indices[key][target_idx]] = True
        event_buttons.append(dict(
            label=evt_name,
            method='update',
            args=[{'visible': visibility}]
        ))

    # District dropdown buttons
    district_buttons = []
    for dist_idx, (dist_name, dist_val) in enumerate(district_filters):
        # Default to first event type (all types)
        target_idx = dist_idx  # Index with "all event types" and this district
        visibility = [False] * total_traces
        for key in trace_indices:
            if target_idx < len(trace_indices[key]):
                visibility[trace_indices[key][target_idx]] = True
        district_buttons.append(dict(
            label=dist_name,
            method='update',
            args=[{'visible': visibility}]
        ))

    # Update subplot title annotations to be more visible
    fig_dashboard.update_annotations(font=dict(size=16, family='David, Arial', color='#2C3E50'))

    # Get existing annotations (subplot titles) and add filter labels to them
    existing_annotations = list(fig_dashboard.layout.annotations)

    # Add filter dropdown labels
    filter_annotations = [
        dict(text='<b>סוג אירוע</b>', x=0.78, y=1.15,
             xref='paper', yref='paper', showarrow=False, font=dict(size=12), xanchor='right'),
        dict(text='<b>מחוז</b>', x=0.92, y=1.15,
             xref='paper', yref='paper', showarrow=False, font=dict(size=12), xanchor='right')
    ]

    all_annotations = existing_annotations + filter_annotations

    fig_dashboard.update_layout(
        map=dict(style='carto-positron', center=dict(lat=31.5, lon=35.0), zoom=6.2),
        height=980,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.25),
        font=dict(family='David, Arial', size=13),
        title=dict(
            text=f'<b>דשבורד אינטראקטיבי - דיווחי אירועים רפואיים</b><br><sub>מתוך {total_records} דיווחים | ינואר-יוני 2025</sub>',
            font=dict(size=20), x=0.5
        ),
        margin=dict(t=160, b=50, l=50, r=50),
        updatemenus=[
            dict(
                buttons=event_buttons,
                direction='down',
                showactive=True,
                x=0.70, xanchor='right',
                y=1.12, yanchor='top',
                bgcolor='white', bordercolor='gray',
                font=dict(size=12)
            ),
            dict(
                buttons=district_buttons,
                direction='down',
                showactive=True,
                x=0.92, xanchor='right',
                y=1.12, yanchor='top',
                bgcolor='white', bordercolor='gray',
                font=dict(size=12)
            )
        ],
        annotations=all_annotations
    )

    fig_dashboard.write_html(f'{OUTPUT_DIR}/1_interactive_dashboard.html')
    print(f"   Saved: {OUTPUT_DIR}/1_interactive_dashboard.html")

    # ========================================================================
    # GRAPH 2: HEATMAP WITH AXIS SELECTION DROPDOWN (HTML)
    # ========================================================================
    print("\n2. Creating heatmap with axis selection dropdown...")

    # Prepare heatmap data with all needed columns
    df_heatmap = df_clean.copy()

    # Add district_name column
    main_districts = ['מחוז ירושלים', 'מחוז צפון', 'מחוז דרום', 'מחוז מרכז',
                      'ירושלים', 'צפון', 'דרום', 'מרכז']
    df_heatmap = df_heatmap[df_heatmap[DISTRICT].isin(main_districts)].copy()
    df_heatmap['district_name'] = df_heatmap[DISTRICT].map(
        lambda x: DISTRICT_DATA.get(x, {}).get('name', x)
    )
    df_heatmap['population'] = df_heatmap[DISTRICT].map(
        lambda x: DISTRICT_DATA.get(x, {}).get('population', 200000)
    )

    # Add anonymous column (empty = לא)
    df_heatmap['anonymous_display'] = df_heatmap[ANONYMOUS].fillna('לא')
    df_heatmap.loc[df_heatmap['anonymous_display'] == '', 'anonymous_display'] = 'לא'

    # Create age bins from birth year (current year = 2025)
    current_year = 2025
    df_heatmap['age'] = current_year - df_heatmap[BIRTH_YEAR]
    df_heatmap['age_group'] = pd.cut(
        df_heatmap['age'],
        bins=[0, 18, 30, 45, 60, 75, 120],
        labels=['0-18', '19-30', '31-45', '46-60', '61-75', '76+'],
        right=True
    )

    # Get top values for filtering
    top_roles = df_heatmap[ROLE].value_counts().head(8).index.tolist()
    top_districts = df_heatmap['district_name'].dropna().value_counts().head(6).index.tolist() if 'district_name' in df_heatmap.columns else []

    # District population for normalization
    district_pop = {d: DISTRICT_DATA.get(d, DISTRICT_DATA.get('מחוז ' + d, {})).get('population', 200000)
                    for d in top_districts}

    # Heatmap configurations:
    # 1. תפקיד × מחוז (מנורמל)
    # 2. תפקיד × סוג אירוע
    # 3. גיל הנפגע × מין הנפגע
    heatmap_configs = {
        'תפקיד × מחוז (מנורמל)': (ROLE, 'district_name', top_roles, top_districts, 'תפקיד המדווח', 'מחוז', True),
        'תפקיד × סוג אירוע': (ROLE, EVENT_OR_NEAR, top_roles, ['אירוע', 'כמעט אירוע'], 'תפקיד המדווח', 'סוג אירוע', False),
        'גיל הנפגע × מין הנפגע': ('age_group', GENDER, ['0-18', '19-30', '31-45', '46-60', '61-75', '76+'], ['זכר', 'נקבה'], 'קבוצת גיל', 'מין הנפגע', False)
    }

    fig_heatmap = go.Figure()

    # Add traces for each configuration
    first = True
    for config_name, (row_col, col_col, row_filter, col_filter, y_title, x_title, normalize_by_district) in heatmap_configs.items():
        heatmap_data = pd.crosstab(df_heatmap[row_col], df_heatmap[col_col])
        heatmap_filtered = heatmap_data.loc[
            heatmap_data.index.isin(row_filter),
            heatmap_data.columns.isin(col_filter)
        ].copy()

        # Store original counts before normalization
        original_counts = heatmap_filtered.copy()

        # Normalize by district population if needed (per 1000 insured)
        if normalize_by_district and col_col == 'district_name':
            for col in heatmap_filtered.columns:
                pop = district_pop.get(col, 200000)
                heatmap_filtered[col] = (heatmap_filtered[col] / pop * 1000).round(2)

        # Custom text: hide zeros, show normalized + (actual) for normalized views
        if normalize_by_district:
            text_values = []
            for i, row in enumerate(heatmap_filtered.values):
                text_row = []
                for j, v in enumerate(row):
                    orig = int(original_counts.iloc[i, j])
                    if v == 0 or orig == 0:
                        text_row.append('')
                    else:
                        text_row.append(f'{v:.2f} ({orig})')
                text_values.append(text_row)
            hover_template = f'{y_title}: %{{y}}<br>{x_title}: %{{x}}<br>ל-1000 מבוטחים: %{{z:.2f}}<extra></extra>'
            colorbar_title = 'ל-1000'
        else:
            text_values = [['' if v == 0 else str(int(v)) for v in row] for row in heatmap_filtered.values]
            hover_template = f'{y_title}: %{{y}}<br>{x_title}: %{{x}}<br>כמות: %{{z}}<extra></extra>'
            colorbar_title = 'כמות'

        fig_heatmap.add_trace(go.Heatmap(
            z=heatmap_filtered.values,
            x=heatmap_filtered.columns.tolist(),
            y=heatmap_filtered.index.tolist(),
            colorscale=[
                [0, '#f5f5f5'],
                [0.1, '#fff3e0'],
                [0.3, '#ffcc80'],
                [0.5, '#ff9800'],
                [0.7, '#f57c00'],
                [1, '#e65100']
            ],
            text=text_values,
            texttemplate='%{text}',
            textfont=dict(size=12, color='black'),
            hovertemplate=hover_template,
            showscale=True,
            colorbar=dict(title=colorbar_title),
            visible=first,
            name=config_name
        ))
        first = False

    # Create dropdown buttons
    buttons = []
    for i, (config_name, (_, _, _, _, y_title, x_title, _)) in enumerate(heatmap_configs.items()):
        visibility = [j == i for j in range(len(heatmap_configs))]
        buttons.append(dict(
            label=config_name,
            method='update',
            args=[
                {'visible': visibility},
                {'title': f'<b>מפת חום: {config_name}</b>',
                 'xaxis.title.text': x_title,
                 'yaxis.title.text': y_title}
            ]
        ))

    fig_heatmap.update_layout(
        title=dict(
            text='<b>מפת חום: תפקיד × מחוז (מנורמל)</b>',
            font=dict(size=20, family='David, Arial'),
            x=0.5
        ),
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            direction='down',
            showactive=True,
            x=0.18,
            xanchor='right',
            y=1.12,
            yanchor='top',
            bgcolor='white',
            bordercolor='gray',
            font=dict(size=13)
        )],
        annotations=[dict(
            text='<b>בחר צירים</b>',
            x=0.18, y=1.16,
            xref='paper', yref='paper',
            xanchor='right',
            showarrow=False,
            font=dict(size=14)
        )],
        xaxis=dict(
            title=dict(text='מחוז', font=dict(size=14)),
            tickfont=dict(size=11),
            tickangle=45
        ),
        yaxis=dict(
            title=dict(text='תפקיד המדווח', font=dict(size=14)),
            tickfont=dict(size=11)
        ),
        height=750,
        font=dict(family='David, Arial'),
        margin=dict(l=200, r=50, t=130, b=120)
    )

    fig_heatmap.write_html(f'{OUTPUT_DIR}/2_drilldown_heatmap.html')
    print(f"   Saved: {OUTPUT_DIR}/2_drilldown_heatmap.html")

    # ========================================================================
    # GRAPH 3: DUAL BAR CHART - REGULATION COMPLIANCE (PNG)
    # Two side-by-side charts: Events and Near-events
    # X-axis: up to 24h, 24h-3d, over 3d
    # Color: green=compliant, red=not compliant
    # ========================================================================
    print("\n3. Creating dual bar chart for regulation compliance...")

    fig3, axes = plt.subplots(1, 2, figsize=(16, 8), facecolor='white')

    df_delay = df_clean[[EVENT_OR_NEAR, AE]].dropna().copy()

    # Categories
    categories = [
        fix_hebrew('עד 24 שעות'),
        fix_hebrew('24 שעות - 3 ימים'),
        fix_hebrew('מעל 3 ימים')
    ]

    # For Events (אירוע) - regulation is 24 hours
    events_df = df_delay[df_delay[EVENT_OR_NEAR] == 'אירוע']
    events_up_to_24h = (events_df[AE] <= 1).sum()
    events_24h_to_3d = ((events_df[AE] > 1) & (events_df[AE] <= 3)).sum()
    events_over_3d = (events_df[AE] > 3).sum()
    events_values = [events_up_to_24h, events_24h_to_3d, events_over_3d]
    events_total = sum(events_values)

    # Colors for events: only up to 24h is compliant (green), rest is red
    events_colors = [COLORS['success'], COLORS['danger'], COLORS['danger']]

    # For Near-events (כמעט אירוע) - regulation is 3 days
    near_df = df_delay[df_delay[EVENT_OR_NEAR] == 'כמעט אירוע']
    near_up_to_24h = (near_df[AE] <= 1).sum()
    near_24h_to_3d = ((near_df[AE] > 1) & (near_df[AE] <= 3)).sum()
    near_over_3d = (near_df[AE] > 3).sum()
    near_values = [near_up_to_24h, near_24h_to_3d, near_over_3d]
    near_total = sum(near_values)

    # Colors for near-events: up to 3d is compliant (green), over 3d is red
    near_colors = [COLORS['success'], COLORS['success'], COLORS['danger']]

    # Plot Events
    ax1 = axes[0]
    x_pos = np.arange(len(categories))
    bars1 = ax1.bar(x_pos, events_values, color=events_colors, edgecolor='white', width=0.6)

    for i, (bar, val) in enumerate(zip(bars1, events_values)):
        if val > 0:
            pct = round(val / events_total * 100) if events_total > 0 else 0
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{val}\n({pct}%)', ha='center', va='bottom',
                    fontsize=14, fontweight='bold', color=COLORS['primary'])

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(categories, fontsize=12)
    ax1.set_ylabel(fix_hebrew('מספר דיווחים'), fontsize=14, fontweight='bold')
    ax1.set_title(f'{fix_hebrew("אירוע חריג")}\n{fix_hebrew("רגולציה: עד 24 שעות")}\n{fix_hebrew(f"(מתוך {events_total})")}',
                  fontsize=16, fontweight='bold', pad=10)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Add compliance rate for events
    events_compliant = events_up_to_24h
    events_compliance_rate = round(events_compliant / events_total * 100) if events_total > 0 else 0
    ax1.text(0.5, 0.95, f'{fix_hebrew("עמידה ברגולציה:")} {events_compliance_rate}%',
             transform=ax1.transAxes, fontsize=14, ha='center', fontweight='bold',
             color=COLORS['success'] if events_compliance_rate >= 70 else COLORS['danger'])

    # Plot Near-events
    ax2 = axes[1]
    bars2 = ax2.bar(x_pos, near_values, color=near_colors, edgecolor='white', width=0.6)

    for i, (bar, val) in enumerate(zip(bars2, near_values)):
        if val > 0:
            pct = round(val / near_total * 100) if near_total > 0 else 0
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{val}\n({pct}%)', ha='center', va='bottom',
                    fontsize=14, fontweight='bold', color=COLORS['primary'])

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(categories, fontsize=12)
    ax2.set_ylabel(fix_hebrew('מספר דיווחים'), fontsize=14, fontweight='bold')
    ax2.set_title(f'{fix_hebrew("כמעט אירוע")}\n{fix_hebrew("רגולציה: עד 3 ימים")}\n{fix_hebrew(f"(מתוך {near_total})")}',
                  fontsize=16, fontweight='bold', pad=10)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # Add compliance rate for near-events
    near_compliant = near_up_to_24h + near_24h_to_3d
    near_compliance_rate = round(near_compliant / near_total * 100) if near_total > 0 else 0
    ax2.text(0.5, 0.95, f'{fix_hebrew("עמידה ברגולציה:")} {near_compliance_rate}%',
             transform=ax2.transAxes, fontsize=14, ha='center', fontweight='bold',
             color=COLORS['success'] if near_compliance_rate >= 70 else COLORS['danger'])

    # Set same y-axis scale for both charts for fair comparison
    max_y_value = max(max(events_values), max(near_values))
    y_limit = max_y_value * 1.25  # Add 25% padding for labels
    ax1.set_ylim(0, y_limit)
    ax2.set_ylim(0, y_limit)

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLORS['success'], label=fix_hebrew('עומד ברגולציה')),
        mpatches.Patch(color=COLORS['danger'], label=fix_hebrew('חורג מהרגולציה'))
    ]
    fig3.legend(handles=legend_elements, loc='upper center', ncol=2, fontsize=12,
                bbox_to_anchor=(0.5, 0.02))

    plt.suptitle(fix_hebrew('עמידה ברגולציה לפי סוג אירוע וזמן דיווח'),
                 fontsize=20, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/3_regulation_compliance.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   Saved: {OUTPUT_DIR}/3_regulation_compliance.png")

    # ========================================================================
    # GRAPH 4: PROFESSION DELAYS - STACKED BAR (EVENT VS NEAR-EVENT)
    # ========================================================================
    print("\n4. Creating profession delay stacked bar chart...")

    fig4, ax4 = plt.subplots(figsize=(14, 10), facecolor='white')

    df_prof = df_clean[[W, AE, EVENT_OR_NEAR]].dropna()

    # Calculate mean delay by profession and event type
    prof_event = df_prof[df_prof[EVENT_OR_NEAR] == 'אירוע'].groupby(W)[AE].mean()
    prof_near = df_prof[df_prof[EVENT_OR_NEAR] == 'כמעט אירוע'].groupby(W)[AE].mean()

    # Get all professions with at least 5 reports
    prof_counts = df_prof.groupby(W).size()
    valid_profs = prof_counts[prof_counts >= 5].index.tolist()

    # Create dataframe with both types
    prof_data = pd.DataFrame({
        'אירוע': prof_event,
        'כמעט אירוע': prof_near
    }).fillna(0)
    prof_data = prof_data[prof_data.index.isin(valid_profs)]

    # Sort by total average
    prof_data['total'] = prof_data['אירוע'] + prof_data['כמעט אירוע']
    prof_data = prof_data.sort_values('total', ascending=True)
    prof_data = prof_data.drop('total', axis=1)

    y_pos = np.arange(len(prof_data))
    bar_height = 0.35

    # Stacked horizontal bars
    bars_event = ax4.barh(y_pos + bar_height/2, prof_data['אירוע'], height=bar_height,
                          color=COLORS['event'], label=fix_hebrew('אירוע'), edgecolor='white')
    bars_near = ax4.barh(y_pos - bar_height/2, prof_data['כמעט אירוע'], height=bar_height,
                         color=COLORS['near_event'], label=fix_hebrew('כמעט אירוע'), edgecolor='white')

    # Add value labels (positioned to avoid overlap)
    for i, (ev, near) in enumerate(zip(prof_data['אירוע'], prof_data['כמעט אירוע'])):
        if ev > 0:
            ax4.text(ev + 0.15, i + bar_height/2, f'{ev:.1f}', va='center', ha='left',
                    fontsize=10, fontweight='bold', color=COLORS['event'])
        if near > 0:
            ax4.text(near + 0.15, i - bar_height/2, f'{near:.1f}', va='center', ha='left',
                    fontsize=10, fontweight='bold', color=COLORS['near_event'])

    # Regulation lines
    ax4.axvline(1, color=COLORS['success'], linestyle='--', linewidth=3, alpha=0.8)
    ax4.axvline(3, color=COLORS['warning'], linestyle='--', linewidth=3, alpha=0.8)

    # Place regulation labels at staggered heights to avoid overlap
    ax4.text(1, len(prof_data) + 0.5, fix_hebrew('רגולציה אירוע: 24 שעות'), fontsize=10,
             color=COLORS['success'], fontweight='bold', ha='center')
    ax4.text(3, len(prof_data) + 0.9, fix_hebrew('רגולציה כמעט אירוע: 3 ימים'), fontsize=10,
             color=COLORS['warning'], fontweight='bold', ha='center')

    ax4.set_yticks(y_pos)
    ax4.set_yticklabels([fix_hebrew(str(x)) for x in prof_data.index], fontsize=12)
    ax4.set_xlabel(fix_hebrew('ממוצע ימים מאירוע לדיווח'), fontsize=14, fontweight='bold')

    max_val = max(prof_data['אירוע'].max(), prof_data['כמעט אירוע'].max())
    ax4.set_xlim(0, max_val + 3)
    ax4.set_ylim(-0.5, len(prof_data) + 1.3)

    ax4.set_title(fix_hebrew('זמן דיווח לפי מקצוע המדווח - אירוע לעומת כמעט אירוע'),
                  fontsize=18, fontweight='bold', pad=20)

    ax4.legend(loc='lower right', fontsize=13, frameon=True)

    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/4_profession_delays.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   Saved: {OUTPUT_DIR}/4_profession_delays.png")

    # ========================================================================
    # GRAPH 5: EXTERNAL REPORTING (PNG)
    # ========================================================================
    print("\n5. Creating external reporting chart...")

    fig5, ax5 = plt.subplots(figsize=(12, 10), facecolor='white')

    df_ext = df_clean.copy()
    df_ext['needs_legal'] = df_ext[LEGAL].fillna('').astype(str).str.contains('כן|yes', case=False, na=False)
    df_ext['needs_insurance'] = df_ext[INSURANCE].fillna('').astype(str).str.contains('כן|yes', case=False, na=False)
    df_ext['needs_health_ministry'] = df_ext[HEALTH_MINISTRY].fillna('').astype(str).str.contains('כן|yes', case=False, na=False)

    categories = [
        (fix_hebrew('יועמ"ש'), 'needs_legal'),
        (fix_hebrew('חברת ביטוח'), 'needs_insurance'),
        (fix_hebrew('משרד הבריאות'), 'needs_health_ministry')
    ]

    events_counts = []
    near_events_counts = []

    for _, col in categories:
        df_filtered = df_ext[df_ext[col]]
        event_count = (df_filtered[EVENT_OR_NEAR] == 'אירוע').sum()
        near_event_count = (df_filtered[EVENT_OR_NEAR] == 'כמעט אירוע').sum()
        events_counts.append(event_count)
        near_events_counts.append(near_event_count)

    x_pos = np.arange(len(categories))
    width = 0.7

    bars_events = ax5.bar(x_pos, events_counts, width, label=fix_hebrew('אירוע'),
                          color=COLORS['event'], edgecolor=COLORS['event'])
    bars_near = ax5.bar(x_pos, near_events_counts, width, bottom=events_counts,
                        label=fix_hebrew('כמעט אירוע'), color=COLORS['near_event'],
                        edgecolor=COLORS['near_event'])

    for i, (ev, near) in enumerate(zip(events_counts, near_events_counts)):
        total = ev + near
        pct_of_all = round(total / total_records * 100)

        if ev > 0:
            ax5.text(i, ev / 2, f'{ev}', ha='center', va='center',
                    fontsize=16, fontweight='bold', color='white')
        if near > 0:
            ax5.text(i, ev + near / 2, f'{near}', ha='center', va='center',
                    fontsize=16, fontweight='bold', color='white')
        ax5.text(i, total + 2, f'{fix_hebrew("סה״כ:")} {total}\n({pct_of_all}% {fix_hebrew("מכלל הדיווחים")})',
                ha='center', va='bottom', fontsize=12, fontweight='bold', color=COLORS['primary'])

    ax5.set_xticks(x_pos)
    ax5.set_xticklabels([cat[0] for cat in categories], fontsize=16, fontweight='bold')
    ax5.set_ylabel(fix_hebrew('מספר אירועים'), fontsize=14, fontweight='bold')

    ax5.set_title(fix_hebrew(f'אירועים שדרשו דיווח חיצוני (מתוך {total_records} דיווחים)'),
                  fontsize=20, fontweight='bold', pad=20)

    ax5.legend(loc='upper right', fontsize=14, frameon=True)
    ax5.spines['top'].set_visible(False)
    ax5.spines['right'].set_visible(False)

    max_height = max([e + n for e, n in zip(events_counts, near_events_counts)])
    ax5.set_ylim(0, max_height * 1.35)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/5_external_reporting.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   Saved: {OUTPUT_DIR}/5_external_reporting.png")

    # ========================================================================
    # GRAPH 6: EVENT TYPES FUNNEL (PNG)
    # ========================================================================
    print("\n6. Creating event types funnel chart...")

    fig6, ax6 = plt.subplots(figsize=(14, 10), facecolor='white')

    event_types = df_clean[EVENT_TYPE].value_counts().head(10)
    colors_types = plt.cm.Blues(np.linspace(0.9, 0.4, len(event_types)))

    y_pos = np.arange(len(event_types))
    bars = ax6.barh(y_pos[::-1], event_types.values, color=colors_types, edgecolor='white', height=0.7)

    for i, (bar, val) in enumerate(zip(bars, event_types.values)):
        pct = round(val / total_records * 100)
        ax6.text(val + 3, len(event_types) - 1 - i, f'{val} ({pct}%)', va='center', ha='left',
                fontsize=14, fontweight='bold', color=COLORS['primary'])

    ax6.set_yticks(y_pos)
    ax6.set_yticklabels([fix_hebrew(str(x)) for x in event_types.index[::-1]], fontsize=13)
    ax6.set_xlabel(fix_hebrew('מספר אירועים'), fontsize=14, fontweight='bold')
    ax6.set_xlim(0, event_types.values[0] * 1.25)

    # Calculate total percentage covered by top 10
    top_10_total = event_types.sum()
    top_10_pct = round(top_10_total / total_records * 100)

    ax6.set_title(fix_hebrew(f'10 סוגי האירועים הנפוצים ביותר (מתוך {total_records} דיווחים, {top_10_pct}% מהכלל)'),
                  fontsize=18, fontweight='bold', pad=20)

    ax6.spines['top'].set_visible(False)
    ax6.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/6_event_types.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   Saved: {OUTPUT_DIR}/6_event_types.png")

    # ========================================================================
    # GRAPH 7: AVERAGE REPORTING TIME DISTRIBUTION (HORIZONTAL BAR)
    # ========================================================================
    print("\n7. Creating average reporting time distribution chart...")

    fig7, ax7 = plt.subplots(figsize=(14, 8), facecolor='white')

    df_time_dist = df_clean[AE].dropna()

    # Create time bins
    time_bins = [
        ('עד 24 שעות', (df_time_dist <= 1).sum()),
        ('1-3 ימים', ((df_time_dist > 1) & (df_time_dist <= 3)).sum()),
        ('3-7 ימים', ((df_time_dist > 3) & (df_time_dist <= 7)).sum()),
        ('7-14 ימים', ((df_time_dist > 7) & (df_time_dist <= 14)).sum()),
        ('14-30 ימים', ((df_time_dist > 14) & (df_time_dist <= 30)).sum()),
        ('מעל 30 ימים', (df_time_dist > 30).sum())
    ]

    labels = [fix_hebrew(t[0]) for t in time_bins]
    values = [t[1] for t in time_bins]
    total_with_time = sum(values)

    # Colors: gradient from green to red
    bar_colors = [COLORS['success'], COLORS['success'], COLORS['warning'],
                  COLORS['warning'], COLORS['danger'], COLORS['danger']]

    y_pos = np.arange(len(labels))
    bars = ax7.barh(y_pos[::-1], values, color=bar_colors, edgecolor='white', height=0.6)

    for i, (bar, val) in enumerate(zip(bars, values)):
        pct = round(val / total_with_time * 100) if total_with_time > 0 else 0
        ax7.text(val + 5, len(labels) - 1 - i, f'{val} ({pct}%)', va='center', ha='left',
                fontsize=14, fontweight='bold', color=COLORS['primary'])

    ax7.set_yticks(y_pos)
    ax7.set_yticklabels(labels[::-1], fontsize=14)
    ax7.set_xlabel(fix_hebrew('מספר דיווחים'), fontsize=14, fontweight='bold')
    ax7.set_xlim(0, max(values) * 1.3)

    ax7.set_title(fix_hebrew(f'התפלגות זמני דיווח (מתוך {total_with_time} דיווחים עם נתוני זמן)'),
                  fontsize=18, fontweight='bold', pad=20)

    ax7.spines['top'].set_visible(False)
    ax7.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/7_time_distribution.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   Saved: {OUTPUT_DIR}/7_time_distribution.png")

    # ========================================================================
    # GRAPH 8: REPORTING SPEED BY DISTRICT (WITH HOSPITAL X, DENTAL, NO HQ)
    # ========================================================================
    print("\n8. Creating reporting speed by district chart...")

    fig8, ax8 = plt.subplots(figsize=(14, 8), facecolor='white')

    # Filter: include hospital X and dental, exclude HQ (מטה)
    df_district_speed = df_clean[df_clean[DISTRICT] != 'מטה'].copy()
    df_district_speed = df_district_speed[[DISTRICT, AE]].dropna()

    # Calculate average reporting time by district
    district_speed = df_district_speed.groupby(DISTRICT)[AE].mean().sort_values()

    y_pos = np.arange(len(district_speed))
    bar_colors_speed = [COLORS['success'] if v <= 1 else COLORS['warning'] if v <= 3 else COLORS['danger']
                        for v in district_speed.values]

    bars = ax8.barh(y_pos, district_speed.values, color=bar_colors_speed, edgecolor='white', height=0.6)

    for i, (bar, val) in enumerate(zip(bars, district_speed.values)):
        ax8.text(val + 0.1, i, f'{val:.1f}', va='center', ha='left',
                fontsize=12, fontweight='bold', color=COLORS['primary'])

    ax8.set_yticks(y_pos)
    ax8.set_yticklabels([fix_hebrew(str(x)) for x in district_speed.index], fontsize=12)
    ax8.set_xlabel(fix_hebrew('ממוצע ימים לדיווח'), fontsize=14, fontweight='bold')

    ax8.set_xlim(0, max(district_speed.values) * 1.2)

    ax8.set_title(fix_hebrew('מהירות דיווח לפי מחוז (ממוצע ימים מאירוע לדיווח)'),
                  fontsize=18, fontweight='bold', pad=20)

    ax8.spines['top'].set_visible(False)
    ax8.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/8_district_speed.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   Saved: {OUTPUT_DIR}/8_district_speed.png")

    # ========================================================================
    # GRAPH 9: REPORTING VOLUME BY DISTRICT (WITH HOSPITAL X, DENTAL, NO HQ)
    # ========================================================================
    print("\n9. Creating reporting volume by district chart...")

    fig9, ax9 = plt.subplots(figsize=(14, 8), facecolor='white')

    # Filter: include hospital X and dental, exclude HQ (מטה)
    df_district_volume = df_clean[df_clean[DISTRICT] != 'מטה'].copy()

    # Count reports by district
    district_volume = df_district_volume[DISTRICT].value_counts().sort_values()

    y_pos = np.arange(len(district_volume))
    colors_volume = plt.cm.Blues(np.linspace(0.4, 0.9, len(district_volume)))

    bars = ax9.barh(y_pos, district_volume.values, color=colors_volume, edgecolor='white', height=0.6)

    total_volume = district_volume.sum()
    for i, (bar, val) in enumerate(zip(bars, district_volume.values)):
        pct = round(val / total_volume * 100)
        ax9.text(val + 3, i, f'{val} ({pct}%)', va='center', ha='left',
                fontsize=12, fontweight='bold', color=COLORS['primary'])

    ax9.set_yticks(y_pos)
    ax9.set_yticklabels([fix_hebrew(str(x)) for x in district_volume.index], fontsize=12)
    ax9.set_xlabel(fix_hebrew('מספר דיווחים'), fontsize=14, fontweight='bold')
    ax9.set_xlim(0, max(district_volume.values) * 1.25)

    ax9.set_title(fix_hebrew(f'נפח דיווחים לפי מחוז (מתוך {total_volume} דיווחים)'),
                  fontsize=18, fontweight='bold', pad=20)

    ax9.spines['top'].set_visible(False)
    ax9.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/9_district_volume.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   Saved: {OUTPUT_DIR}/9_district_volume.png")

    # ========================================================================
    # CREATE COMBINED HTML DASHBOARD
    # ========================================================================
    print("\n10. Creating combined HTML dashboard...")

    total_events = (df_clean[EVENT_OR_NEAR] == 'אירוע').sum()
    total_near_events = (df_clean[EVENT_OR_NEAR] == 'כמעט אירוע').sum()
    avg_delay = df_ae_valid.mean()

    dashboard_html = f'''<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>דשבורד דיווחי אירועים רפואיים</title>
    <style>
        @font-face {{
            font-family: 'David';
            src: local('David');
        }}
        body {{
            font-family: 'David', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            direction: rtl;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #2C3E50 0%, #3498DB 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .export-btn {{
            position: fixed;
            top: 20px;
            left: 20px;
            background: #27AE60;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-family: inherit;
            z-index: 1000;
        }}
        .export-btn:hover {{
            background: #219a52;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            max-width: 1800px;
            margin: 0 auto;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .card.full-width {{
            grid-column: span 2;
        }}
        .card-header {{
            background: #2C3E50;
            color: white;
            padding: 12px 20px;
            font-size: 16px;
            font-weight: bold;
        }}
        .card-header .badge {{
            background: #E74C3C;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-right: 8px;
        }}
        .card-body {{
            padding: 15px;
            text-align: center;
        }}
        .card-body img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }}
        .card-body iframe {{
            width: 100%;
            height: 650px;
            border: none;
        }}
        .stats-bar {{
            display: flex;
            justify-content: space-around;
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2C3E50;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 3px;
        }}
        .period-note {{
            background: #E8F4FD;
            border: 1px solid #3498DB;
            border-radius: 5px;
            padding: 8px 15px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
            color: #2C3E50;
        }}
        .interactive-note {{
            background: #FDF2E9;
            border: 1px solid #E67E22;
            border-radius: 5px;
            padding: 6px 10px;
            font-size: 11px;
            color: #8B4513;
            margin-top: 8px;
        }}
        .color-legend {{
            background: white;
            border-radius: 10px;
            padding: 12px 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            font-size: 14px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        @media print {{
            .export-btn {{ display: none; }}
        }}
    </style>
    <script>
        function exportDashboard() {{
            window.print();
        }}

        function downloadHTML() {{
            // Create a complete HTML document with embedded iframes content
            const htmlContent = document.documentElement.outerHTML;
            const blob = new Blob([htmlContent], {{type: 'text/html;charset=utf-8'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'dashboard_export.html';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
    </script>
</head>
<body>
    <div style="position: fixed; top: 20px; left: 20px; z-index: 1000; display: flex; gap: 10px;">
        <button class="export-btn" onclick="exportDashboard()">📤 ייצוא ל-PDF</button>
        <button class="export-btn" style="background: #3498DB;" onclick="downloadHTML()">💾 הורדת HTML</button>
    </div>

    <div class="header">
        <h1>דשבורד דיווחי אירועים רפואיים</h1>
        <p>ניתוח מקיף של דפוסי דיווח, זמני תגובה והתפלגות גיאוגרפית</p>
    </div>

    <div class="period-note">
        <strong>תקופת הנתונים:</strong> ינואר - יוני 2025 | <strong>מתוך {total_records} דיווחים</strong>
    </div>

    <div class="stats-bar">
        <div class="stat">
            <div class="stat-value">{total_records}</div>
            <div class="stat-label">סה"כ דיווחים</div>
        </div>
        <div class="stat">
            <div class="stat-value">{total_events}</div>
            <div class="stat-label">אירועים</div>
        </div>
        <div class="stat">
            <div class="stat-value">{total_near_events}</div>
            <div class="stat-label">כמעט אירועים</div>
        </div>
        <div class="stat">
            <div class="stat-value">{avg_reports_per_month}</div>
            <div class="stat-label">ממוצע דיווחים בחודש</div>
        </div>
        <div class="stat">
            <div class="stat-value">{avg_delay:.1f}</div>
            <div class="stat-label">ממוצע ימים לדיווח</div>
        </div>
        <div class="stat">
            <div class="stat-value" style="color: {'#27AE60' if compliance_rate >= 70 else '#E74C3C'}">{compliance_rate}%</div>
            <div class="stat-label">עמידה ברגולציה</div>
        </div>
    </div>

    <div class="color-legend">
        <strong>מקרא צבעים:</strong>
        <div class="legend-item">
            <div class="legend-color" style="background: #27AE60;"></div>
            <span>ירוק = מעט דיווחים / זמן קצר / עמידה ברגולציה</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #F39C12;"></div>
            <span>כתום = בינוני</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #E74C3C;"></div>
            <span>אדום = הרבה דיווחים / זמן ארוך / חריגה מרגולציה</span>
        </div>
    </div>

    <div class="grid">
        <div class="card full-width">
            <div class="card-header">
                <span class="badge">אינטראקטיבי</span>
                1. דשבורד מרכזי עם מפה, מד עמידה ברגולציה, ומגמות
            </div>
            <div class="card-body">
                <iframe src="1_interactive_dashboard.html"></iframe>
                <div class="interactive-note">
                    💡 לחץ על מחוז במפה לפילטור | העבר עכבר לפרטים נוספים
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">2. סוגי אירועים נפוצים (מהגדול לקטן)</div>
            <div class="card-body">
                <img src="6_event_types.png" alt="Event Types">
            </div>
        </div>

        <div class="card">
            <div class="card-header">3. התפלגות זמני דיווח</div>
            <div class="card-body">
                <img src="7_time_distribution.png" alt="Time Distribution">
            </div>
        </div>

        <div class="card">
            <div class="card-header">4. מהירות דיווח לפי מחוז</div>
            <div class="card-body">
                <img src="8_district_speed.png" alt="District Speed">
            </div>
        </div>

        <div class="card">
            <div class="card-header">5. נפח דיווחים לפי מחוז</div>
            <div class="card-body">
                <img src="9_district_volume.png" alt="District Volume">
            </div>
        </div>

        <div class="card full-width">
            <div class="card-header">
                <span class="badge">אינטראקטיבי</span>
                6. מפת חום עם בחירת צירים
            </div>
            <div class="card-body">
                <iframe src="2_drilldown_heatmap.html"></iframe>
                <div class="interactive-note">
                    💡 בחר צירים מהתפריט: תפקיד×מחוז, תפקיד×סוג אירוע, או גיל×מין
                </div>
            </div>
        </div>

        <div class="card full-width">
            <div class="card-header">7. עמידה ברגולציה - אירוע (24 שעות) vs כמעט אירוע (3 ימים)</div>
            <div class="card-body">
                <img src="3_regulation_compliance.png" alt="Regulation Compliance">
            </div>
        </div>

        <div class="card">
            <div class="card-header">8. זמן דיווח לפי מקצוע</div>
            <div class="card-body">
                <img src="4_profession_delays.png" alt="Profession Delays">
            </div>
        </div>

        <div class="card">
            <div class="card-header">9. דיווחים חיצוניים - אירוע vs כמעט אירוע</div>
            <div class="card-body">
                <img src="5_external_reporting.png" alt="External Reporting">
            </div>
        </div>
    </div>
</body>
</html>'''

    with open(f'{OUTPUT_DIR}/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)

    print(f"   Saved: {OUTPUT_DIR}/dashboard.html")

    # ========================================================================
    # CREATE SELF-CONTAINED SHAREABLE HTML
    # ========================================================================
    print("\n11. Creating self-contained shareable HTML...")

    import base64
    import json

    # Read interactive dashboard HTML files
    with open(f'{OUTPUT_DIR}/1_interactive_dashboard.html', 'r', encoding='utf-8') as f:
        dashboard1_html = f.read()
    with open(f'{OUTPUT_DIR}/2_drilldown_heatmap.html', 'r', encoding='utf-8') as f:
        dashboard2_html = f.read()

    # Convert to base64 for safe embedding
    dashboard1_b64 = base64.b64encode(dashboard1_html.encode('utf-8')).decode('utf-8')
    dashboard2_b64 = base64.b64encode(dashboard2_html.encode('utf-8')).decode('utf-8')

    # Convert PNG images to base64
    def img_to_base64(path):
        with open(path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')

    img3_b64 = img_to_base64(f'{OUTPUT_DIR}/3_regulation_compliance.png')
    img4_b64 = img_to_base64(f'{OUTPUT_DIR}/4_profession_delays.png')
    img5_b64 = img_to_base64(f'{OUTPUT_DIR}/5_external_reporting.png')
    img6_b64 = img_to_base64(f'{OUTPUT_DIR}/6_event_types.png')
    img7_b64 = img_to_base64(f'{OUTPUT_DIR}/7_time_distribution.png')
    img8_b64 = img_to_base64(f'{OUTPUT_DIR}/8_district_speed.png')
    img9_b64 = img_to_base64(f'{OUTPUT_DIR}/9_district_volume.png')

    compliance_color = '#27AE60' if compliance_rate >= 70 else '#E74C3C'

    # Create fully self-contained HTML with JavaScript blob loading
    shareable_html = f'''<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>דשבורד דיווחי אירועים רפואיים</title>
    <style>
        @font-face {{ font-family: 'David'; src: local('David'); }}
        body {{ font-family: 'David', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; direction: rtl; }}
        .header {{ text-align: center; padding: 20px; background: linear-gradient(135deg, #2C3E50 0%, #3498DB 100%); color: white; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 10px 0 0 0; font-size: 14px; opacity: 0.9; }}
        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; max-width: 1800px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }}
        .card.full-width {{ grid-column: span 2; }}
        .card-header {{ background: #2C3E50; color: white; padding: 12px 20px; font-size: 16px; font-weight: bold; }}
        .card-header .badge {{ background: #E74C3C; padding: 3px 8px; border-radius: 4px; font-size: 11px; margin-right: 8px; }}
        .card-body {{ padding: 15px; text-align: center; }}
        .card-body img {{ max-width: 100%; height: auto; border-radius: 5px; }}
        .stats-bar {{ display: flex; justify-content: space-around; background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #2C3E50; }}
        .stat-label {{ font-size: 12px; color: #666; margin-top: 3px; }}
        .period-note {{ background: #E8F4FD; border: 1px solid #3498DB; border-radius: 5px; padding: 8px 15px; margin-bottom: 20px; text-align: center; font-size: 14px; color: #2C3E50; }}
        .interactive-note {{ background: #FDF2E9; border: 1px solid #E67E22; border-radius: 5px; padding: 6px 10px; font-size: 11px; color: #8B4513; margin-top: 8px; }}
        .embedded-chart {{ width: 100%; border: none; }}
        .color-legend {{ background: white; border-radius: 10px; padding: 12px 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; justify-content: center; align-items: center; gap: 30px; font-size: 14px; }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; }}
        .legend-color {{ width: 20px; height: 20px; border-radius: 4px; }}
        @media print {{ body {{ padding: 10px; }} .card {{ break-inside: avoid; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>דשבורד דיווחי אירועים רפואיים</h1>
        <p>ניתוח מקיף של דפוסי דיווח, זמני תגובה והתפלגות גיאוגרפית</p>
    </div>

    <div class="period-note">
        <strong>תקופת הנתונים:</strong> ינואר - יוני 2025 | <strong>מתוך {total_records} דיווחים</strong>
    </div>

    <div class="stats-bar">
        <div class="stat"><div class="stat-value">{total_records}</div><div class="stat-label">סה"כ דיווחים</div></div>
        <div class="stat"><div class="stat-value">{total_events}</div><div class="stat-label">אירועים</div></div>
        <div class="stat"><div class="stat-value">{total_near_events}</div><div class="stat-label">כמעט אירועים</div></div>
        <div class="stat"><div class="stat-value">{avg_reports_per_month}</div><div class="stat-label">ממוצע דיווחים בחודש</div></div>
        <div class="stat"><div class="stat-value">{avg_delay:.1f}</div><div class="stat-label">ממוצע ימים לדיווח</div></div>
        <div class="stat"><div class="stat-value" style="color: {compliance_color}">{compliance_rate}%</div><div class="stat-label">עמידה ברגולציה</div></div>
    </div>

    <div class="color-legend">
        <strong>מקרא צבעים:</strong>
        <div class="legend-item"><div class="legend-color" style="background: #27AE60;"></div><span>ירוק = מעט דיווחים / זמן קצר / עמידה ברגולציה</span></div>
        <div class="legend-item"><div class="legend-color" style="background: #F39C12;"></div><span>כתום = בינוני</span></div>
        <div class="legend-item"><div class="legend-color" style="background: #E74C3C;"></div><span>אדום = הרבה דיווחים / זמן ארוך / חריגה מרגולציה</span></div>
    </div>

    <div class="grid">
        <div class="card full-width">
            <div class="card-header"><span class="badge">אינטראקטיבי</span>1. דשבורד מרכזי עם מפה, מד עמידה ברגולציה, ומגמות</div>
            <div class="card-body">
                <iframe id="chart1" class="embedded-chart" style="height: 1000px;"></iframe>
                <div class="interactive-note">💡 לחץ על מחוז במפה לפילטור | העבר עכבר לפרטים נוספים</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">2. סוגי אירועים נפוצים (מהגדול לקטן)</div>
            <div class="card-body"><img src="data:image/png;base64,{img6_b64}" alt="Event Types"></div>
        </div>

        <div class="card">
            <div class="card-header">3. התפלגות זמני דיווח</div>
            <div class="card-body"><img src="data:image/png;base64,{img7_b64}" alt="Time Distribution"></div>
        </div>

        <div class="card">
            <div class="card-header">4. מהירות דיווח לפי מחוז</div>
            <div class="card-body"><img src="data:image/png;base64,{img8_b64}" alt="District Speed"></div>
        </div>

        <div class="card">
            <div class="card-header">5. נפח דיווחים לפי מחוז</div>
            <div class="card-body"><img src="data:image/png;base64,{img9_b64}" alt="District Volume"></div>
        </div>

        <div class="card full-width">
            <div class="card-header"><span class="badge">אינטראקטיבי</span>6. מפת חום עם בחירת צירים</div>
            <div class="card-body">
                <iframe id="chart2" class="embedded-chart" style="height: 800px;"></iframe>
                <div class="interactive-note">💡 בחר צירים מהתפריט: תפקיד×מחוז, תפקיד×סוג אירוע, או גיל×מין</div>
            </div>
        </div>

        <div class="card full-width">
            <div class="card-header">7. עמידה ברגולציה - אירוע (24 שעות) vs כמעט אירוע (3 ימים)</div>
            <div class="card-body"><img src="data:image/png;base64,{img3_b64}" alt="Regulation Compliance"></div>
        </div>

        <div class="card">
            <div class="card-header">8. זמן דיווח לפי מקצוע</div>
            <div class="card-body"><img src="data:image/png;base64,{img4_b64}" alt="Profession Delays"></div>
        </div>

        <div class="card">
            <div class="card-header">9. דיווחים חיצוניים - אירוע vs כמעט אירוע</div>
            <div class="card-body"><img src="data:image/png;base64,{img5_b64}" alt="External Reporting"></div>
        </div>
    </div>

    <script>
        // Decode base64 and load into iframe via srcdoc (preserves origin for map tiles)
        function loadChart(iframeId, base64Content) {{
            const html = atob(base64Content);
            document.getElementById(iframeId).srcdoc = html;
        }}

        // Load charts when page loads
        window.onload = function() {{
            loadChart('chart1', '{dashboard1_b64}');
            loadChart('chart2', '{dashboard2_b64}');
        }};
    </script>
</body>
</html>'''

    with open(f'{OUTPUT_DIR}/dashboard_shareable.html', 'w', encoding='utf-8') as f:
        f.write(shareable_html)

    print(f"   Saved: {OUTPUT_DIR}/dashboard_shareable.html")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 60)
    print("DASHBOARD CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nData period: January - June 2025")
    print(f"Total records: {total_records}")
    print(f"Average reports per month: {avg_reports_per_month}")
    print(f"Compliance rate: {compliance_rate}%")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("\nFiles created:")
    print("  1. 1_interactive_dashboard.html - Dashboard with working filters")
    print("  2. 2_drilldown_heatmap.html     - Heatmap with axis selection")
    print("  3. 3_regulation_compliance.png  - Dual bar (event vs near-event)")
    print("  4. 4_profession_delays.png      - Stacked bar by profession")
    print("  5. 5_external_reporting.png     - External reporting")
    print("  6. 6_event_types.png            - Event types funnel")
    print("  7. 7_time_distribution.png      - Reporting time distribution")
    print("  8. 8_district_speed.png         - Reporting speed by district")
    print("  9. 9_district_volume.png        - Reporting volume by district")
    print(" 10. dashboard.html               - Combined dashboard (local use)")
    print(" 11. dashboard_shareable.html     - Self-contained file for sharing")
    print("\nRegulation rules applied:")
    print("  - Event (אירוע): 24 hours")
    print("  - Near-event (כמעט אירוע): 3 days")
    print("\n📤 לשיתוף הדשבורד:")
    print("   שלח את הקובץ: dashboard_shareable.html")
    print("   קובץ יחיד שעובד בכל דפדפן ללא צורך בקבצים נוספים!")
    print("=" * 60)