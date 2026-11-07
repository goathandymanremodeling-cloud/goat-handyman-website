# GOAT Handyman Website - Ariel Feedback Changes

**Document Created:** 2026-10-20
**Client:** Ariel (GOAT Handyman & Remodeling)
**Preview URL:** https://zaylegend.com/goat-preview/
**Source Email:** Ariel feedback received October 2026

---

## Overview

This document tracks all changes requested by Ariel for the GOAT Handyman preview website. Changes are organized by priority and mapped to specific files in the codebase.

**Codebase Location:** `/var/www/zaylegend/apps/staging/goat-handyman-static/`

**Architecture:** Static site generated from:
- `site.config.json` - Master content configuration
- `generate.py` - Python static site generator
- Individual HTML files in subdirectories

---

## Change Summary

| # | Issue | Priority | Complexity |
|---|-------|----------|------------|
| 1 | Remove licensing claims | HIGH | Medium |
| 2 | Remove permit coordination section | HIGH | Low |
| 3 | Nassau + Suffolk coverage consistency | HIGH | Medium |
| 4 | Correct priority locations (23 towns) | HIGH | High |
| 5 | Update phone number (tracking #) | HIGH | Medium |
| 6 | Fix duplicate/mismatched photos | MEDIUM | Medium |
| 7 | Use real Google reviews | MEDIUM | Medium |
| 8 | Remove Green Empire reference | HIGH | Low |
| 9 | Adjust messaging (remove full builds) | MEDIUM | Medium |
| 10 | Check service list (13 services) | HIGH | High |
| 11 | Fix hours + add city to forms | MEDIUM | Low |
| 12 | Improve readability/contrast | LOW | Medium |
| 13 | Rewrite About Us section | HIGH | Medium |
| 14 | Add service-specific FAQs | HIGH | High |

---

## Detailed Change Specifications

### 1. Remove All Licensing Claims

**Priority:** HIGH
**Status:** ☐ Pending

**What to Remove:**
- "licensed" and "fully licensed" throughout entire website
- "Licensed & Insured" badge → Change to just "Insured"
- Workers' compensation or specific coverage claims

**Files to Check:**
- [ ] `index.html` - Homepage introduction
- [ ] `about/index.html` - About page (lines 112-116 checklist)
- [ ] `faq/index.html` - FAQ Q&A items
- [ ] `site.config.json` - FAQ answers, feature descriptions
- [ ] `generate.py` - Generated content templates
- [ ] All service pages in `services/*/index.html`
- [ ] All location pages in `service-areas/*/index.html`
- [ ] Footer sections (all pages)

**Replace With:**
- "Insured" (no specific coverage details unless confirmed)
- Remove any licensing badges/icons

**Current Problematic Text Found:**
```
about/index.html line 114: "Fully licensed and insured in New York State"
```

---

### 2. Remove Permit Coordination Section

**Priority:** HIGH
**Status:** ☐ Pending

**What to Remove:**
> "We handle all permits and municipal approvals – no surprises, no delays, work starts on time."

**Files to Check:**
- [ ] `index.html` - Homepage sections
- [ ] `services/*/index.html` - All service pages
- [ ] `site.config.json` - Service descriptions
- [ ] `about/index.html` - About page content

**Action:** Delete entire section/paragraph where this appears. Search for "permit" across all files.

---

### 3. Nassau and Suffolk Coverage Consistency

**Priority:** HIGH
**Status:** ☐ Pending

**Current Issue:**
- Homepage badge mentions both counties
- Main headline and introduction focus only on Nassau
- Service Areas page has Suffolk heading with nothing listed

**Required Changes:**
- [ ] Update homepage headline to mention both Nassau AND Suffolk
- [ ] Update homepage introduction paragraph
- [ ] Update all service page introductions
- [ ] Update About page coverage statements
- [ ] Update FAQs coverage answer
- [ ] Update footer service areas section
- [ ] Fix Service Areas page - add Suffolk content or restructure

**Files:**
- `index.html` - Homepage headline (line ~100)
- `site.config.json` - brand.tagline (currently "Nassau County's Trusted...")
- `about/index.html` - Coverage statements
- `faq/index.html` - "What areas do you serve?" answer
- `service-areas/index.html` - Directory page
- `generate.py` - Footer generation

**New Tagline Suggestion:**
```
"Nassau & Suffolk Counties' Trusted Handyman & Remodeling Experts"
```

**Important Note from Ariel:**
> "The specific towns we selected are the locations we want to focus on more heavily for marketing and SEO. They are not the only places we serve. Please make that distinction clear."

---

### 4. Correct Priority Locations

**Priority:** HIGH
**Status:** ☐ Pending

**Ariel's Priority Locations (23 towns):**
1. Garden City
2. Westbury
3. Roslyn
4. Mineola
5. Sands Point
6. Plandome
7. Old Westbury
8. Brookville
9. Old Brookville
10. Plandome Manor
11. Manhasset
12. Lake Success
13. East Hills
14. Kings Point
15. Flower Hill
16. Jericho
17. Syosset
18. Port Washington
19. Plainview
20. Rockville Centre
21. Merrick
22. Wantagh
23. East Meadow

**Current Locations (23 towns - MISMATCHED):**
Garden City, Levittown, Hempstead, Hicksville, Mineola, Westbury, Freeport, Massapequa, Valley Stream, Rockville Centre, East Meadow, Uniondale, Baldwin, Oceanside, Merrick, Bellmore, Wantagh, Seaford, Bethpage, Plainview, Elmont, Franklin Square, Lynbrook

**Location Comparison:**
| Keep | Remove | Add New |
|------|--------|---------|
| Garden City | Levittown | Roslyn |
| Mineola | Hempstead | Sands Point |
| Westbury | Hicksville | Plandome |
| Rockville Centre | Freeport | Old Westbury |
| East Meadow | Massapequa | Brookville |
| Merrick | Valley Stream | Old Brookville |
| Wantagh | Uniondale | Plandome Manor |
| Plainview | Baldwin | Manhasset |
| | Oceanside | Lake Success |
| | Bellmore | East Hills |
| | Seaford | Kings Point |
| | Bethpage | Flower Hill |
| | Elmont | Jericho |
| | Franklin Square | Syosset |
| | Lynbrook | Port Washington |

**Files to Update:**
- [ ] `site.config.json` - serviceAreas array (lines 219-282)
- [ ] Run `python generate.py` to regenerate all pages
- [ ] Delete old location page directories
- [ ] Create new location page directories

**SEO Consideration (from Ariel):**
> "If there are existing pages for other towns that have SEO value, please flag them before removing anything. We should preserve useful pages or redirect them properly."

**Action Items:**
1. Check if any removed towns have backlinks or rankings
2. Set up 301 redirects for removed pages → main service areas page
3. Update site.config.json with correct 23 towns
4. Regenerate site

**Service Page Location Display:**
> "On individual service pages, please use a shorter selection of relevant towns and link to the full Service Areas page instead of repeating all 23 locations every time."

---

### 5. Update Phone Number

**Priority:** HIGH
**Status:** ☐ Pending - WAITING FOR TRACKING NUMBER

**Current Number:** (516) 903-3012
**New Number:** TBD (Ariel will send tracking number)

**Locations to Update:**
1. `site.config.json` - brand.phone and brand.phoneRaw
2. `index.html` - Hero CTA button, nav, footer
3. `about/index.html` - CTA section
4. `faq/index.html` - Inline CTA
5. `request-service.html` - Form data attribute, CTA text
6. `js/main.js` - Error fallback message (line ~95)
7. All generated service pages
8. All generated location pages

**After Config Update:**
Run `python generate.py` to propagate changes to all pages.

**Testing Required:**
- [ ] Verify calls reach correct number
- [ ] Verify tracking is working
- [ ] Test on mobile (tap-to-call)

---

### 6. Fix Duplicate and Mismatched Photos

**Priority:** MEDIUM
**Status:** ☐ Pending

**Duplicate Photos Identified:**
| Service | Current Photo | Issue |
|---------|--------------|-------|
| Kitchen Remodeling | kitchen-remodeling.jpg | Duplicated |
| Carpentry Services | kitchen-remodeling.jpg | Same kitchen photo |
| Bathroom Remodeling | bathroom-remodeling.jpg | Duplicated |
| Light Plumbing & Electrical | bathroom-remodeling.jpg | Same bathroom photo |

**Mismatched Photos:**
| Service | Current Photo | Issue | Suggested |
|---------|--------------|-------|-----------|
| Drywall Repair | Shows bookshelves/cabinetry | Not drywall work | Drywall patching/taping |
| Deck Repair | Shows pergola/patio cover | Not deck work | Actual deck boards/framing |
| Window Repair | Shows sliding patio door | Not window | Standard window installation |
| Carpentry | Kitchen photo | Not carpentry | Trim, molding, built-ins |

**About Page:**
> "The About page would also benefit from an actual team or project photo instead of the large 'GOAT HANDYMAN – Family-Owned & Operated' graphic."

**Files:**
- `images/services/*.jpg` - Service photos
- `images/team.png` - About page team photo
- `site.config.json` - Image path references

**Action:** Request approved numbered photos from Ariel or source appropriate stock images.

---

### 7. Use Real Google Reviews

**Priority:** MEDIUM
**Status:** ☐ Pending

**Current Issue:**
- 28 real Google reviews exist but not being used
- Fake/inconsistent testimonials with wrong locations
- Location changes between pages

**Inconsistencies Found:**
- Robert K. → "Levittown" on Reviews page, "Garden City" on Garden City page
- Jennifer L. → "Hicksville" on Reviews page, "Garden City" on Garden City page
- Westbury page → All 3 reviewers labeled "Westbury"

**Required Changes:**
- [ ] Pull actual reviews from Google Business Profile
- [ ] Use real names and locations
- [ ] Link back to Google Business Profile
- [ ] Keep locations consistent across all pages

**Files:**
- `site.config.json` - testimonials array
- `reviews/index.html` - Reviews page
- `service-areas/*/index.html` - Location-specific testimonials
- `generate.py` - Testimonial generation logic

---

### 8. Remove Green Empire Reference

**Priority:** HIGH
**Status:** ☐ Pending

**Found:**
```
about/index.html line 126: "The Green Empire Difference"
```

**Change To:**
"The GOAT Difference" or "Why Choose GOAT"

**Action:** Search entire codebase for "Green Empire" and replace/remove all instances.

```bash
grep -r "Green Empire" /var/www/zaylegend/apps/staging/goat-handyman-static/
```

---

### 9. Adjust Messaging - Remove Full Builds

**Priority:** MEDIUM
**Status:** ☐ Pending

**What to Remove:**
- "full home additions and custom builds"
- "all phases of construction"
- Any claims suggesting full construction services

**Found On:**
- Location pages
- Estimate page

**Focus Instead On:**
- Home repairs
- Painting
- Carpentry
- Room updates
- Remodeling services

**Files to Check:**
- [ ] `request-service.html` - Estimate page
- [ ] `service-areas/*/index.html` - All location pages
- [ ] `site.config.json` - Service descriptions
- [ ] `index.html` - Homepage content

---

### 10. Verify and Update Service List

**Priority:** HIGH
**Status:** ☐ Pending

**Ariel's Required Services (13):**
1. Handyman Services ← NEW
2. Home Repair Services ← NEW
3. Drywall Repair & Installation ✓
4. Carpentry Services ✓
5. Door Repair & Installation ✓
6. Window Repair & Installation ✓
7. Flooring Repair & Installation ✓
8. Deck Repair & Installation ✓
9. Bathroom Remodeling ✓
10. Kitchen Remodeling ✓
11. Siding Repair & Installation ✓
12. Insulation Services ✓
13. Light Plumbing & Electrical Services ✓

**Current Services (11):**
Missing: Handyman Services, Home Repair Services

**Each Service Page Must Include:**
- [ ] What work we actually handle
- [ ] Common customer problems
- [ ] Our process
- [ ] Relevant project examples
- [ ] 4-8 service-specific FAQs
- [ ] Avoid generic paragraph with only service name changed

**Files:**
- `site.config.json` - services array
- `services/*/index.html` - Individual service pages
- `generate.py` - Service page generation

---

### 11. Fix Hours and Form Fields

**Priority:** MEDIUM
**Status:** ☐ Pending

**Hours Inconsistency:**
| Location | Current | Correct |
|----------|---------|---------|
| Estimate page | Mon-Sat, 7am-6pm | Mon-Sat, 8am-6pm |
| Service/location pages | Sun-Fri, 8am-6pm | Mon-Sat, 8am-6pm |

**Correct Hours:** Monday-Saturday, 8am-6pm

**Form Field Change:**
| Field | Current | Required |
|-------|---------|----------|
| Location | ZIP code | City name |

**Why:** Identify customer location while keeping forms simple.

**Files:**
- `site.config.json` - brand.hours
- `request-service.html` - Form fields
- `index.html` - Sidebar form
- `generate.py` - Form generation
- `js/main.js` - Form validation

---

### 12. Improve Readability and Add Project Examples

**Priority:** LOW
**Status:** ☐ Pending

**Readability Issues:**
- Homepage statistics in dark sections - difficult to read
- Need better contrast
- Check on both desktop and mobile

**Duplicate Content:**
- Garden City and Westbury pages use almost identical text
- Only the town name is changed

**Action:**
- [ ] Improve text contrast in dark sections
- [ ] Add genuine local project examples where available
- [ ] Create unique content for location pages

**Files:**
- `css/main.css` - Contrast/colors
- `css/theme.css` - Theme variables
- `service-areas/*/index.html` - Location pages

---

### 13. Rewrite About Us Section

**Priority:** HIGH
**Status:** ☐ Pending

**New Content Provided by Ariel:**

See full copy in section below. Key points:
- New headline structure
- Focus on combined projects, not single tasks
- Clear service categories
- Our approach explanation
- Workmanship warranty mention
- CTA at bottom

**Files:**
- `about/index.html` - Complete rewrite
- `images/` - New team/project photo needed

**Full About Page Copy:**

---

#### About GOAT Handyman & Remodeling
*Home repairs, room updates, and remodeling across Nassau and Suffolk Counties.*

**For the Projects That Have Been Waiting to Get Done**

Sometimes a home needs more than one repair. The ceiling needs patching and painting. A door and its frame need replacing. The trim needs attention, and the flooring is ready for an update. Other times, it's a kitchen or bathroom that no longer works the way you want it to.

GOAT Handyman & Remodeling helps Long Island homeowners bring those projects together.

GOAT is a locally owned, insured handyman and home improvement company serving Nassau and Suffolk Counties. Our focus is on practical repairs and remodeling that improve how your home looks, functions, and feels.

**A Handyman Company That Can Take On the Bigger Picture**

Many homeowners hear "handyman" and think of a single small task. Our work also includes projects that require several types of repair, installation, and finishing.

That might mean repairing a water-damaged ceiling after the leak has been resolved, then preparing and painting the surface. It could involve replacing doors, repairing the surrounding drywall, and installing new trim. Or it might be updating several rooms as part of one home improvement project.

These connected projects are an important part of what GOAT does. We help homeowners think through the full scope, including the finishing work that can be easy to overlook at the beginning.

**The Work We Handle**

Our services cover interior and exterior home improvements:

- **Home repairs and interior finishing:** Handyman services, drywall repair and installation, painting, carpentry, trim, and molding.
- **Doors, windows, and flooring:** Repair and installation, including the surrounding finish work identified in the project scope.
- **Kitchen and bathroom remodeling:** Updates, repairs, and renovations based on the existing space and your goals.
- **Exterior improvements:** Deck repairs and installation, along with siding repairs and replacement.
- **Insulation:** Attic, wall, crawl-space, and basement insulation, including removal and replacement.

Our siding services include vinyl, wood, fiber cement, and aluminum. Our insulation services include fiberglass and spray foam. You can find the full scope of each service on its dedicated page.

**How We Approach Your Project**

We start with what you want to accomplish: fixing damage, updating a room, replacing worn materials, or taking care of several overdue repairs.

From there, the important questions are practical. What can be repaired? What needs replacement? Which materials will work with what is already there? What preparation and finishing should be included?

Our aim is to make those decisions clear before work begins. We want the project scope to account for the details—from drywall preparation and trim to caulking and paint—so the finished work makes sense as a whole.

GOAT provides a workmanship warranty on completed work.

**Let's Talk About Your Home**

Whether you have a list of repairs or a room you're ready to improve, tell us what you have in mind.

Send your ZIP code, a brief description, and any photos you have. We'll review your project and discuss the next step.

[Request an Estimate Button]

---

### 14. Service Page FAQs

**Priority:** HIGH
**Status:** ☐ Pending

**Requirements:**
- 2 service-specific Q&As per service page (13 services × 2 = 26 Q&As)
- 6 general Q&As for main FAQ page

**Files:**
- `site.config.json` - FAQ arrays per service
- `services/*/index.html` - Service pages
- `faq/index.html` - Main FAQ page
- `generate.py` - FAQ generation

#### Service-Specific FAQs (Provided by Ariel):

**1. Handyman Services**
- Q: What types of projects can a handyman company handle?
- Q: Can several home repairs be combined into one project?

**2. Home Repair Services**
- Q: Which home repairs should I address first?
- Q: Why does the same ceiling stain or damaged area keep coming back?

**3. Drywall Repair & Installation**
- Q: Can water-damaged drywall be repaired, or does it need to be replaced?
- Q: Will a drywall patch still be visible after painting?

**4. Carpentry Services**
- Q: Can damaged baseboards and trim be repaired instead of replaced?
- Q: Is PVC trim a good replacement for exterior wood trim?

**5. Door Repair & Installation**
- Q: Can I replace an interior door without replacing the frame?
- Q: Does a drafty exterior door need to be replaced?

**6. Window Repair & Installation**
- Q: Does condensation on a window mean the window needs replacement?
- Q: What is the difference between insert and full-frame window replacement?

**7. Flooring Repair & Installation**
- Q: Can damaged hardwood flooring be repaired without replacing the entire room?
- Q: Can luxury vinyl flooring be installed over an existing floor?

**8. Deck Repair & Installation**
- Q: How do I know whether my deck needs repairs or replacement?
- Q: Can wood deck boards be replaced with composite decking on the existing frame?

**9. Bathroom Remodeling**
- Q: Can I update my bathroom without moving the toilet, shower, or sink?
- Q: Will replacing grout or caulk fix a leaking shower?

**10. Kitchen Remodeling**
- Q: Can I update my kitchen without replacing all the cabinets?
- Q: What usually increases the cost of a kitchen remodel?

**11. Siding Repair & Installation**
- Q: Can damaged siding be repaired without replacing the entire exterior?
- Q: What should be checked before replacing damaged siding?

**12. Insulation Services**
- Q: Does old attic insulation have to be removed before adding new insulation?
- Q: What is the difference between attic insulation and air sealing?

**13. Light Plumbing & Electrical Services**
- Q: Does a dripping faucet need to be replaced, or can it be repaired?
- Q: Can a new light fixture use the existing wiring and electrical box?

#### Main FAQ Page - General Questions (6):

1. What affects the cost of a home repair or remodeling project on Long Island?
2. What should a written home improvement estimate include?
3. Why can two contractors give very different prices for the same project?
4. Should I buy materials before getting an estimate?
5. Can I stay in my home during a remodeling project?
6. What happens if hidden damage is found during a repair or remodel?

---

## Implementation Order

### Phase 1: Critical Fixes (Do First)
1. Remove Green Empire reference
2. Remove licensing claims
3. Remove permit coordination
4. Fix hours consistency

### Phase 2: Content Updates
5. Rewrite About Us section
6. Update Nassau + Suffolk coverage
7. Add 2 new service pages (Handyman, Home Repair)
8. Add all service-specific FAQs
9. Update main FAQ page

### Phase 3: Location Updates
10. Update priority locations (23 towns)
11. Set up redirects for removed locations
12. Make location content unique

### Phase 4: Media & Reviews
13. Fix duplicate/mismatched photos
14. Pull real Google reviews
15. Fix review location consistency

### Phase 5: Forms & Contact
16. Update phone number (when provided)
17. Change ZIP to City on forms
18. Remove full builds messaging

### Phase 6: Polish
19. Improve contrast/readability
20. Test on mobile
21. Final QA pass

---

## Waiting On Client

- [ ] **Tracking phone number** - Ariel will send
- [ ] **Approved numbered photos** - For service cards
- [ ] **Team/project photo** - For About page
- [ ] **Real Google reviews** - Need access or export

---

## Notes

- After any `site.config.json` changes, run `python generate.py` to regenerate all pages
- Consider SEO impact before removing existing location pages
- Test all forms after phone number update
- Mobile testing required after contrast changes

---

## Changelog

| Date | Changes |
|------|---------|
| 2026-10-20 | Document created from Ariel email feedback |

