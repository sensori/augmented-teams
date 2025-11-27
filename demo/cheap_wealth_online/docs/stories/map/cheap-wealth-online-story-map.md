# Story Map: Cheap Wealth Online

**Navigation:** [📊 Increments](../increments/cheap-wealth-online-story-map-increments.md)

**File Name**: `cheap-wealth-online-story-map.md`
**Location**: `demo/cheap_wealth_online/docs/stories/map/cheap-wealth-online-story-map.md`

> **CRITICAL MARKDOWN FORMATTING**: All tree structure lines MUST end with TWO SPACES (  ) for proper line breaks. Without two spaces, markdown will wrap lines together into one long line, breaking the visual tree structure.

> **CRITICAL HIERARCHY FORMATTING**: The epic_hierarchy section MUST use tree structure characters to show hierarchy:
> - Use `│` (vertical line) for continuing branches
> - Use `├─` (branch) for items that have siblings below them
> - Use `└─` (end branch) for the last item in a group
> - Epic format: `🎯 **Epic Name** (X features, ~Y stories)  `
> - Feature format: `├─ ⚙️ **Feature Name** (~Z stories)  ` or `└─ ⚙️ **Feature Name** (~Z stories)  ` for last feature
> - Story format (when present): `│  ├─ 📝 Story: [Verb-Noun Name]  ` followed by `│  │  *[Component interaction description]*  ` on the next line, or `│  └─ 📝 Story: [Verb-Noun Name]  ` for last story
> - **MANDATORY STORY NAMING FORMAT**: All story names MUST follow Actor-Verb-Noun format:
>   - Story name: Concise Verb-Noun format (e.g., "Create Mob from Selected Tokens", "Display Mob Grouping in Combat Tracker", "Execute Mob Attack with Strategy")
>   - Description: Italicized component interaction description showing component-to-component interactions (e.g., "*GM selects multiple minion tokens on canvas and Mob manager creates mob with selected tokens and assigns random leader*")
> - Example structure:
>   ```
>   🎯 **Epic Name** (2 features, ~8 stories)  
>   │  
>   ├─ ⚙️ **Feature 1** (~5 stories)  
>   │  ├─ 📝 Story: Create Mob from Selected Tokens  
>   │  │  *GM selects multiple minion tokens on canvas and Mob manager creates mob*  
>   │  └─ 📝 Story: Display Mob Grouping  
>   │     *Combat Tracker receives mob creation notification and updates display*  
>   │  
>   └─ ⚙️ **Feature 2** (~3 stories)  
>      └─ 📝 Story: Execute Mob Attack  
>         *Combat Tracker moves to mob leader's turn and Mob manager forwards action*  
>   ```

## System Purpose
Enable retail investors to quickly onboard, fund accounts, and invest in stocks and ETFs through a user-friendly platform with fractional shares, auto-investing, and robo-advisor capabilities, while maintaining regulatory compliance and operational efficiency.

---

## Legend
- 🎯 **Epic** - High-level capability
- 📂 **Sub-Epic** - Sub-capability (when epic has > 9 features)
- ⚙️ **Feature** - Cohesive set of functionality
- 📝 **Story** - Small increment of behavior (3-12d)

---

## Story Map Structure

🎯 **Onboard Users** (2 features, ~2 stories)  
│  
├─ ⚙️ **Verify Identity and Assign KYC Tier** (~1 story)  
│  └─ 📝 Story: Verify Identity in 3 Minutes  
│     *User scans driver's license or passport, System verifies document via ID verification provider, System assigns KYC tier based on verification results, System grants account access appropriate to tier*  
│  
└─ ⚙️ **Save Partial Onboarding State** (~1 story)  
   └─ 📝 Story: Resume Abandoned Onboarding  
      *User starts onboarding but doesn't complete, System saves partial state (completed steps, entered data), System sends email nudge after delay, User clicks link in email, System resumes from saved state*  

🎯 **Fund Accounts** (4 features, ~4 stories)  
│  
├─ ⚙️ **Link Bank Account via Plaid/Flinks** (~1 story)  
│  └─ 📝 Story: Link Bank and Enable ACH Funding  
│     *User initiates bank connection, System connects via Plaid/Flinks, System initiates micro-deposit verification (two small deposits), User confirms deposit amounts, System enables ACH funding capability, System displays funding timeline*  
│  
├─ ⚙️ **Enable Instant Deposit with Risk Engine** (~1 story)  
│  └─ 📝 Story: Approve Instant Deposit via Risk Engine  
│     *User requests instant deposit, System runs risk engine (evaluates user activity + deposit history + external data), System calculates risk score, If approved: System credits account immediately, If denied: System falls back to standard ACH flow*  
│  
├─ ⚙️ **Handle Failed ACH and Account Freeze** (~1 story)  
│  └─ 📝 Story: Freeze Account on Failed ACH  
│     *ACH payment fails (insufficient funds, account closed, etc.), System flags account, System freezes all trading activity, System displays red warning banner to user, System sends email notification, User must resolve issue before trading resumes*  
│  
└─ ⚙️ **Convert Foreign Currency for US Assets** (~1 story)  
   └─ 📝 Story: Convert Currency for US Stock Purchase  
      *User deposits Canadian dollars, User attempts to buy US stock, System detects currency mismatch, System converts CAD to USD at current exchange rate, System applies FX markup fee, System executes trade with converted amount*  

🎯 **Trade Securities** (1 feature, ~1 story)  
│  
└─ ⚙️ **Place Market Order for Fractional Shares** (~1 story)  
   └─ 📝 Story: Execute Market Order with Price Visibility  
      *User searches for ticker symbol, System displays current market price (delayed or real-time), User places market order for fractional shares, System shows estimated execution price, System routes order to custodian, System receives execution confirmation with final fill price, System updates portfolio holdings*  

🎯 **Manage Portfolios** (3 features, ~3 stories)  
│  
├─ ⚙️ **Set Up Auto-Investing with Weekly Deposits** (~1 story)  
│  └─ 📝 Story: Configure Auto-Investing Schedule  
│     *User sets weekly deposit amount, User configures asset allocation percentages, System schedules automatic trades for each deposit, System monitors portfolio drift daily, System triggers rebalancing when allocation drifts 5% from target*  
│  
├─ ⚙️ **Complete Robo-Advisor Questionnaire** (~1 story)  
│  └─ 📝 Story: Get Robo-Advisor Portfolio Recommendation  
│     *User answers questionnaire (goals, time horizon, risk tolerance), System analyzes responses, System recommends model portfolio (Conservative/Balanced/Growth/Aggressive), User reviews and accepts recommendation, System allocates funds automatically, System displays Monte-Carlo projection chart with disclaimers*  
│  
└─ ⚙️ **Rebalance Robo-Advisor Portfolio** (~1 story)  
   └─ 📝 Story: Trigger Rebalancing on Drift Threshold  
      *System monitors robo-advisor portfolio allocation daily, System compares current allocation to target model portfolio, System detects allocation drift exceeds 5% threshold, System calculates required rebalancing trades, System executes trades automatically, System notifies user of rebalancing activity*  

🎯 **Monitor and Alert** (1 feature, ~1 story)  
│  
└─ ⚙️ **Set Price Alerts and Receive Notifications** (~1 story)  
   └─ 📝 Story: Receive Price Alert and Take Action  
      *User sets price alert ('Alert me when TSLA drops below $150'), System monitors market data for ticker, System detects condition met (price drops to $149), System sends push notification and email, User views alert, User can place trade directly from alert notification*  

🎯 **Handle Compliance and Operations** (4 features, ~4 stories)  
│  
├─ ⚙️ **Generate Tax Forms by Region** (~1 story)  
│  └─ 📝 Story: Download Regional Tax Forms  
│     *User requests tax forms from account settings, System determines user's region (Canada vs US), System generates appropriate tax forms (T5/T3 for Canada, 1099/8949 for US), System calculates all required tax data (dividends, capital gains, cost basis), System generates PDF documents, System provides download link, System archives forms for 7-year retention*  
│  
├─ ⚙️ **Perform Real-Time AML/OFAC Compliance Checks** (~1 story)  
│  └─ 📝 Story: Check Deposit Against AML/OFAC Lists  
│     *User initiates deposit transaction, System triggers AML/OFAC compliance check, System queries compliance service with user and transaction data, System receives check result, If flagged: System freezes account and alerts compliance team, If clear: System processes deposit normally*  
│  
├─ ⚙️ **Review Suspicious Trades in Admin Dashboard** (~1 story)  
│  └─ 📝 Story: Escalate Suspicious Trade to Compliance  
│     *System detects suspicious trade pattern (e.g., rapid trading, unusual amounts), System flags account in admin dashboard, Admin views trade details and user profile, Admin can freeze account if needed, Admin escalates case to compliance team, System logs all admin actions in audit trail*  
│  
└─ ⚙️ **Reconcile Trades with Custodian Daily** (~1 story)  
   └─ 📝 Story: Reconcile Daily Trades with Custodian  
      *Nightly batch job runs at scheduled time, System queries custodian API for all trades executed that day, System retrieves internal trade records from database, System compares custodian trades with internal records, System flags any discrepancies (missing trades, mismatched prices, etc.), System generates reconciliation report, Operations team reviews report next morning*  

---

## Source Material

**Shape Phase:**
- **Primary Source Document**: `demo/cheap_wealth_online/notes.txt` - Rough, unstructured requirements dump for WealthSimple-style investing/brokerage platform
- **Sections Referenced**: 
  - User Onboarding (Brain-Dump)
  - Account Types (Scatter Notes)
  - Funding / Money Movement
  - Trading & Instruments (Chaotic Notes)
  - Portfolio Stuff
  - Robo-Advisor / Managed Investing (Random Notes)
  - Notifications & Alerts (Misc Dump)
  - Security (All Over The Place)
  - Back Office / Operations
  - Legal & Compliance (Everything We Keep Forgetting)
- **Date Generated**: 2024-11-26
- **Context Note**: Initial shaping of messy, unstructured requirements into organized story map with 6 epics, 15 stories, and 5 marketable increments. Focus on end-to-end user-system behaviors where architectural uncertainty, business complexity, uniqueness, integration complexity, or user behavior variability exists.




