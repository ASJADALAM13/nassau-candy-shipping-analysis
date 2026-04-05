# 🍬 Nassau Candy Distributor — Shipping Route Efficiency Analysis

> *Turning thousands of shipment records into clear, actionable logistics intelligence.*

---

## The Story Behind This Project

Nassau Candy Distributor ships candy products from 5 factories to customers all across the United States and Canada. Every day, hundreds of orders go out — some arrive on time, some don't. The problem? Nobody knew which routes were slow, which factories were causing delays, or whether paying extra for premium shipping was actually worth it.

This project changes that. Using two years of real shipment data, we built a complete data analysis pipeline that answers the question every logistics manager wants answered:

> **"Which routes are working, which aren't, and what should we do about it?"**

---

## What We Found

| What We Looked At | What We Found |
|---|---|
| Total orders analyzed | 10,194 orders over 2 years |
| Routes mapped | 196 unique factory-to-state routes |
| Best performing route | Secret Factory → New Mexico (0% delays, perfect score) |
| Worst performing route | Sugar Shack → New Jersey (100% delays, score: 0.0009) |
| Average lead time | 1,320 days across the entire network |
| Delay rate | 33.14% of all shipments arrive late |
| Best shipping method | Standard Class — fastest AND most profitable |
| Surprising finding | First Class is actually the slowest ship mode |

---

## What's Inside This Project

```
nassau_candy_project/
│
├── 📓 notebook/
│   └── Project.ipynb          ← Full EDA with step by step analysis
│
├── 📊 dashboard/
│   └── app.py                 ← Interactive Streamlit dashboard
│
├── 📄 report/
│   ├── Nassau_Candy_EDA_Report.docx        ← Full research paper
│   └── Nassau_Candy_Executive_Summary.docx ← 1 page stakeholder summary
│
├── 📦 data/                   ← Dataset folder (not included in repo)
├── requirements.txt           ← All Python libraries needed
└── README.md                  ← You are here
```

---

## The Dashboard

The Streamlit dashboard has 4 modules:

**Module 1 — Route Efficiency Overview**
See which routes are performing best and worst, with a full ranked leaderboard of all 196 routes and a CSV download option.

**Module 2 — Geographic Shipping Map**
An interactive North America map showing delivery performance by state and province. Switch between customer destinations view and the complete shipping network with factory locations marked as gold stars.

**Module 3 — Ship Mode Comparison**
Side by side comparison of all 4 shipping methods by average lead time and delay frequency.

**Module 4 — Route Drill Down**
Factory performance rankings, top 15 most delayed states, and order-level shipment data — all filterable by date, region, state, ship mode, and lead time threshold.

---

## How to Run It Yourself

**Step 1 — Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/nassau-candy-shipping-analysis.git
cd nassau-candy-shipping-analysis
```

**Step 2 — Install the libraries**
```bash
pip install -r requirements.txt
```

**Step 3 — Add the dataset**
Place the Nassau Candy Distributor CSV file in the `data/` folder.

**Step 4 — Run the EDA notebook**
```bash
jupyter notebook notebook/Project.ipynb
```

**Step 5 — Launch the dashboard**
```bash
streamlit run dashboard/app.py
```

---

## Libraries Used

```
pandas          — data cleaning and analysis
numpy           — numerical calculations
plotly          — interactive charts and maps
streamlit       — web dashboard
scikit-learn    — route efficiency score normalization
matplotlib      — chart image export
kaleido         — saving plotly charts as images
openpyxl        — Excel file support
jupyter         — notebook environment
```

---

## The Three Deliverables

This project was built as part of a Data Analytics Internship with Nassau Candy Distributor. The three required deliverables are:

1. **EDA Research Paper** — A complete 10 section analysis document with findings, charts, and recommendations written for a technical audience.

2. **Streamlit Dashboard** — A live interactive analytics dashboard that lets logistics managers explore the data themselves with filters and drill-downs.

3. **Executive Summary** — A clean one page document written for government and senior stakeholders who need the key findings without the technical detail.

---

## About

**Analyst:** MD Asjad Alam
**Program:** Data Analytics Internship
**Organization:** Nassau Candy Distributor
**Date:** April 2026
**GitHub:** [nassau-candy-shipping-analysis](https://github.com/YOUR_USERNAME/nassau-candy-shipping-analysis)

---

*Built with Python, Pandas, Plotly, and Streamlit.*
