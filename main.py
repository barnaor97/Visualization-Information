import pandas as pd
import matplotlib.pyplot as plt
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
LEGAL = 'להעביר ליועמ"ש'  # Column S - Legal counsel
INSURANCE = 'צורך בדיווח לחברת ביטוח?'  # Column X - Insurance
HEALTH_MINISTRY = 'צורך בדיווח למשרד הבריאות?'  # Column Y - Ministry of Health

def fix_hebrew(text):
    """Fix Hebrew text for correct RTL display in matplotlib"""
    return get_display(str(text))

if __name__ == '__main__':
    # Load data
    df = pd.read_excel('/Users/barnaor/Downloads/project_data.xlsx', sheet_name='גיליון1')

    # ══════════════════════════════════════════════════════════════════════
    # DATA QUALITY CHECK - Print and remove negative values
    # ══════════════════════════════════════════════════════════════════════
    print("=" * 60)
    print("DATA QUALITY CHECK")
    print("=" * 60)

    total_records = len(df)
    records_with_ae = df[AE].notna().sum()
    negative_records = (df[AE] < 0).sum()
    extreme_records = (df[AE] > 365).sum()

    print(f"Total records: {total_records}")
    print(f"Records with AE value: {records_with_ae}")
    print(f"Records with NEGATIVE values (AE < 0): {negative_records}")
    print(f"Records with EXTREME values (AE > 365 days): {extreme_records}")
    print(f"Records to be removed: {negative_records + extreme_records}")
    print("=" * 60)

    # Remove negative and extreme values from the dataframe
    df_clean = df[(df[AE].isna()) | ((df[AE] >= 0) & (df[AE] <= 365))].copy()
    print(f"Records after cleaning: {len(df_clean)}")
    print("=" * 60 + "\n")

    # Set up style
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.autolayout'] = False

    # Color palette for storytelling
    COLORS = {
        'primary': '#2C3E50',
        'danger': '#E74C3C',
        'warning': '#F39C12',
        'success': '#27AE60',
        'info': '#3498DB',
        'light': '#ECF0F1'
    }

    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 1: THE SCALE - "How big is the challenge?"
    # ══════════════════════════════════════════════════════════════════════
    fig1, axes1 = plt.subplots(2, 2, figsize=(16, 12))
    fig1.suptitle(fix_hebrew('פרק 1: היקף האתגר'), fontsize=18, fontweight='bold')

    # Calculate key metrics
    total_events = len(df_clean)
    total_real_events = df_clean[EVENT_OR_NEAR].value_counts().get('אירוע', 0)
    df_ae_valid = df_clean[AE].dropna()
    avg_delay = df_ae_valid.mean()
    median_delay = df_ae_valid.median()

    # 1.1 Big Numbers (top left)
    ax1 = axes1[0, 0]
    ax1.axis('off')
    metrics = [
        (str(total_events), fix_hebrew('סה"כ דיווחים'), COLORS['primary']),
        (str(total_real_events), fix_hebrew('אירועים ממשיים'), COLORS['danger']),
    ]
    for i, (value, label, color) in enumerate(metrics):
        ax1.text(0.25 + i * 0.5, 0.65, value, fontsize=36, fontweight='bold',
                ha='center', va='center', color=color, transform=ax1.transAxes)
        ax1.text(0.25 + i * 0.5, 0.35, label, fontsize=12, ha='center', va='center',
                color='gray', transform=ax1.transAxes)

    # 1.2 Delay metrics (top right)
    ax2 = axes1[0, 1]
    ax2.axis('off')
    metrics2 = [
        (f'{avg_delay:.1f}', fix_hebrew('ממוצע ימים'), COLORS['warning']),
        (f'{median_delay:.0f}', fix_hebrew('חציון ימים'), COLORS['success']),
    ]
    for i, (value, label, color) in enumerate(metrics2):
        ax2.text(0.25 + i * 0.5, 0.65, value, fontsize=36, fontweight='bold',
                ha='center', va='center', color=color, transform=ax2.transAxes)
        ax2.text(0.25 + i * 0.5, 0.35, label, fontsize=12, ha='center', va='center',
                color='gray', transform=ax2.transAxes)

    # 1.3 Timeline (bottom left)
    ax3 = axes1[1, 0]
    df_time = df_clean[df_clean[EVENT_DATE].notna()].copy()
    df_time['month'] = df_time[EVENT_DATE].dt.to_period('M')
    monthly = df_time.groupby('month').size()

    x = range(len(monthly))
    ax3.fill_between(x, monthly.values, alpha=0.3, color=COLORS['info'])
    ax3.plot(x, monthly.values, color=COLORS['info'], linewidth=2, marker='o', markersize=3)
    ax3.set_xlabel(fix_hebrew('זמן'), fontsize=11)
    ax3.set_ylabel(fix_hebrew('מספר דיווחים'), fontsize=11)
    ax3.set_title(fix_hebrew('מגמת דיווחים לאורך זמן'), fontsize=12, fontweight='bold')

    tick_positions = list(range(0, len(monthly), max(1, len(monthly)//6)))
    ax3.set_xticks(tick_positions)
    ax3.set_xticklabels([str(monthly.index[i]) for i in tick_positions], rotation=45, ha='right', fontsize=9)

    # 1.4 Event Types (bottom right)
    ax4 = axes1[1, 1]
    event_types = df_clean[EVENT_TYPE].value_counts()
    colors_types = plt.cm.Blues(np.linspace(0.4, 0.9, len(event_types)))
    bars = ax4.barh([fix_hebrew(str(x)) for x in event_types.index], event_types.values, color=colors_types)
    ax4.set_xlabel(fix_hebrew('מספר אירועים'), fontsize=11)
    ax4.set_title(fix_hebrew('סוגי אירועים'), fontsize=12, fontweight='bold')
    ax4.tick_params(axis='y', labelsize=9)

    plt.tight_layout()
    plt.subplots_adjust(top=0.92, hspace=0.3, wspace=0.3)

    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 2: THE PROBLEM - "The Delay Crisis"
    # ══════════════════════════════════════════════════════════════════════
    fig2, axes2 = plt.subplots(2, 1, figsize=(14, 10))
    fig2.suptitle(fix_hebrew('פרק 2: משבר העיכובים'), fontsize=18, fontweight='bold')

    # Calculate delay categories
    same_day = (df_ae_valid <= 1).sum()
    within_week = ((df_ae_valid > 1) & (df_ae_valid <= 7)).sum()
    within_month = ((df_ae_valid > 7) & (df_ae_valid <= 30)).sum()
    over_month = (df_ae_valid > 30).sum()
    total_valid = len(df_ae_valid)

    # 2.1 Delay Categories Bar Chart
    ax_delay = axes2[0]
    categories = [fix_hebrew('באותו יום'), fix_hebrew('תוך שבוע'),
                  fix_hebrew('תוך חודש'), fix_hebrew('מעל חודש')]
    values = [same_day, within_week, within_month, over_month]
    percentages = [v/total_valid*100 for v in values]
    colors_delay = [COLORS['success'], COLORS['info'], COLORS['warning'], COLORS['danger']]

    bars = ax_delay.bar(categories, values, color=colors_delay, edgecolor='white', linewidth=2)
    for bar, val, pct in zip(bars, values, percentages):
        ax_delay.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
                     f'{val} ({pct:.1f}%)', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax_delay.set_ylabel(fix_hebrew('מספר דיווחים'), fontsize=11)
    ax_delay.set_title(fix_hebrew('כמה מהר מדווחים על אירועים?'), fontsize=12, fontweight='bold')
    ax_delay.set_ylim(0, max(values) * 1.25)

    # 2.2 Histogram
    ax_hist = axes2[1]
    df_hist = df_ae_valid[df_ae_valid <= 60]
    n, bins, patches = ax_hist.hist(df_hist, bins=60, color=COLORS['info'], alpha=0.7, edgecolor='white')

    for patch, bin_left in zip(patches, bins[:-1]):
        if bin_left <= 1:
            patch.set_facecolor(COLORS['success'])
        elif bin_left <= 7:
            patch.set_facecolor(COLORS['info'])
        elif bin_left <= 30:
            patch.set_facecolor(COLORS['warning'])
        else:
            patch.set_facecolor(COLORS['danger'])

    ax_hist.axvline(7, color=COLORS['warning'], linestyle='--', linewidth=2, label=fix_hebrew('שבוע'))
    ax_hist.axvline(30, color=COLORS['danger'], linestyle='--', linewidth=2, label=fix_hebrew('חודש'))
    ax_hist.axvline(df_ae_valid.median(), color='black', linestyle='-', linewidth=2,
                   label=f'{fix_hebrew("חציון")}: {df_ae_valid.median():.0f}')
    ax_hist.set_xlabel(fix_hebrew('ימים מאירוע לדיווח'), fontsize=11)
    ax_hist.set_ylabel(fix_hebrew('מספר דיווחים'), fontsize=11)
    ax_hist.set_title(fix_hebrew('התפלגות זמני דיווח (עד 60 יום)'), fontsize=12, fontweight='bold')
    ax_hist.legend(loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.subplots_adjust(top=0.92, hspace=0.35)

    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 3: WHO DELAYS? - "Finding the Bottlenecks"
    # ══════════════════════════════════════════════════════════════════════
    fig3, axes3 = plt.subplots(1, 2, figsize=(16, 10))
    fig3.suptitle(fix_hebrew('פרק 3: מי מעכב? זיהוי צווארי בקבוק'), fontsize=18, fontweight='bold')

    # Prepare profession data
    df_prof = df_clean[[W, AE]].dropna()
    prof_stats = df_prof.groupby(W).agg({AE: ['mean', 'median', 'count']}).round(2)
    prof_stats.columns = ['mean', 'median', 'count']
    prof_stats = prof_stats[prof_stats['count'] >= 5]
    prof_stats = prof_stats.sort_values('mean', ascending=True)

    # 3.1 Bar Chart by Profession
    ax_prof = axes3[0]
    colors_prof = [COLORS['success'] if m <= 7 else COLORS['warning'] if m <= 30 else COLORS['danger']
                   for m in prof_stats['mean']]
    bars = ax_prof.barh([fix_hebrew(str(x)) for x in prof_stats.index], prof_stats['mean'],
                        color=colors_prof, alpha=0.8)
    ax_prof.axvline(7, color=COLORS['warning'], linestyle='--', alpha=0.7, label=fix_hebrew('שבוע'))
    ax_prof.axvline(30, color=COLORS['danger'], linestyle='--', alpha=0.7, label=fix_hebrew('חודש'))
    ax_prof.set_xlabel(fix_hebrew('ממוצע ימים לדיווח'), fontsize=11)
    ax_prof.set_title(fix_hebrew('זמן דיווח לפי מקצוע'), fontsize=12, fontweight='bold')
    ax_prof.legend(loc='lower right', fontsize=10)
    ax_prof.tick_params(axis='y', labelsize=9)

    # 3.2 Scatter - Volume vs Speed
    ax_scatter = axes3[1]
    scatter = ax_scatter.scatter(prof_stats['count'], prof_stats['mean'],
                                 s=120, c=prof_stats['mean'], cmap='RdYlGn_r',
                                 alpha=0.7, edgecolors='black', linewidth=1)
    for idx, row in prof_stats.iterrows():
        if row['count'] > 40 or row['mean'] > 25:
            ax_scatter.annotate(fix_hebrew(str(idx)), (row['count'], row['mean']),
                              fontsize=8, alpha=0.8, xytext=(5, 5), textcoords='offset points')
    ax_scatter.set_xlabel(fix_hebrew('מספר דיווחים'), fontsize=11)
    ax_scatter.set_ylabel(fix_hebrew('ממוצע ימים'), fontsize=11)
    ax_scatter.set_title(fix_hebrew('נפח מול מהירות: מי משפיע הכי הרבה?'), fontsize=12, fontweight='bold')
    ax_scatter.axhline(7, color=COLORS['warning'], linestyle='--', alpha=0.5)
    plt.colorbar(scatter, ax=ax_scatter, label=fix_hebrew('ימים'), shrink=0.8)

    plt.tight_layout()
    plt.subplots_adjust(top=0.92, wspace=0.25)

    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 4: WHERE? - Geographic Patterns
    # ══════════════════════════════════════════════════════════════════════
    fig4, axes4 = plt.subplots(2, 2, figsize=(16, 12))
    fig4.suptitle(fix_hebrew('פרק 4: איפה הבעיה? ניתוח גיאוגרפי'), fontsize=18, fontweight='bold')

    # District analysis
    df_district = df_clean[[DISTRICT, AE, EVENT_TYPE]].dropna(subset=[DISTRICT])
    district_stats = df_district.groupby(DISTRICT).agg({AE: ['mean', 'median', 'count']}).round(2)
    district_stats.columns = ['mean', 'median', 'count']
    district_stats = district_stats.sort_values('count', ascending=True)

    # 4.1 District Volume
    ax_vol = axes4[0, 0]
    colors_dist = plt.cm.Blues(np.linspace(0.4, 0.9, len(district_stats)))
    ax_vol.barh([fix_hebrew(str(x)) for x in district_stats.index], district_stats['count'], color=colors_dist)
    ax_vol.set_xlabel(fix_hebrew('מספר דיווחים'), fontsize=11)
    ax_vol.set_title(fix_hebrew('נפח דיווחים לפי מחוז'), fontsize=12, fontweight='bold')
    ax_vol.tick_params(axis='y', labelsize=10)

    # 4.2 District Speed
    ax_speed = axes4[0, 1]
    district_stats_sorted = district_stats.sort_values('mean')
    colors_speed = [COLORS['success'] if m <= 10 else COLORS['warning'] if m <= 20 else COLORS['danger']
                    for m in district_stats_sorted['mean']]
    ax_speed.barh([fix_hebrew(str(x)) for x in district_stats_sorted.index],
                  district_stats_sorted['mean'], color=colors_speed)
    ax_speed.axvline(district_stats['mean'].mean(), color='black', linestyle='--',
                    label=f'{fix_hebrew("ממוצע")}: {district_stats["mean"].mean():.1f}')
    ax_speed.set_xlabel(fix_hebrew('ממוצע ימים'), fontsize=11)
    ax_speed.set_title(fix_hebrew('מהירות דיווח לפי מחוז'), fontsize=12, fontweight='bold')
    ax_speed.legend(loc='lower right', fontsize=10)
    ax_speed.tick_params(axis='y', labelsize=10)

    # 4.3 Heatmap
    ax_heat = axes4[1, 0]
    heat_data = pd.crosstab(df_clean[DISTRICT], df_clean[EVENT_TYPE])
    heat_data.index = [fix_hebrew(str(x)) for x in heat_data.index]
    heat_data.columns = [fix_hebrew(str(x)[:12]) for x in heat_data.columns]
    sns.heatmap(heat_data, annot=True, fmt='d', cmap='YlOrRd', ax=ax_heat,
                cbar_kws={'label': fix_hebrew('אירועים'), 'shrink': 0.8}, annot_kws={'size': 9})
    ax_heat.set_title(fix_hebrew('מפת חום: מחוז × סוג אירוע'), fontsize=12, fontweight='bold')
    ax_heat.tick_params(axis='x', rotation=45, labelsize=9)
    ax_heat.tick_params(axis='y', labelsize=9)

    # 4.4 Bubble Chart
    ax_bubble = axes4[1, 1]
    scatter = ax_bubble.scatter(
        district_stats['mean'], district_stats['count'],
        s=district_stats['count'] * 1.5, c=district_stats['mean'],
        cmap='RdYlGn_r', alpha=0.6, edgecolors='black', linewidth=1
    )
    for idx, row in district_stats.iterrows():
        ax_bubble.annotate(fix_hebrew(str(idx)), (row['mean'], row['count']),
                          ha='center', va='center', fontsize=9)
    ax_bubble.set_xlabel(fix_hebrew('ממוצע ימים לדיווח'), fontsize=11)
    ax_bubble.set_ylabel(fix_hebrew('מספר דיווחים'), fontsize=11)
    ax_bubble.set_title(fix_hebrew('גודל = נפח, צבע = מהירות'), fontsize=12, fontweight='bold')
    plt.colorbar(scatter, ax=ax_bubble, label=fix_hebrew('ימים'), shrink=0.8)

    plt.tight_layout()
    plt.subplots_adjust(top=0.92, hspace=0.35, wspace=0.3)

    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 5: CONCLUSIONS
    # ══════════════════════════════════════════════════════════════════════
    fig5, ax5 = plt.subplots(figsize=(14, 10))
    fig5.suptitle(fix_hebrew('פרק 5: סיכום ותובנות'), fontsize=18, fontweight='bold')
    ax5.axis('off')

    fastest_prof = prof_stats['mean'].idxmin()
    slowest_prof = prof_stats['mean'].idxmax()
    fastest_district = district_stats['mean'].idxmin()
    slowest_district = district_stats['mean'].idxmax()
    pct_delayed = (df_ae_valid > 7).sum() / len(df_ae_valid) * 100

    summary_lines = [
        "",
        fix_hebrew('סיכום הממצאים העיקריים'),
        "=" * 50,
        "",
        fix_hebrew('היקף:'),
        f"  • {total_events} {fix_hebrew('דיווחים נותחו')}",
        f"  • {negative_records} {fix_hebrew('רשומות עם ערך שלילי הוסרו')}",
        f"  • {total_real_events} {fix_hebrew('אירועים ממשיים')} ({total_real_events/total_events*100:.1f}%)",
        "",
        fix_hebrew('עיכובים:'),
        f"  • {fix_hebrew('ממוצע זמן דיווח:')} {avg_delay:.1f} {fix_hebrew('ימים')}",
        f"  • {fix_hebrew('חציון:')} {median_delay:.0f} {fix_hebrew('ימים')}",
        f"  • {pct_delayed:.1f}% {fix_hebrew('מתעכבים מעל שבוע')}",
        "",
        fix_hebrew('מקצועות:'),
        f"  • {fix_hebrew('מהיר:')} {fix_hebrew(str(fastest_prof))} ({prof_stats.loc[fastest_prof, 'mean']:.1f} {fix_hebrew('ימים')})",
        f"  • {fix_hebrew('איטי:')} {fix_hebrew(str(slowest_prof))} ({prof_stats.loc[slowest_prof, 'mean']:.1f} {fix_hebrew('ימים')})",
        "",
        fix_hebrew('מחוזות:'),
        f"  • {fix_hebrew('מהיר:')} {fix_hebrew(str(fastest_district))} ({district_stats.loc[fastest_district, 'mean']:.1f} {fix_hebrew('ימים')})",
        f"  • {fix_hebrew('איטי:')} {fix_hebrew(str(slowest_district))} ({district_stats.loc[slowest_district, 'mean']:.1f} {fix_hebrew('ימים')})",
        "",
        "=" * 50,
        fix_hebrew('המלצות:'),
        f"  1. {fix_hebrew('הדרכה למקצועות איטיים')}",
        f"  2. {fix_hebrew('למידה מהמחוזות המהירים')}",
        f"  3. {fix_hebrew('יעד: הפחתת עיכובים ב-50%')}",
    ]

    summary_text = '\n'.join(summary_lines)
    ax5.text(0.5, 0.5, summary_text, fontsize=13, ha='center', va='center',
            transform=ax5.transAxes, linespacing=1.6,
            bbox=dict(boxstyle='round,pad=1', facecolor=COLORS['light'], alpha=0.8),
            family='monospace')

    plt.tight_layout()
    plt.subplots_adjust(top=0.92)

    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 6: ESCALATION ANALYSIS - Events requiring external reporting
    # ══════════════════════════════════════════════════════════════════════
    fig6, axes6 = plt.subplots(2, 2, figsize=(18, 14))
    fig6.suptitle(fix_hebrew('פרק 6: אירועים שדרשו דיווח חיצוני - יועמ"ש, ביטוח ומשרד הבריאות'),
                  fontsize=18, fontweight='bold')

    # Prepare data with month
    df_escalation = df_clean[df_clean[EVENT_DATE].notna()].copy()
    df_escalation['month'] = df_escalation[EVENT_DATE].dt.to_period('M')

    # Create flags for external reporting (check for 'כן' or similar positive values)
    df_escalation['needs_legal'] = df_escalation[LEGAL].fillna('').astype(str).str.contains('כן|yes', case=False, na=False)
    df_escalation['needs_insurance'] = df_escalation[INSURANCE].fillna('').astype(str).str.contains('כן|yes', case=False, na=False)
    df_escalation['needs_health_ministry'] = df_escalation[HEALTH_MINISTRY].fillna('').astype(str).str.contains('כן|yes', case=False, na=False)
    df_escalation['needs_any_external'] = df_escalation['needs_legal'] | df_escalation['needs_insurance'] | df_escalation['needs_health_ministry']

    # Count totals
    total_legal = df_escalation['needs_legal'].sum()
    total_insurance = df_escalation['needs_insurance'].sum()
    total_health = df_escalation['needs_health_ministry'].sum()
    total_any = df_escalation['needs_any_external'].sum()

    print("=" * 60)
    print("EXTERNAL REPORTING STATISTICS")
    print("=" * 60)
    print(f"Events requiring Legal (יועמ\"ש): {total_legal}")
    print(f"Events requiring Insurance (ביטוח): {total_insurance}")
    print(f"Events requiring Health Ministry (משרד הבריאות): {total_health}")
    print(f"Events requiring ANY external reporting: {total_any}")
    print("=" * 60 + "\n")

    # 6.1 Stacked Bar - Events vs Near-events by month
    ax_stacked = axes6[0, 0]
    monthly_by_type = df_escalation.groupby(['month', EVENT_OR_NEAR]).size().unstack(fill_value=0)

    # Ensure we have both columns
    if 'אירוע' not in monthly_by_type.columns:
        monthly_by_type['אירוע'] = 0
    if 'כמעט אירוע' not in monthly_by_type.columns:
        monthly_by_type['כמעט אירוע'] = 0

    x_months = range(len(monthly_by_type))
    width = 0.8

    events_vals = monthly_by_type.get('אירוע', pd.Series([0]*len(monthly_by_type))).values
    near_events_vals = monthly_by_type.get('כמעט אירוע', pd.Series([0]*len(monthly_by_type))).values

    ax_stacked.bar(x_months, events_vals, width, label=fix_hebrew('אירוע'), color=COLORS['danger'], alpha=0.8)
    ax_stacked.bar(x_months, near_events_vals, width, bottom=events_vals,
                   label=fix_hebrew('כמעט אירוע'), color=COLORS['info'], alpha=0.8)

    tick_pos = list(range(0, len(monthly_by_type), max(1, len(monthly_by_type)//8)))
    ax_stacked.set_xticks(tick_pos)
    ax_stacked.set_xticklabels([str(monthly_by_type.index[i]) for i in tick_pos], rotation=45, ha='right', fontsize=8)
    ax_stacked.set_xlabel(fix_hebrew('חודש'), fontsize=11)
    ax_stacked.set_ylabel(fix_hebrew('מספר אירועים'), fontsize=11)
    ax_stacked.set_title(fix_hebrew('אירועים וכמעט אירועים לפי חודש'), fontsize=12, fontweight='bold')
    ax_stacked.legend(loc='upper right', fontsize=10)

    # 6.2 Bar Chart - External reporting requirements comparison (with percentages)
    ax_external = axes6[0, 1]
    total_events_ch6 = len(df_escalation)

    external_categories = [
        fix_hebrew('יועמ"ש'),
        fix_hebrew('חברת ביטוח'),
        fix_hebrew('משרד הבריאות')
    ]
    external_values = [total_legal, total_insurance, total_health]
    external_pcts = [v / total_events_ch6 * 100 for v in external_values]
    external_colors = [COLORS['warning'], COLORS['danger'], COLORS['primary']]

    bars_ext = ax_external.bar(external_categories, external_values, color=external_colors, edgecolor='white', linewidth=2)
    for bar, val, pct in zip(bars_ext, external_values, external_pcts):
        ax_external.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                        f'{val}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax_external.set_ylabel(fix_hebrew('מספר אירועים'), fontsize=11)
    ax_external.set_title(fix_hebrew(f'אירועים שדרשו דיווח חיצוני (מתוך {total_events_ch6})'), fontsize=12, fontweight='bold')
    ax_external.set_ylim(0, max(external_values) * 1.35 if max(external_values) > 0 else 10)

    # 6.3 Monthly trend with external reporting highlighted
    ax_trend = axes6[1, 0]

    # Group by month and count events needing external reporting
    monthly_total = df_escalation.groupby('month').size()
    monthly_external = df_escalation[df_escalation['needs_any_external']].groupby('month').size()

    # Align indices
    monthly_external = monthly_external.reindex(monthly_total.index, fill_value=0)

    x_trend = range(len(monthly_total))

    # Plot total events
    ax_trend.fill_between(x_trend, monthly_total.values, alpha=0.3, color=COLORS['info'])
    ax_trend.plot(x_trend, monthly_total.values, color=COLORS['info'], linewidth=2, marker='o',
                  markersize=4, label=fix_hebrew('סה"כ אירועים'))

    # Plot events needing external reporting with warning color
    ax_trend.fill_between(x_trend, monthly_external.values, alpha=0.5, color=COLORS['danger'])
    ax_trend.plot(x_trend, monthly_external.values, color=COLORS['danger'], linewidth=2, marker='s',
                  markersize=4, label=fix_hebrew('דרשו דיווח חיצוני'))

    tick_pos2 = list(range(0, len(monthly_total), max(1, len(monthly_total)//8)))
    ax_trend.set_xticks(tick_pos2)
    ax_trend.set_xticklabels([str(monthly_total.index[i]) for i in tick_pos2], rotation=45, ha='right', fontsize=8)
    ax_trend.set_xlabel(fix_hebrew('חודש'), fontsize=11)
    ax_trend.set_ylabel(fix_hebrew('מספר אירועים'), fontsize=11)
    ax_trend.set_title(fix_hebrew('מגמה חודשית - סה"כ מול אירועים שדרשו דיווח חיצוני'), fontsize=12, fontweight='bold')
    ax_trend.legend(loc='upper right', fontsize=10)

    # 6.4 Breakdown by event type (event vs near-event) and external reporting
    ax_breakdown = axes6[1, 1]

    # Create breakdown data
    breakdown_data = df_escalation.groupby(EVENT_OR_NEAR).agg({
        'needs_legal': 'sum',
        'needs_insurance': 'sum',
        'needs_health_ministry': 'sum'
    }).fillna(0)

    if len(breakdown_data) > 0:
        x_breakdown = np.arange(len(breakdown_data))
        width_bd = 0.25

        legal_vals = breakdown_data['needs_legal'].values
        insurance_vals = breakdown_data['needs_insurance'].values
        health_vals = breakdown_data['needs_health_ministry'].values

        bars1 = ax_breakdown.bar(x_breakdown - width_bd, legal_vals, width_bd,
                                 label=fix_hebrew('יועמ"ש'), color=COLORS['warning'], alpha=0.8)
        bars2 = ax_breakdown.bar(x_breakdown, insurance_vals, width_bd,
                                 label=fix_hebrew('ביטוח'), color=COLORS['danger'], alpha=0.8)
        bars3 = ax_breakdown.bar(x_breakdown + width_bd, health_vals, width_bd,
                                 label=fix_hebrew('משרד הבריאות'), color=COLORS['primary'], alpha=0.8)

        # Add value labels
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax_breakdown.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                                     f'{int(height)}', ha='center', va='bottom', fontsize=9)

        ax_breakdown.set_xticks(x_breakdown)
        ax_breakdown.set_xticklabels([fix_hebrew(str(x)) for x in breakdown_data.index], fontsize=10)
        ax_breakdown.set_xlabel(fix_hebrew('סוג'), fontsize=11)
        ax_breakdown.set_ylabel(fix_hebrew('מספר אירועים'), fontsize=11)
        ax_breakdown.set_title(fix_hebrew('דיווח חיצוני לפי אירוע / כמעט אירוע'), fontsize=12, fontweight='bold')
        ax_breakdown.legend(loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.subplots_adjust(top=0.92, hspace=0.35, wspace=0.25)

    # Show all figures
    plt.show()
