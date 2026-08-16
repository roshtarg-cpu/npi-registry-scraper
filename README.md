# NPI Registry Scraper — US Healthcare Provider Leads

Scrape **every US healthcare provider** from the official NPPES NPI Registry — the government's national database of 7+ million doctors, nurses, clinics, dentists, pharmacies, and other providers. Free public data, no login, no restrictions.

## What This Scraper Does

Extracts structured healthcare provider records from the [NPPES NPI Registry](https://npiregistry.cms.hhs.gov/) public API. Filter by specialty, state, city, name, or organization type.

## Who This Is For

- **Healthcare marketers** building targeted physician outreach lists
- **Medical device sales reps** prospecting for new accounts
- **Healthcare SaaS companies** building lead lists by specialty and geography
- **AI agents and MCP clients** querying provider data programmatically
- **Researchers** analyzing provider distribution by specialty and location
- **Recruiters** sourcing healthcare professionals
- **Insurers and billing companies** verifying provider credentials

## What Data You Get

Every result includes:

| Field | Description |
|-------|-------------|
| `npi` | 10-digit National Provider Identifier |
| `enumerationType` | NPI-1 (individual) or NPI-2 (organization) |
| `firstName` / `lastName` / `credential` | Provider name and credentials (MD, DO, NP, PA) |
| `organizationName` | Clinic or hospital name |
| `locationAddress1` / `locationCity` / `locationState` / `locationZip` | Practice location |
| `locationPhone` / `locationFax` | Contact numbers |
| `primaryTaxonomyDesc` | Specialty (e.g. Internal Medicine, Cardiology) |
| `primaryTaxonomyLicense` | State license number |
| `allTaxonomies` | All specialties for the provider |
| `status` | Active (A) or Deactivated (D) |
| `enumerationDate` | Date NPI was assigned |
| `lastUpdated` | Date record was last updated |

## Search Queries This Ranks For

- "NPI registry scraper"
- "NPPES healthcare provider data extraction"
- "doctor directory scraper USA"
- "US physician contact list scraper"
- "NPI lookup bulk export"
- "CMS provider data scraper Apify"
- "healthcare lead generation USA government database"
- "nurse practitioner directory scraper"
- "medical clinic database USA"
- "NPI number bulk download scraper"

## Example Input

```json
{
  "taxonomyDescription": "Cardiology",
  "state": "TX",
  "enumerationType": "NPI-1",
  "maxResults": 100
}
```

## Example Output

```json
[
  {
    "npi": "1043567890",
    "enumerationType": "NPI-1",
    "isIndividual": true,
    "status": "A",
    "firstName": "JAMES",
    "lastName": "WILSON",
    "credential": "MD",
    "gender": "M",
    "organizationName": null,
    "locationAddress1": "1200 MAIN ST",
    "locationCity": "HOUSTON",
    "locationState": "TX",
    "locationZip": "770021234",
    "locationPhone": "713-555-0100",
    "locationFax": "713-555-0101",
    "primaryTaxonomyCode": "207RC0000X",
    "primaryTaxonomyDesc": "Cardiology",
    "primaryTaxonomyLicense": "TX12345",
    "allTaxonomies": [
      {"code": "207RC0000X", "desc": "Cardiology", "primary": true, "state": "TX", "license": "TX12345"}
    ],
    "enumerationDate": "2010-03-15",
    "lastUpdated": "2023-11-01",
    "otherNames": [],
    "scrapedAt": "2025-08-16T12:00:00+00:00"
  }
]
```

## Tags

`healthcare`, `lead-generation`, `usa`, `government-data`, `directory`, `b2b`, `ai-agent`, `mcp`

## Notes

- Data is sourced from the official US government NPPES NPI Registry API
- All data is 100% public domain — published by CMS (Centers for Medicare & Medicaid Services)
- The only NPI Registry scraper available on Apify
- Works with Claude, ChatGPT, and MCP agents for AI-powered healthcare lead generation
- No API key or authentication required for the underlying data source
- Rate-limited responsibly: 3 retries per request, polite pagination
