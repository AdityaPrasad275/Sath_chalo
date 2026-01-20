# Frontend Design Philosophy

> **Core Thesis**: We're not building a transit app. We're building an anxiety medication that happens to show buses.

---

## The Problem We're Solving

### What Incumbents Get Wrong

| Problem | Google Maps / Moovit |
|---------|---------------------|
| **Cognitive Load** | 2D maps, pinch-zoom, route planning — overwhelming |
| **Target User** | Lost tourists, first-timers who need discovery |
| **Update Speed** | Slow ML inference, 6+ months to reflect road changes |
| **UI Density** | Cluttered, ad-heavy (Moovit), municipal-feeling |
| **Core Experience** | "Here's information, figure it out" |

### What Daily Commuters Actually Need

Regular commuters don't need:
- ❌ Directions
- ❌ Discovery  
- ❌ Onboarding
- ❌ Route planning

They need:
- ✅ **Reassurance** — "Is the bus coming?"
- ✅ **Confidence** — "Am I at the right stop?"
- ✅ **Normalcy** — "Today is on schedule"

**This is a psychological product, not a mapping product.**

---

## The Gold Standard UX Question

> **Can I use this app without consciously "using" it?**

If the app feels like:
- 🎵 Music playing in the background
- 🪟 Looking out the window
- 💆 Background reassurance

**We win.**

---

## Design Principles

### 1. **1D Over 2D**

Maps are 2D data. Hard to load, hard to parse, high cognitive load.

We solve for **stop-to-stop** navigation:
- User is at a stop → "When is bus coming?"
- User is on a bus → "Where am I on this route?"

This is a **1D problem**. A timeline. A rail. A pulse.

**There are two distinct 1D views:**

| View | Orientation | Where Used | Purpose |
|------|-------------|------------|---------|
| **Pulse** | Horizontal | Stop Detail page | Shows bus approaching THIS stop |
| **Rail** | Vertical | Bus Timeline page | Shows route with all stops |

**Pulse View** (Stop Detail — "buses coming to me"):
```
━━━━●━━━━━━━━━━●
    🚌 2 min    YOU (at stop)
```
- Horizontal line
- Bus dot moves RIGHT as it approaches
- You're always on the right (the destination)

**Rail View** (Bus Timeline — "where am I on the route"):
```
● Andheri ← bus here
│
○ Jogeshwari
│
★ Malad ← your stop
│
○ Borivali
```
- Vertical list
- Scrollable
- Shows full journey

### 2. **Glanceable in 0.5 Seconds**

The Pulse view (on Stop Detail page) is the primary "glance" surface.

- **Shape = Information**: Dots on a line. Gap = time remaining.
- **Color = Confidence**: Bright = verified. Dim = scheduled estimate.
- **Animation = Aliveness**: Subtle pulses = data is fresh.

The Pulse is what you see when you open a stop. Zero reading required.

### 3. **Dark Mode Default**

Most commutes happen in early morning or evening. Most transit apps blast harsh whites.

- **Background**: Deep blacks (#0a0a0a to #1a1a1a)
- **Accent**: Warm amber/gold (#f59e0b) — sunrise/sunset vibes
- **Secondary**: Cool grays for inactive elements
- **No pure white text**: Use #e5e5e5 or similar

The message: *"This is a premium lifestyle app that happens to do transit."*

### 4. **Zero Friction Data Capture** (Phase 2)

> **Deferred for MVP.** First we deliver static GTFS data beautifully. Then we layer in crowdsourced verification.

The bulk of useful data comes from regular commuters — people who know the route but can still verify it.

Make "claiming a bus" effortless:
- Detect user at stop (geolocation)
- Detect user moving (accelerometer)  
- Single tap or shake to confirm: *"On the 9:15 Route 502?"*

**We're not asking them to use the app. We're asking them to nod.**

### 5. **FOMO by Design**

We want users to attract users. The app should be **visually remarkable** enough that someone next to you thinks: "What's that? I want it."

- Premium dark aesthetic stands out in a sea of bright apps
- (Phase 2) "Claimed" buses show **live presence** of other users
- (Phase 2) Visible social proof: "2 people on this bus" with subtle glow

---

## PWA Architecture

### Why PWA Over Native

| Aspect | Native App | PWA |
|--------|------------|-----|
| Development cost | 2-3x | 1x |
| Distribution | App Store approval | Instant deploy |
| Install friction | Download → Install | Just visit URL |
| Geolocation | ✅ | ✅ |
| Offline | ✅ | ✅ (Service Workers) |
| Home screen | ✅ | ✅ (Add to Home Screen) |
| Background location | ✅ | ❌ |

**For MVP, PWA handles 100% of our use cases.**

The only native-only feature we lose is background location tracking. But:
- Foreground tracking works fine for "open app → confirm bus"
- This is sufficient to validate the UX hypothesis

### Data Strategy: Cache vs Real-time

Different data has different freshness requirements:

| Data Type | Freshness | Caching Strategy |
|-----------|-----------|------------------|
| **Stop list** | Static | Cache indefinitely (Service Worker) |
| **Route shapes** | Static | Cache indefinitely |
| **Scheduled times** | Static | Cache for 24h |
| **Upcoming trips** | Semi-dynamic | Fetch on page load, show loading shimmer |
| **Bus position** (Phase 2) | Real-time | WebSocket or poll every 30s |

**For MVP (Schedule-only):**
- Static GTFS data cached aggressively
- "Upcoming trips" endpoint fetched fresh on each Stop Detail load
- No real-time updates needed yet — schedule is schedule

**UX approach:**
- Show cached data instantly on load (feels fast)
- Fetch fresh data in background
- If data changes, update UI smoothly (no jarring refresh)
- Pull-to-refresh as manual override

**Granularity of time display:**
- We show **minutes** not seconds: "2 min", "8 min", "15 min"
- Under 1 min: "Arriving" or "< 1 min"
- Updates: client-side countdown based on scheduled time (no need to poll just for clock)

### PWA Optimizations

1. **Service Worker**: Cache static assets + GTFS data for instant re-load
2. **Manifest**: Proper icons, theme color, standalone display mode
3. **Preconnect**: Hint browser to establish early connections to API
4. **Minimal Bundle**: No heavy libraries. Vanilla CSS. Lean React.

---

## Core User Flows

### Flow 1: Stop Discovery (Home Page)

**User Story**: "I'm at a bus stop. What buses come here?"

```
┌─────────────────────────────┐
│  📍 Stops Near You          │
├─────────────────────────────┤
│  ● Andheri Station (50m)    │
│    Route 502, 203, 115      │
│                             │
│  ● Jogeshwari East (200m)   │
│    Route 502, 341           │
│                             │
│  ○ Search stops...          │
└─────────────────────────────┘
```

**Design Notes**:
- Auto-detect location on load (with permission prompt)
- Distance shown is **straight-line** (Haversine formula) — NOT walking path
- Format: `50m`, `200m`, `1.2km` — no "min walk" claims (we don't know the path)
- Show which routes serve each stop as preview
- Tap to enter Stop Detail

### Flow 2: Stop Detail (Buses Coming Here)

**User Story**: "When is the next bus to this stop?"

```
┌─────────────────────────────┐
│  ← Andheri Station          │
├─────────────────────────────┤
│                             │
│  Route 502 → Borivali       │
│  ━━━━━━━━━━━●━━━●           │
│            🚌    ▼           │
│            2 min            │
│                             │
├─────────────────────────────┤
│  Route 203 → Malad          │
│  ━━━━━━●━━━━━━━━━●           │
│       🚌         ▼           │
│       8 min                 │
│                             │
└─────────────────────────────┘
```

**The Timeline Problem**: Different buses travel different distances, so a proportional timeline would be confusing (one bus might be 2km away, another 500m away, but both "5 min").

**Solution — Time-based, not distance-based:**
- The pulse timeline represents **TIME to arrival**, not distance
- All timelines are normalized: right edge = NOW (when you're at the stop)
- Bus dot position = proportional to minutes remaining
- This keeps it simple and comparable across different routes

**Example logic:**
```
Timeline width = fixed (say 100%)
Bus at 2 min → dot at ~10% from right
Bus at 8 min → dot at ~40% from right
```

**Why this works:** User cares about "when" not "where from" — time is the universal unit.

**Design Notes**:
- Route name + direction shown (e.g., "502 → Borivali")
- Big "2 min" number is the hero — glanceable
- Tap the card to open full Bus Timeline (Rail view)
- Keep it fast: no fancy animations on load, just smooth

### Flow 3: Bus Timeline / Rail View

**User Story**: "I'm on the bus. How many stops until mine?"

```
┌─────────────────────────────┐
│  ← Route 502 → Borivali     │
│  🚌 3 stops away            │
├─────────────────────────────┤
│                             │
│  ● Andheri Station    09:15 │
│  │ ← Bus is here            │
│  │                          │
│  ○ Jogeshwari         09:22 │
│  │                          │
│  ○ Goregaon           09:28 │
│  │                          │
│  ★ Malad              09:35 │
│  │   ← Your stop            │
│  │                          │
│  ○ Kandivali          09:42 │
│  │                          │
│  ○ Borivali           09:50 │
│                             │
└─────────────────────────────┘
```

**Design Notes**:
- Vertical 1D timeline (inspired by Mumbai's train indicators)
- **Scheduled times shown next to each stop** (e.g., 09:15, 09:22)
- ETA to your stop in header: "3 stops away" or "~20 min"
- Bus position based on schedule (MVP) or real-time (Phase 2)
- User's stop highlighted with star icon
- Passed stops fade to gray
- Auto-scroll to current bus position on load
- (Phase 2) "Claim" button at bottom

---

## Visual Language

### Color Palette

```css
/* Core */
--bg-primary: #0a0a0a;      /* Deep black */
--bg-secondary: #141414;    /* Card background */
--bg-tertiary: #1f1f1f;     /* Elevated surfaces */

/* Accent */
--accent-primary: #f59e0b;  /* Amber - verified, active */
--accent-secondary: #fbbf24;/* Light amber - hover */
--accent-glow: rgba(245, 158, 11, 0.3); /* Glow effect */

/* Text */
--text-primary: #e5e5e5;    /* Main text */
--text-secondary: #a3a3a3;  /* Muted text */
--text-tertiary: #525252;   /* Very muted / disabled */

/* Semantic */
--color-verified: #22c55e;  /* Green - high confidence */
--color-scheduled: #6b7280; /* Gray - schedule only */
--color-user: #3b82f6;      /* Blue - user's position */
```

### Typography

```css
/* Font Stack — Apple-inspired for premium feel */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;

/* Scale */
--text-xs: 0.75rem;   /* 12px - timestamps */
--text-sm: 0.875rem;  /* 14px - secondary info */
--text-base: 1rem;    /* 16px - body */
--text-lg: 1.125rem;  /* 18px - card titles */
--text-xl: 1.25rem;   /* 20px - page headers */
--text-2xl: 1.5rem;   /* 24px - hero numbers (e.g., "2 min") */
```

### Animation

All animations are CSS-only. Keep them **fast and subtle**:

```css
/* Pulse for bus dot - subtle, not distracting */
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.85; transform: scale(1.03); }
}

/* Apply on schedule-based data (every 2s, gentle) */
.bus-dot--scheduled { animation: pulse 2s ease-in-out infinite; }

/* Transition defaults — fast is premium */
--transition-fast: 100ms ease;
--transition-base: 150ms ease;
--transition-slow: 200ms ease;
```

**Update granularity:**
- Display: **minutes** (not seconds)
- Client-side countdown: Update displayed "X min" every 60 seconds
- No need to poll server just for time countdown — scheduled times are fixed
- (Phase 2) Real-time bus position: poll every 30s or use WebSocket

---

## Component Architecture (MVP — Static Schedule Focus)

```
src/
├── components/
│   ├── common/
│   │   ├── Pulse.jsx             # The animated bus dot
│   │   ├── Timeline.jsx          # 1D horizontal timeline (for Stop Detail)
│   │   └── Rail.jsx              # 1D vertical timeline (for Bus Timeline)
│   │
│   ├── stops/
│   │   ├── StopList.jsx          # Nearby stops list
│   │   └── StopCard.jsx          # Individual stop preview
│   │
│   └── bus/
│       └── BusCard.jsx           # Single bus arrival info (route, time, pulse)
│
├── hooks/
│   ├── useGeolocation.js         # Browser geolocation wrapper
│   ├── useNearbyStops.js         # Fetch nearby stops
│   └── useUpcomingTrips.js       # Fetch buses for a stop
│
├── pages/
│   ├── Home.jsx                  # Stop discovery (default)
│   ├── Stop.jsx                  # Stop detail with upcoming buses
│   └── Trip.jsx                  # Bus timeline (rail view)
│
├── styles/
│   ├── tokens.css                # CSS custom properties
│   └── global.css                # Global styles + reset
│
└── utils/
    ├── api.js                    # API client
    ├── geo.js                    # Haversine distance helper
    └── time.js                   # Time formatting (relative, countdown)
```

**Note:** ClaimButton and real-time features deferred to Phase 2. MVP is pure scheduled data, displayed beautifully.

---

## Performance Budget

| Metric | Target | Why |
|--------|--------|-----|
| First Contentful Paint | < 1.0s | Win attention in first 3 seconds |
| Time to Interactive | < 2.0s | Must feel instant |
| Bundle Size (gzipped) | < 40KB | Aggressive — no bloat |
| Lighthouse Performance | > 95 | Prove we're serious |

### How We Hit This

1. **No heavy dependencies**: React only. No state library (useState sufficient for MVP)
2. **CSS-only animations**: No Framer Motion, no JS animation libs
3. **Lazy load routes**: Code split per page with React.lazy
4. **Inline critical CSS**: Above-the-fold styles load instantly
5. **Preload font**: Load Inter from Google Fonts with preconnect

---

## Accessibility

- **Minimum tap target**: 44x44px
- **Color contrast**: WCAG AA minimum (4.5:1 for text)
- **Motion**: Respect `prefers-reduced-motion` — disable pulse animation
- **Screen reader**: Semantic HTML + ARIA labels for bus arrival times
- **Focus states**: Visible focus rings on all interactive elements

---

## MVP Scope

**Phase 1 (Now):** Static Schedule, Beautiful UX
- Home: Nearby stops (geolocation + Haversine)
- Stop Detail: Upcoming buses with pulse visualization
- Bus Timeline: Full route with scheduled times
- All data from GTFS schedule
- Cached aggressively, pull-to-refresh

**Phase 2 (Later):** Crowdsourced Real-time
- "Claim this bus" button
- Real-time bus positions from user claims
- Verified vs scheduled visual distinction
- Social proof ("2 people on this bus")

**Phase 3 (Future):**
- Home Screen Widget
- Push Notifications
- Ghost Mode (learn patterns)
- Background tracking (native wrapper)

---

## Summary

| Dimension | Our Approach |
|-----------|--------------|
| **Mental Model** | 1D timeline (Pulse + Rail), not 2D map |
| **Emotion** | Calm reassurance, not information dump |
| **Aesthetic** | Dark, premium, Apple-inspired |
| **Interaction** | Passive glancing, not active planning |
| **Data (MVP)** | Schedule-only, cached, fast |
| **Data (Phase 2)** | Crowdsourced verification layer |
| **Distribution** | PWA → URL shareable → viral potential |
