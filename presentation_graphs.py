import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from bidi.algorithm import get_display

# Column names
W = 'מקצוע המדווח (לא תפקיד)*'
AE = 'מתאריך האירוע לתאריך שליחת הדיווח'
DISTRICT = 'מחוז*'
EVENT_TYPE = 'סוג אירוע ראשי*'
EVENT_DATE = 'תאריך האירוע*'
EVENT_OR_NEAR = 'אירוע / כמעט אירוע'

def fix_hebrew(text):
    """Fix Hebrew text for correct RTL display in matplotlib"""
    return get_display(str(text))

if __name__ == '__main__':
    # Load and clean data
    df = pd.read_excel('/Users/barnaor/Downloads/project_data.xlsx', sheet_name='גיליון1')
    df_clean = df[(df[AE].isna()) | ((df[AE] >= 0) & (df[AE] <= 365))].copy()
    df_ae_valid = df_clean[AE].dropna()

    # Style setup
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['axes.unicode_minus'] = False

    # Color palette - professional and impactful
    COLORS = {
        'dark': '#1a1a2e',
        'accent': '#e94560',
        'highlight': '#0f3460',
        'success': '#16a085',
        'warning': '#f39c12',
        'danger': '#c0392b',
        'info': '#3498db',
        'light': '#eaf2f8',
        'gradient_start': '#667eea',
        'gradient_end': '#764ba2'
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # GRAPH 1: "THE WAKE-UP CALL" - Dramatic donut showing delay crisis
    # ═══════════════════════════════════════════════════════════════════════════
    fig1, ax1 = plt.subplots(figsize=(14, 10), facecolor='white')

    # Calculate dramatic stats
    total_reports = len(df_ae_valid)
    delayed_over_week = (df_ae_valid > 7).sum()
    delayed_over_month = (df_ae_valid > 30).sum()
    on_time = (df_ae_valid <= 7).sum()

    pct_delayed = delayed_over_week / total_reports * 100
    pct_on_time = on_time / total_reports * 100

    # Create dramatic donut chart
    sizes = [on_time, delayed_over_week - delayed_over_month, delayed_over_month]
    colors_donut = [COLORS['success'], COLORS['warning'], COLORS['danger']]
    explode = (0, 0.02, 0.05)  # Explode the "danger" slice

    wedges, texts, autotexts = ax1.pie(
        sizes,
        explode=explode,
        colors=colors_donut,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.75,
        wedgeprops=dict(width=0.5, edgecolor='white', linewidth=3),
        textprops={'fontsize': 14, 'fontweight': 'bold'}
    )

    # Center text - the shocking statistic
    ax1.text(0, 0.1, f'{pct_delayed:.0f}%', fontsize=72, fontweight='bold',
             ha='center', va='center', color=COLORS['danger'])
    ax1.text(0, -0.15, fix_hebrew('מתעכבים מעל שבוע'), fontsize=18,
             ha='center', va='center', color=COLORS['dark'])

    # Title
    ax1.set_title(fix_hebrew('משבר הדיווחים: כמה מהר מגיע המידע?'),
                  fontsize=24, fontweight='bold', pad=30, color=COLORS['dark'])

    # Legend
    legend_labels = [
        f'{fix_hebrew("בזמן (עד שבוע)")} - {on_time} ({pct_on_time:.1f}%)',
        f'{fix_hebrew("עיכוב בינוני (שבוע-חודש)")} - {delayed_over_week - delayed_over_month}',
        f'{fix_hebrew("עיכוב קריטי (מעל חודש)")} - {delayed_over_month}'
    ]
    legend_patches = [mpatches.Patch(color=c, label=l) for c, l in zip(colors_donut, legend_labels)]
    ax1.legend(handles=legend_patches, loc='lower center', fontsize=12,
               ncol=1, frameon=True, facecolor='white', edgecolor='gray',
               bbox_to_anchor=(0.5, -0.1))

    # Subtitle with context
    fig1.text(0.5, 0.02, fix_hebrew(f'מבוסס על {total_reports} דיווחים | ממוצע זמן דיווח: {df_ae_valid.mean():.1f} ימים'),
              fontsize=12, ha='center', color='gray', style='italic')

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)

    # ═══════════════════════════════════════════════════════════════════════════
    # GRAPH 2: "THE CULPRITS" - Who delays the most? Horizontal lollipop chart
    # ═══════════════════════════════════════════════════════════════════════════
    fig2, ax2 = plt.subplots(figsize=(14, 10), facecolor='white')

    # Prepare profession data
    df_prof = df_clean[[W, AE]].dropna()
    prof_stats = df_prof.groupby(W).agg({AE: ['mean', 'count']}).round(2)
    prof_stats.columns = ['mean', 'count']
    prof_stats = prof_stats[prof_stats['count'] >= 10]  # Minimum 10 reports
    prof_stats = prof_stats.sort_values('mean', ascending=True)

    # Colors based on performance (good = within 3 days)
    colors_lollipop = [COLORS['success'] if m <= 3 else COLORS['warning'] if m <= 10 else COLORS['danger']
                       for m in prof_stats['mean']]

    y_pos = np.arange(len(prof_stats))

    # Draw horizontal lines (stems)
    for i, (mean, color) in enumerate(zip(prof_stats['mean'], colors_lollipop)):
        ax2.hlines(y=i, xmin=0, xmax=mean, color=color, alpha=0.7, linewidth=3)

    # Draw circles (lollipops)
    ax2.scatter(prof_stats['mean'], y_pos, c=colors_lollipop, s=300, zorder=5,
                edgecolors='white', linewidth=2)

    # Add value labels inside circles
    for i, mean in enumerate(prof_stats['mean']):
        ax2.text(mean, i, f'{mean:.0f}', ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')

    # Add count labels at the end
    for i, (idx, row) in enumerate(prof_stats.iterrows()):
        ax2.text(prof_stats['mean'].max() + 3, i, f'n={int(row["count"])}',
                fontsize=9, color='gray', va='center')

    # Reference lines
    ax2.axvline(3, color=COLORS['success'], linestyle='--', linewidth=2, alpha=0.7)
    ax2.axvline(10, color=COLORS['warning'], linestyle='--', linewidth=2, alpha=0.7)
    ax2.text(3, len(prof_stats) - 0.5, fix_hebrew('יעד: 3 ימים'), fontsize=10,
             color=COLORS['success'], fontweight='bold')

    # Labels
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([fix_hebrew(str(x)) for x in prof_stats.index], fontsize=11)
    ax2.set_xlabel(fix_hebrew('ממוצע ימים מאירוע לדיווח'), fontsize=14, fontweight='bold')
    ax2.set_xlim(0, prof_stats['mean'].max() + 15)

    # Title
    ax2.set_title(fix_hebrew('מי מעכב? זמן דיווח לפי מקצוע'),
                  fontsize=24, fontweight='bold', pad=20, color=COLORS['dark'])

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLORS['success'], label=fix_hebrew('מצוין (עד 3 ימים)')),
        mpatches.Patch(color=COLORS['warning'], label=fix_hebrew('בינוני (3-10 ימים)')),
        mpatches.Patch(color=COLORS['danger'], label=fix_hebrew('קריטי (מעל 10 ימים)'))
    ]
    ax2.legend(handles=legend_elements, loc='lower right', fontsize=11, frameon=True)

    # Remove top and right spines
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.tick_params(left=False)

    plt.tight_layout()

    # ═══════════════════════════════════════════════════════════════════════════
    # GRAPH 3: "EXTERNAL ESCALATION" - Stacked bar for external reporting
    # ═══════════════════════════════════════════════════════════════════════════
    fig3, ax3 = plt.subplots(figsize=(14, 10), facecolor='white')

    # Column names for external reporting
    LEGAL = 'להעביר ליועמ"ש'
    INSURANCE = 'צורך בדיווח לחברת ביטוח?'
    HEALTH_MINISTRY = 'צורך בדיווח למשרד הבריאות?'

    # Create flags for external reporting
    df_ext = df_clean.copy()
    df_ext['needs_legal'] = df_ext[LEGAL].fillna('').astype(str).str.contains('כן|yes', case=False, na=False)
    df_ext['needs_insurance'] = df_ext[INSURANCE].fillna('').astype(str).str.contains('כן|yes', case=False, na=False)
    df_ext['needs_health_ministry'] = df_ext[HEALTH_MINISTRY].fillna('').astype(str).str.contains('כן|yes', case=False, na=False)

    # Count by event type (אירוע vs כמעט אירוע) for each external reporting category
    categories = [
        (fix_hebrew('יועמ"ש'), 'needs_legal', COLORS['warning']),
        (fix_hebrew('חברת ביטוח'), 'needs_insurance', COLORS['danger']),
        (fix_hebrew('משרד הבריאות'), 'needs_health_ministry', COLORS['highlight'])
    ]

    x_pos = np.arange(len(categories))
    width = 0.6

    events_counts = []
    near_events_counts = []

    for _, col, _ in categories:
        df_filtered = df_ext[df_ext[col]]
        event_count = (df_filtered[EVENT_OR_NEAR] == 'אירוע').sum()
        near_event_count = (df_filtered[EVENT_OR_NEAR] == 'כמעט אירוע').sum()
        events_counts.append(event_count)
        near_events_counts.append(near_event_count)

    # Stacked bars
    bars_events = ax3.bar(x_pos, events_counts, width, label=fix_hebrew('אירוע'),
                          color=COLORS['danger'], edgecolor='white', linewidth=2)
    bars_near = ax3.bar(x_pos, near_events_counts, width, bottom=events_counts,
                        label=fix_hebrew('כמעט אירוע'), color=COLORS['info'],
                        edgecolor='white', linewidth=2)

    # Add labels inside the bars
    for i, (ev, near) in enumerate(zip(events_counts, near_events_counts)):
        total = ev + near
        # Event count (bottom part)
        if ev > 0:
            ax3.text(i, ev / 2, f'{ev}', ha='center', va='center',
                    fontsize=14, fontweight='bold', color='white')
        # Near-event count (top part)
        if near > 0:
            ax3.text(i, ev + near / 2, f'{near}', ha='center', va='center',
                    fontsize=14, fontweight='bold', color='white')
        # Total on top
        ax3.text(i, total + 1, f'{fix_hebrew("סה״כ")}: {total}', ha='center', va='bottom',
                fontsize=12, fontweight='bold', color=COLORS['dark'])

    # Calculate percentages from total events
    total_all_events = len(df_ext)
    totals = [e + n for e, n in zip(events_counts, near_events_counts)]

    # Add percentage labels below bars
    for i, total in enumerate(totals):
        pct = total / total_all_events * 100
        ax3.text(i, -3, f'({pct:.1f}%)', ha='center', va='top',
                fontsize=11, color='gray', style='italic')

    ax3.set_xticks(x_pos)
    ax3.set_xticklabels([cat[0] for cat in categories], fontsize=14, fontweight='bold')
    ax3.set_ylabel(fix_hebrew('מספר אירועים'), fontsize=14, fontweight='bold')
    ax3.set_ylim(-8, max(totals) * 1.2)

    # Title
    ax3.set_title(fix_hebrew('אירועים שדרשו דיווח חיצוני: אירוע vs כמעט אירוע'),
                  fontsize=24, fontweight='bold', pad=20, color=COLORS['dark'])

    # Subtitle
    fig3.text(0.5, 0.02, fix_hebrew(f'מתוך {total_all_events} דיווחים | אחוזים מציינים שיעור מסך כל האירועים'),
              fontsize=12, ha='center', color='gray', style='italic')

    # Legend
    ax3.legend(loc='upper right', fontsize=12, frameon=True, facecolor='white')

    # Clean spines
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.12)

    # ═══════════════════════════════════════════════════════════════════════════
    # GRAPH 4: EVENTS VS NEAR-EVENTS - 2025 ONLY
    # ═══════════════════════════════════════════════════════════════════════════
    fig4, ax4 = plt.subplots(figsize=(14, 10), facecolor='white')

    # Filter for 2025 only
    df_2025 = df_clean[df_clean[EVENT_DATE].notna()].copy()
    df_2025 = df_2025[df_2025[EVENT_DATE].dt.year == 2025]
    df_2025['month'] = df_2025[EVENT_DATE].dt.month

    # Group by month and event type
    monthly_events = df_2025.groupby(['month', EVENT_OR_NEAR]).size().unstack(fill_value=0)

    # Ensure columns exist
    if 'אירוע' not in monthly_events.columns:
        monthly_events['אירוע'] = 0
    if 'כמעט אירוע' not in monthly_events.columns:
        monthly_events['כמעט אירוע'] = 0

    months = monthly_events.index
    month_names = ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
                   'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר']

    x_pos = np.arange(len(months))
    width = 0.6

    events_2025 = monthly_events['אירוע'].values
    near_events_2025 = monthly_events['כמעט אירוע'].values

    # Stacked bars
    bars_ev = ax4.bar(x_pos, events_2025, width, label=fix_hebrew('אירוע'),
                      color=COLORS['danger'], edgecolor='white', linewidth=2)
    bars_near = ax4.bar(x_pos, near_events_2025, width, bottom=events_2025,
                        label=fix_hebrew('כמעט אירוע'), color=COLORS['info'],
                        edgecolor='white', linewidth=2)

    # Add labels inside bars
    for i, (ev, near) in enumerate(zip(events_2025, near_events_2025)):
        total = ev + near
        if ev > 0:
            ax4.text(i, ev / 2, f'{ev}', ha='center', va='center',
                    fontsize=11, fontweight='bold', color='white')
        if near > 0:
            ax4.text(i, ev + near / 2, f'{near}', ha='center', va='center',
                    fontsize=11, fontweight='bold', color='white')
        # Total on top
        ax4.text(i, total + 2, f'{total}', ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=COLORS['dark'])

    # X-axis labels
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels([fix_hebrew(month_names[m-1]) for m in months], fontsize=11, rotation=45, ha='right')
    ax4.set_ylabel(fix_hebrew('מספר אירועים'), fontsize=14, fontweight='bold')

    # Title
    total_2025 = len(df_2025)
    total_events_2025 = events_2025.sum()
    total_near_2025 = near_events_2025.sum()
    ax4.set_title(fix_hebrew(f'אירועים וכמעט אירועים - 2025 (סה״כ: {total_2025})'),
                  fontsize=24, fontweight='bold', pad=20, color=COLORS['dark'])

    # Subtitle with stats
    pct_events = total_events_2025 / total_2025 * 100 if total_2025 > 0 else 0
    pct_near = total_near_2025 / total_2025 * 100 if total_2025 > 0 else 0
    fig4.text(0.5, 0.02,
              fix_hebrew(f'אירועים: {total_events_2025} ({pct_events:.1f}%) | כמעט אירועים: {total_near_2025} ({pct_near:.1f}%)'),
              fontsize=12, ha='center', color='gray', style='italic')

    ax4.legend(loc='upper right', fontsize=12, frameon=True, facecolor='white')
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)

    # Show all graphs
    plt.show()

    print("\n" + "=" * 60)
    print("4 PRESENTATION GRAPHS CREATED:")
    print("=" * 60)
    print(f"1. THE WAKE-UP CALL: {pct_delayed:.0f}% of reports are delayed over a week")
    print(f"2. THE CULPRITS: Showing delay by profession (n≥10) - Good = 3 days")
    print(f"3. EXTERNAL ESCALATION: Stacked bar (Event vs Near-event) for Legal/Insurance/Health Ministry")
    print(f"4. EVENTS 2025: Events vs Near-events by month for 2025")
    print("=" * 60)