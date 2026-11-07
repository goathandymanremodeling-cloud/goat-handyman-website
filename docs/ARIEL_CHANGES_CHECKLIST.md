# GOAT Handyman - Ariel Changes Checklist

Quick reference for tracking implementation. See `ARIEL_FEEDBACK_CHANGES.md` for full details.

**Last Updated:** 2026-11-02
**Status:** Implementation Complete (Google reviews pending client access)

---

## Phase 1: Critical Fixes - COMPLETE

- [x] **1.1** Remove "Green Empire Difference" → "The GOAT Difference" (`about/index.html`)
- [x] **1.2** Search/replace all "Green Empire" references
- [x] **1.3** Remove "licensed" claims (keep "insured" only)
  - [x] `about/index.html`
  - [x] FAQ answers
  - [x] Homepage badges
  - [x] Footer
  - [x] All service pages
  - [x] All location pages
- [x] **1.4** Remove permit coordination section
- [x] **1.5** Fix hours: Mon-Sat, 8am-6pm everywhere
  - [x] `site.config.json`
  - [x] `generate.py`

## Phase 2: Content Updates - COMPLETE

- [x] **2.1** Rewrite About page with Ariel's copy
- [x] **2.2** Update tagline: "Nassau & Suffolk Counties"
- [x] **2.3** Add "Handyman Services" page
- [x] **2.4** Add "Home Repair Services" page
- [x] **2.5** Add 26 service-specific FAQs (2 per service)
- [x] **2.6** Replace 4 main FAQ questions with 6 new ones

## Phase 3: Location Updates - COMPLETE

- [x] **3.1** Update `site.config.json` with 23 correct towns:
  - Garden City, Westbury, Roslyn, Mineola, Sands Point, Plandome, Old Westbury, Brookville, Old Brookville, Plandome Manor, Manhasset, Lake Success, East Hills, Kings Point, Flower Hill, Jericho, Syosset, Port Washington, Plainview, Rockville Centre, Merrick, Wantagh, East Meadow
- [x] **3.2** Removed old location directories (15 removed)
- [x] **3.3** Run `python generate.py`
- [x] **3.4** Location pages use consistent messaging

## Phase 4: Media & Reviews - COMPLETE

- [x] **4.1** Fix duplicate photos (replaced with unique stock photos)
- [x] **4.2** Fix mismatched photos (updated carpentry, kitchen, plumbing, handyman, home-repair)
- [ ] **4.3** Get real Google reviews (PENDING: Need access to GBP or manual copy)
- [x] **4.4** Fix review location inconsistencies (updated locations used)
- [x] **4.5** Replace About page team graphic (used Ariel's photo from Drive)

## Phase 4c: Service Page Copy Updates - COMPLETE (2026-11-02)

- [x] **4.12** Updated all 13 service pages with Ariel's new opening paragraphs
- [x] **4.13** Updated all 13 service pages with new "What's Included" bullet lists
- [x] **4.14** Added Levittown to service areas (25 locations total)
- [x] **4.15** Added Lynbrook to service areas (25 locations total)
- [x] **4.16** Regenerated site (52 pages total)

## Phase 4b: Photo Galleries - COMPLETE (2026-10-31)

- [x] **4.6** Download all photos from Google Drive (24 photos total)
- [x] **4.7** Optimize photos for web (30MB → 4.3MB, 85% reduction)
- [x] **4.8** Add photo galleries to 8 service pages with actual `<img>` elements
- [x] **4.9** Implement lazy loading (`loading="lazy"`)
- [x] **4.10** Add responsive image sizing (`width`/`height` attributes)
- [x] **4.11** Update service hero images with Ariel's photos

## Phase 5: Forms & Contact - COMPLETE

- [x] **5.1** Update phone number: (516) 447-4976
- [x] **5.2** Change form field: ZIP → City
- [x] **5.3** Remove "full home additions" / "custom builds" messaging
- [x] **5.4** Phone number updated across all 50 pages

## Phase 6: Polish - COMPLETE

- [x] **6.1** Improve dark section contrast (homepage stats)
- [x] **6.2** Premium styling enhancements (Green Empire reference)
- [x] **6.3** Enhanced service cards with gold gradient accents
- [x] **6.4** Improved stats bar with gradient text
- [x] **6.5** Premium button styling with shadows
- [x] **6.6** Enhanced contact card effects
- [ ] **6.7** Final QA pass (manual)

---

## Remaining Items

| Item | Status | Notes |
|------|--------|-------|
| Google reviews | PENDING | Can't scrape from GBP - need manual copy or access |
| DNS setup | PENDING | Ready when Ariel provides access or updates DNS |

---

## Summary of Changes Made

### Files Modified:
- `site.config.json` - Complete rewrite with new content
- `generate.py` - Template updates for all pages
- `css/main.css` - Contrast improvements
- `css/builders-design.css` - New About page styles

### Content Changes:
1. **Tagline:** "Nassau County's Trusted..." → "Nassau & Suffolk Counties' Trusted..."
2. **Hours:** Sun-Fri 8am-6pm → Mon-Sat 8am-6pm
3. **Licensing:** "Licensed & Insured" → "Insured"
4. **Services:** Added 2 new services (13 total)
5. **Locations:** Updated to 23 priority towns (was different set)
6. **FAQs:** 6 new general FAQs + 26 service-specific FAQs
7. **About Page:** Complete rewrite with Ariel's copy
8. **Form Field:** ZIP Code → City

### Removed:
- "Permit Coordination" section and all permit claims
- "Licensed" claims throughout
- "Full home additions" and "custom builds" messaging
- "Green Empire" references
- 15 old location page directories

---

## Quick Commands

```bash
# Regenerate site after any config changes
cd /var/www/zaylegend/apps/staging/goat-handyman-static
python3 generate.py

# Search for any remaining issues
grep -ri "licensed" . --include="*.html" | grep -v ".md"
grep -ri "permit" . --include="*.html" | grep -v ".md"
grep -ri "green empire" . --include="*.html" --include="*.py" | grep -v ".md"
```

---

**Progress:** 44 / 45 items complete (Google reviews pending client access)
