# Story Map Increments: Spider-Man Fan Community Website

**Navigation:** [📋 Story Map](../map/spider-man-fan-community-story-map.md) | [🔗 Repository](https://github.com/thomasjeffreyandersontwin/augmented-teams)

**File Name**: `spider-man-fan-community-story-map-increments.md`
**Location**: `spider_man_fan/docs/stories/increments/spider-man-fan-community-story-map-increments.md`

> **CRITICAL MARKDOWN FORMATTING**: All tree structure lines MUST end with TWO SPACES (  ) for proper line breaks. Without two spaces, markdown will wrap lines together into one long line, breaking the visual tree structure.

## Increment Planning Philosophy

**🎯 VERTICAL SLICES - NOT Horizontal Layers**

Each increment should deliver a **thin end-to-end working flow** across multiple features/epics, NOT complete one feature/epic at a time.

- ✅ **DO**: Include PARTIAL features from MULTIPLE epics in each increment
- ✅ **DO**: Ensure each increment demonstrates complete flow: input → process → validate → persist → display
- ✅ **DO**: Layer complexity across increments (simple first, then add users/scenarios/edge cases)
- ❌ **DON'T**: Complete entire Epic A, then Epic B, then Epic C
- ❌ **DON'T**: Build increments that can't demonstrate working end-to-end flow

**Layering Strategy:**
- **Increment 1**: Simplest user + simplest scenario + happy path → Full end-to-end
- **Increment 2**: Add complexity (more options, validations) + Additional users → Full end-to-end  
- **Increment 3**: Add edge cases + Error handling + Advanced features → Full end-to-end

## Legend
- 🎯 **Epic** - High-level capability
- 📂 **Sub-Epic** - Sub-capability (when epic has > 9 features)
- ⚙️ **Feature** - Cohesive set of functionality
- 📝 **Story** - Small increment of behavior (3-12d)

---

## Increment 1: Foundation & Discovery

**Priority:** NOW  
**Relative Size:** Medium  
**Approach:** Delivering End-to-End Journey  
**Focus:** User accounts + basic profiles + basic search

**Purpose:** Enables all other features, validates user interest. Delivers complete user journey from sign-up to discovery.

🎯 **Manage User Accounts**  
│  
├─ ⚙️ **Create User Account** (5 stories)  
│  ├─ 📝 Story: Sign Up with Email  
│  │  *User enters email address and password on sign-up form, then system validates email format and password strength, creates account in database, and sends verification email via email service*  
│  ├─ 📝 Story: Verify Email Address  
│  │  *User clicks verification link in email, then system verifies email address and activates account*  
│  ├─ 📝 Story: Log In to Account  
│  │  *User enters email and password, then system authenticates credentials and logs user into their account*  
│  ├─ 📝 Story: Reset Forgotten Password  
│  │  *User requests password reset, then system sends password reset email with link, and user sets new password*  
│  └─ 📝 Story: Log Out of Account  
│     *User clicks log out, then system ends user session and redirects to home page*  
│  
└─ ⚙️ **Build User Profile** (6 stories)  
   ├─ 📝 Story: Create Basic Profile  
   │  *User enters username and bio after account creation, then system saves profile information and displays profile page*  
   ├─ 📝 Story: Upload Profile Picture  
   │  *User selects image file and uploads, then system validates image format and size, uploads to file storage, and displays on profile*  
   ├─ 📝 Story: Edit Profile Information  
   │  *User updates username, bio, or other profile fields, then system validates changes and saves updated profile*  
   ├─ 📝 Story: View User Profile  
   │  *User navigates to profile page, then system displays profile information including username, bio, profile picture, and account creation date*  
   ├─ 📝 Story: View Other User Profile  
   │  *User clicks on another user's name or profile link, then system displays that user's public profile information*  
   └─ 📝 Story: Set Favorite Character  
      *User selects favorite Spider-Man character from list, then system saves preference and displays on profile*  

🎯 **Search and Discover Content**  
│  
├─ ⚙️ **Search Content** (5 stories)  
│  ├─ 📝 Story: Search by Keyword  
│  │  *User enters search term in search bar and clicks search, then system searches across merchandise, users, and videos and displays matching results*  
│  ├─ 📝 Story: View Search Results  
│  │  *System displays search results grouped by type (merchandise, users, videos), then user can click on any result to view details*  
│  ├─ 📝 Story: Search for Users  
│  │  *User selects 'Users' filter and enters search term, then system searches user profiles and displays matching users*  
│  ├─ 📝 Story: Search for Merchandise  
│  │  *User selects 'Merchandise' filter and enters search term, then system searches merchandise posts and displays matching items*  
│  └─ 📝 Story: View Empty Search Results  
│     *User searches for term with no matches, then system displays message indicating no results found and suggests alternative searches*  
│  
└─ ⚙️ **Browse by Category** (4 stories)  
   ├─ 📝 Story: Browse Category List  
   │  *User navigates to browse page, then system displays list of available categories (Comics, Action Figures, Videos, etc.)*  
   ├─ 📝 Story: View Category Content  
   │  *User clicks on category, then system displays all merchandise and videos in that category with pagination*  
   ├─ 📝 Story: Sort Category Results  
   │  *User selects sort option (newest, oldest, most popular), then system reorders category content and displays sorted results*  
   └─ 📝 Story: Navigate Category Pages  
      *User clicks next page or page number, then system loads and displays next page of category content*  

---

## Increment 2: Merchandise Sharing

**Priority:** NOW  
**Relative Size:** Large  
**Approach:** Maximizing Earned Value  
**Focus:** Upload merchandise photos + view posts + basic collections

**Purpose:** Core value proposition, enables trading. Delivers complete flow from uploading merchandise to viewing and organizing collections.

> **Note:** Stories for these features have not been drilled down yet. The increment includes all stories within these features (estimated counts shown).

🎯 **Share Merchandise**  
│  
├─ ⚙️ **Upload Merchandise Photos** (~5 stories)  
│  *All stories in this feature are included in this increment*  
│  
├─ ⚙️ **Organize Collections** (~4 stories)  
│  *All stories in this feature are included in this increment*  
│  
└─ ⚙️ **Interact with Merchandise Posts** (~4 stories)  
   *All stories in this feature are included in this increment*  

---

## Increment 3: Basic Trading

**Priority:** NOW  
**Relative Size:** Large  
**Approach:** Validating Impact-Feasibility  
**Focus:** Mark items for trade + create/view proposals + basic completion

**Purpose:** Differentiates platform, derisks complex trading flow. Delivers end-to-end trading journey from marking items to completing trades.

**Domain Concepts:**
- **Trade Proposal:** A request from one user to another to exchange specific items, including items offered and items requested
- **Trade Status:** The current state of a trade: pending, accepted, rejected, completed, or cancelled
- **Trade Completion:** The finalization of a trade where both users confirm receipt and items are marked as traded

**Domain Behaviors:**
- **Trade Proposal:** User selects items from their collection and items from target user's collection, then system creates trade proposal and notifies target user
- **Trade Completion:** User accepts trade proposal, then system updates trade status to accepted, marks items as traded, and enables rating after completion

🎯 **Trade Items**  
│  
├─ ⚙️ **Mark Items for Trade** (~3 stories)  
│  
├─ ⚙️ **Propose Trade** (2 stories)  
│  ├─ 📝 Story: Create Trade Proposal  
│  │  *User selects items from their collection and items from another user's available-for-trade collection, then system creates trade proposal and sends notification to target user*  
│  └─ 📝 Story: View Trade Proposal  
│     *User receives notification of trade proposal, then system displays proposal details showing items offered and items requested*  
│  
└─ ⚙️ **Complete Trade** (1 story)  
   └─ 📝 Story: Accept Trade Proposal  
      *User clicks accept on trade proposal, then system updates trade status to accepted, marks both users' items as traded, and enables rating option for both users*  

---

## Increment 4: Fan Films

**Priority:** NOW  
**Relative Size:** Medium  
**Approach:** Delivering End-to-End Journey  
**Focus:** Upload fan films + watch films + basic metadata

**Purpose:** Completes Phase 1, validates video infrastructure. Delivers complete flow from uploading videos to watching them.

**Domain Concepts:**
- **Video Upload:** The process of transferring video file from user's device to system's video storage service
- **Video Processing:** System processes uploaded video for streaming, including format conversion and thumbnail generation
- **Video Streaming:** The delivery of video content from video storage service to user's browser for playback

**Domain Behaviors:**
- **Video Upload:** User selects video file and uploads, then system validates file size and format, transfers to video storage service, and processes for streaming
- **Video Streaming:** User clicks play on video, then system requests video stream from video storage service and video player displays streaming content

🎯 **Upload and View Fan Movies**  
│  
├─ ⚙️ **Upload Fan Film** (3 stories)  
│  ├─ 📝 Story: Upload Video File  
│  │  *User selects video file and clicks upload, then system validates file size and format, transfers file to video storage service, and initiates video processing*  
│  ├─ 📝 Story: Add Video Metadata  
│  │  *User enters title, description, category, and character tags for video, then system saves metadata and links it to video file*  
│  └─ 📝 Story: Publish Fan Film  
│     *User clicks publish after video processing completes, then system makes video available for viewing and adds it to creator's profile*  
│  
└─ ⚙️ **Watch Fan Films** (1 story)  
   └─ 📝 Story: Play Fan Film  
      *User clicks play button on video, then system requests video stream from video storage service and video player displays streaming content with playback controls*  

---

## Increment 5: Community Engagement

**Priority:** NEXT  
**Relative Size:** Medium  
**Approach:** Maximizing Earned Value  
**Focus:** Forums + comments + ratings + notifications

**Purpose:** Increases engagement and retention. Delivers community interaction features with notification support.

**Domain Concepts:**
- **Forum Thread:** A discussion topic started by a user with a title and initial post, which other users can reply to
- **Forum Reply:** A response to a forum thread that appears in chronological order within the thread
- **Post Vote:** A user's upvote or downvote on a forum post that affects the post's visibility and ranking
- **Email Notification:** An email message sent to user's email address via email service when specific events occur

**Domain Behaviors:**
- **Forum Thread:** User writes post title and content, selects forum topic, then system creates new thread and displays it in forum topic list
- **Forum Reply:** User writes reply content, then system adds reply to thread in chronological order and notifies thread creator
- **Post Vote:** User clicks upvote or downvote on post, then system records vote, updates post score, and adjusts post ranking in thread
- **Email Notification:** System detects trade event, checks user's notification preferences, then email service sends notification email to user's email address

🎯 **Participate in Community**  
│  
├─ ⚙️ **Create Forum Post** (1 story)  
│  └─ 📝 Story: Start Discussion Thread  
│     *User writes post title and content, selects forum topic category, then system creates new thread, adds it to forum topic list, and displays thread to other users*  
│  
├─ ⚙️ **Reply to Thread** (1 story)  
│  └─ 📝 Story: Post Thread Reply  
│     *User writes reply content and clicks post, then system adds reply to thread in chronological order, updates thread activity timestamp, and sends notification to thread creator*  
│  
└─ ⚙️ **Vote on Posts** (1 story)  
   └─ 📝 Story: Vote on Forum Post  
      *User clicks upvote or downvote button on post, then system records vote, updates post score, recalculates post ranking in thread, and updates display order*  

🎯 **Manage Notifications**  
│  
├─ ⚙️ **Receive Trade Notifications** (2 stories)  
│  ├─ 📝 Story: Send Trade Proposal Email  
│  │  *System detects new trade proposal, checks recipient's notification preferences, then email service sends notification email with trade details to recipient's email address*  
│  └─ 📝 Story: Send Trade Message Email  
│     *System detects new trade message, checks recipient's notification preferences, then email service sends notification email with message preview to recipient's email address*  
│  
└─ ⚙️ **Receive Comment Notifications** (1 story)  
   └─ 📝 Story: Send Comment Notification Email  
      *System detects comment on user's merchandise post or fan film, checks user's notification preferences, then email service sends notification email with comment preview to user's email address*  

---

## Source Material

- **Product Requirements Document**: `spider_man_fan/requirements.md` - Comprehensive requirements document covering features, technical specifications, user experience goals, and launch priorities
- **Clarification Decisions**: `spider_man_fan/docs/activity/story_bot/clarification.json` - Detailed answers to key questions about user types, goals, problems, external systems, and integration points
- **Planning Decisions**: `spider_man_fan/docs/activity/story_bot/planning.json` - Decisions on exploration depth, scope level, depth of shaping for various phases, drill-down limits, and prioritization strategy
- **Story Map**: `spider_man_fan/docs/stories/structured.json` - Complete structured story map with epics, features, stories, and increments

**Discovery Refinements:**
- Enumerated all 20 stories for Foundation & Discovery increment (replaced ~X stories notation with explicit story lists)
- Create User Account: 5 stories explicitly listed with component interaction descriptions
- Build User Profile: 6 stories explicitly listed with component interaction descriptions
- Search Content: 5 stories explicitly listed with component interaction descriptions
- Browse by Category: 4 stories explicitly listed with component interaction descriptions
- All stories follow user-system interaction granularity for design and testing clarity
- Stories show component-to-component interactions (user actions → system responses)

