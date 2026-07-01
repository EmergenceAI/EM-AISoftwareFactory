# SDLC Metrics - Complete Guide

## 🎉 **System Ready!**

You now have a complete SDLC metrics system with:
- ✅ Automated data collection (GitHub + Jira)
- ✅ Excel reports
- ✅ Power BI data exports
- ✅ Daily/Weekly/Monthly automation

---

## 📊 **Quick Start - Generate Reports Now**

### Option 1: Daily Report (Yesterday's Data)
```bash
cd /Users/malamunisamy/Documents/Development/em-sdlc-metrics
./generate_daily_report.sh
```
**Output:** `SDLC_Metrics_daily_YYYYMMDD.xlsx`

### Option 2: Weekly Report (Last 7 Days)
```bash
./generate_weekly_report.sh
```
**Output:** `SDLC_Metrics_weekly_YYYYMMDD.xlsx`

### Option 3: Complete Report (Excel + Power BI)
```bash
./generate_all_reports.sh 7 weekly
```
**Output:** 
- Excel report
- Power BI data (7 CSV files)

---

## 🔷 **Power BI Setup (5 Minutes)**

### Step 1: Open Power BI Desktop

### Step 2: Import Data
1. Click **Get Data** > **Folder**
2. Browse to: `/Users/malamunisamy/Documents/Development/em-sdlc-metrics/powerbi_export`
3. Click **Combine** > **Combine & Transform**
4. Click **Close & Apply**

### Step 3: Create Relationships (Model View)
```
velocity_by_repo[repository] -> dim_repository[repository]
velocity_by_repo[metric_week] -> dim_date[week]
bug_metrics[repository] -> dim_repository[repository]
```

### Step 4: Add Measures
```dax
Avg Cycle Time (Days) = AVERAGE(velocity_by_repo[avg_cycle_time_hours]) / 24
Total PRs = SUM(velocity_by_repo[prs_merged])
Total Bugs = SUM(bug_metrics[total_bugs])
```

### Step 5: Create Visuals
- **Line Chart**: Cycle time trend by week
- **Bar Chart**: PRs merged by repository
- **Cards**: KPIs (Avg Cycle Time, Total PRs, Total Bugs)

---

## 📈 **What You Get**

### Excel Report Contains:
1. **Summary** - Key metrics at a glance
2. **Velocity by Repo** - Weekly cycle times per repository
3. **Velocity by Platform** - Semiconductor vs CRAFT comparison
4. **Bug Metrics** - Bug quality analysis
5. **Sample PRs** - Drill-down data
6. **Sample Bugs** - Drill-down data

### Power BI Data Contains:
1. **velocity_by_repo.csv** (99 rows) - Weekly metrics per repo
2. **velocity_by_platform.csv** (46 rows) - Platform aggregates
3. **bug_metrics.csv** (20 rows) - Weekly bug stats
4. **pull_requests_detail.csv** (2,309 rows) - Individual PRs
5. **bugs_detail.csv** (202 rows) - Individual bugs
6. **dim_repository.csv** (5 rows) - Repository dimension
7. **dim_date.csv** (23 rows) - Date dimension

---

## 🤖 **Automation Setup**

### Daily Reports (Every Day @ 8am)
```bash
crontab -e
# Add this line:
0 8 * * * cd /Users/malamunisamy/Documents/Development/em-sdlc-metrics && ./generate_daily_report.sh >> logs/daily_$(date +\%Y\%m\%d).log 2>&1
```

### Weekly Reports (Every Monday @ 9am)
```bash
# Add this line to crontab:
0 9 * * 1 cd /Users/malamunisamy/Documents/Development/em-sdlc-metrics && ./generate_weekly_report.sh >> logs/weekly_$(date +\%Y\%m\%d).log 2>&1
```

### Power BI Refresh (Every Day @ 6am)
```bash
# Add this line to crontab:
0 6 * * * cd /Users/malamunisamy/Documents/Development/em-sdlc-metrics && source .venv/bin/activate && python export_for_powerbi.py >> logs/powerbi_$(date +\%Y\%m\%d).log 2>&1
```

**Create logs directory:**
```bash
cd /Users/malamunisamy/Documents/Development/em-sdlc-metrics
mkdir -p logs
```

---

## 📊 **Current Metrics (YTD 2026)**

### Repositories Tracked:
1. **em-semi** (Semiconductor) - 680 PRs, 65 hrs avg cycle time
2. **em-runtime-ui** (CRAFT) - 288 PRs, 40 hrs avg cycle time
3. **em-talk2data** (CRAFT) - 384 PRs, 31 hrs avg cycle time
4. **em-data-readiness** (CRAFT) - 766 PRs, 41 hrs avg cycle time
5. **em-runtime** (CRAFT) - 537 PRs, 27 hrs avg cycle time ⭐ BEST

### Key Insights:
- **Total PRs Analyzed:** 2,572
- **Total Bugs Tracked:** 202
- **CRAFT Platform:** 35.3 hrs avg cycle time (1.5 days) ⭐
- **Semiconductor Platform:** 64.9 hrs avg cycle time (2.7 days) ⚠
- **Best Performer:** em-runtime (27 hrs = 1.1 days)

---

## 🔧 **Customization**

### Collect Custom Date Range
```bash
# Last 30 days
./generate_all_reports.sh 30 monthly

# Last 90 days (quarterly)
./generate_all_reports.sh 90 quarterly

# Year to date
./generate_all_reports.sh 158 ytd
```

### Add More Repositories
Edit: `/Users/malamunisamy/Documents/Development/em-sdlc-metrics/.env`
```bash
REPOSITORIES=em-semi,em-runtime-ui,em-talk2data,em-data-readiness,em-runtime,NEW_REPO
```

Edit: `/Users/malamunisamy/Documents/Development/em-sdlc-metrics/config/repo_mappings.yaml`
```yaml
repositories:
  NEW_REPO:
    jira_projects:
      - PROJECT_KEY
    platform: craft  # or semiconductor
    description: "Description"
```

---

## 📁 **File Locations**

### Reports (Excel)
```
/Users/malamunisamy/Documents/Development/em-sdlc-metrics/
  ├── SDLC_Metrics_daily_YYYYMMDD.xlsx
  ├── SDLC_Metrics_weekly_YYYYMMDD.xlsx
  └── SDLC_Metrics_monthly_YYYYMMDD.xlsx
```

### Power BI Data
```
/Users/malamunisamy/Documents/Development/em-sdlc-metrics/powerbi_export/
  ├── velocity_by_repo.csv
  ├── velocity_by_platform.csv
  ├── bug_metrics.csv
  ├── pull_requests_detail.csv
  ├── bugs_detail.csv
  ├── dim_repository.csv
  └── dim_date.csv
```

### Documentation
```
/Users/malamunisamy/Documents/Development/em-sdlc-metrics/
  ├── HOWTO_GENERATE_REPORTS.md      # Report generation guide
  ├── AUTOMATION_GUIDE.md             # Automation setup guide
  ├── DATA_COLLECTION_SUMMARY.md      # What was collected
  └── YTD_2026_COLLECTION_SUMMARY.md  # Current data summary
```

---

## 🎯 **Key Metrics Explained**

### Cycle Time (PRIMARY METRIC)
**Formula:** `PR merged_at - first_commit_at`  
**What it measures:** Total dev time from first code to production-ready  
**Target:** < 48 hours (2 days)

### Time to First Review
**Formula:** `first_review_at - PR created_at`  
**What it measures:** Review responsiveness  
**Target:** < 8 hours

### Defect Escape Rate
**Formula:** `(production_bugs / total_bugs) × 100`  
**What it measures:** % of bugs reaching production  
**Target:** < 5%

---

## 🆘 **Troubleshooting**

### Reports not generating?
```bash
# Check if scripts are executable
cd /Users/malamunisamy/Documents/Development/em-sdlc-metrics
ls -l *.sh

# Make executable if needed
chmod +x *.sh
```

### Python errors?
```bash
# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

### Cron jobs not running?
```bash
# Check crontab
crontab -l

# View logs
tail -f logs/weekly_*.log
```

---

## 📧 **Next Steps**

1. ✅ **Test Reports** - Run `./generate_weekly_report.sh` now
2. ✅ **Set Up Power BI** - Import data and create dashboards
3. ✅ **Enable Automation** - Add cron jobs for daily/weekly reports
4. 📧 **Share Reports** - Email Excel reports to stakeholders
5. 📊 **Build Dashboards** - Create Power BI visualizations
6. 🔄 **Monitor Trends** - Track cycle time improvements weekly

---

## 📞 **Support**

**Documentation:**
- Report Generation: `HOWTO_GENERATE_REPORTS.md`
- Automation: `AUTOMATION_GUIDE.md`
- Cycle Time Strategy: `docs/CYCLE_TIME_STRATEGY.md`

**Quick Help:**
```bash
# View available scripts
ls -l /Users/malamunisamy/Documents/Development/em-sdlc-metrics/*.sh

# Test collection (1 day)
./generate_daily_report.sh 1

# View latest report
open SDLC_Metrics_*.xlsx
```

---

**System Status:** ✅ Ready for Production  
**Last Data Collection:** June 7, 2026  
**Repositories:** 5  
**Total PRs:** 2,572  
**Total Bugs:** 202  
**Automation:** Ready to Enable
