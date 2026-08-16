"""
NPI Registry Scraper — src/main.py
Scrapes US healthcare provider data from the NPPES NPI Registry public API.
No API key required. Government data, no bot protection.
"""

import asyncio
import logging
from datetime import datetime, timezone

import httpx
from apify import Actor

logger = logging.getLogger(__name__)

NPI_API_BASE = "https://npiregistry.cms.hhs.gov/api/"
NPI_API_VERSION = "2.1"
MAX_PER_PAGE = 200  # API max per request
MAX_RETRIES = 3
RETRY_DELAY = 2.0


def _extract_address(addresses: list, purpose: str = "LOCATION") -> dict:
    """Extract a specific address type from the addresses list."""
    for addr in addresses or []:
        if addr.get("address_purpose") == purpose:
            return addr
    # fallback to first address
    return addresses[0] if addresses else {}


def _flatten_result(item: dict) -> dict:
    """Flatten an NPI API result into a clean, flat dictionary."""
    basic = item.get("basic", {})
    addresses = item.get("addresses", [])
    taxonomies = item.get("taxonomies", [])
    other_names = item.get("other_names", [])

    location = _extract_address(addresses, "LOCATION")
    mailing = _extract_address(addresses, "MAILING")

    # Primary taxonomy
    primary_taxonomy = None
    for t in taxonomies:
        if t.get("primary"):
            primary_taxonomy = t
            break
    if not primary_taxonomy and taxonomies:
        primary_taxonomy = taxonomies[0]

    # Determine provider type
    enum_type = item.get("enumeration_type", "")
    is_individual = enum_type == "NPI-1"

    record = {
        "npi": item.get("number", None),
        "enumerationType": enum_type,
        "isIndividual": is_individual,
        "status": basic.get("status", None),
        "enumerationDate": basic.get("enumeration_date", None),
        "lastUpdated": basic.get("last_updated", None),
    }

    if is_individual:
        record.update({
            "firstName": basic.get("first_name", None),
            "middleName": basic.get("middle_name", None),
            "lastName": basic.get("last_name", None),
            "namePrefix": basic.get("name_prefix", None),
            "nameSuffix": basic.get("name_suffix", None),
            "credential": basic.get("credential", None),
            "gender": basic.get("sex", None),
            "soleProprietor": basic.get("sole_proprietor", None),
            "organizationName": None,
        })
    else:
        record.update({
            "firstName": None,
            "middleName": None,
            "lastName": None,
            "namePrefix": None,
            "nameSuffix": None,
            "credential": None,
            "gender": None,
            "soleProprietor": None,
            "organizationName": basic.get("organization_name", None),
        })

    # Location address
    record.update({
        "locationAddress1": location.get("address_1", None),
        "locationAddress2": location.get("address_2", None),
        "locationCity": location.get("city", None),
        "locationState": location.get("state", None),
        "locationZip": location.get("postal_code", None),
        "locationCountry": location.get("country_code", None),
        "locationPhone": location.get("telephone_number", None),
        "locationFax": location.get("fax_number", None),
    })

    # Mailing address
    record.update({
        "mailingAddress1": mailing.get("address_1", None),
        "mailingCity": mailing.get("city", None),
        "mailingState": mailing.get("state", None),
        "mailingZip": mailing.get("postal_code", None),
    })

    # Primary taxonomy
    if primary_taxonomy:
        record.update({
            "primaryTaxonomyCode": primary_taxonomy.get("code", None),
            "primaryTaxonomyDesc": primary_taxonomy.get("desc", None),
            "primaryTaxonomyState": primary_taxonomy.get("state", None),
            "primaryTaxonomyLicense": primary_taxonomy.get("license", None),
        })
    else:
        record.update({
            "primaryTaxonomyCode": None,
            "primaryTaxonomyDesc": None,
            "primaryTaxonomyState": None,
            "primaryTaxonomyLicense": None,
        })

    # All taxonomies as list
    record["allTaxonomies"] = [
        {
            "code": t.get("code", None),
            "desc": t.get("desc", None),
            "primary": t.get("primary", False),
            "state": t.get("state", None),
            "license": t.get("license", None),
        }
        for t in taxonomies
    ]

    # Other names / DBA
    record["otherNames"] = [n.get("organization_name", n.get("name", "")) for n in other_names]

    record["scrapedAt"] = datetime.now(timezone.utc).isoformat()

    return record


async def _fetch_page(
    client: httpx.AsyncClient,
    params: dict,
    skip: int,
    limit: int,
) -> dict | None:
    """Fetch one page from the NPI API with retries."""
    page_params = {**params, "skip": skip, "limit": limit, "version": NPI_API_VERSION}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = await client.get(NPI_API_BASE, params=page_params, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()
            if "Errors" in data:
                logger.warning("API returned errors at skip=%d: %s", skip, data["Errors"])
                return None
            return data
        except Exception as exc:
            logger.warning("Attempt %d/%d failed (skip=%d): %s", attempt, MAX_RETRIES, skip, exc)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY * attempt)
    return None


async def main() -> None:
    async with Actor:
        inp = await Actor.get_input() or {}

        # Input parameters
        taxonomy_desc = inp.get("taxonomyDescription", "")
        first_name = inp.get("firstName", "")
        last_name = inp.get("lastName", "")
        organization_name = inp.get("organizationName", "")
        state = inp.get("state", "")
        city = inp.get("city", "")
        postal_code = inp.get("postalCode", "")
        enumeration_type = inp.get("enumerationType", "")  # NPI-1, NPI-2, or ""
        max_results = int(inp.get("maxResults", 50))

        Actor.log.info(
            "Starting NPI Registry Scraper | taxonomy=%s state=%s maxResults=%d",
            taxonomy_desc, state, max_results,
        )

        # Build query params
        query_params: dict = {}
        if taxonomy_desc:
            query_params["taxonomy_description"] = taxonomy_desc
        if first_name:
            query_params["first_name"] = first_name
        if last_name:
            query_params["last_name"] = last_name
        if organization_name:
            query_params["organization_name"] = organization_name
        if state:
            query_params["state"] = state
        if city:
            query_params["city"] = city
        if postal_code:
            query_params["postal_code"] = postal_code
        if enumeration_type:
            query_params["enumeration_type"] = enumeration_type

        # Require at least one search criterion
        if not query_params:
            query_params["taxonomy_description"] = "Internal Medicine"
            Actor.log.warning("No search criteria provided, defaulting to taxonomy_description=Internal Medicine")

        collected = 0
        skip = 0
        page_size = min(MAX_PER_PAGE, max_results)

        async with httpx.AsyncClient() as client:
            while collected < max_results:
                fetch_limit = min(page_size, max_results - collected)
                Actor.log.info("Fetching skip=%d limit=%d (collected=%d/%d)", skip, fetch_limit, collected, max_results)

                data = await _fetch_page(client, query_params, skip, fetch_limit)

                if data is None:
                    Actor.log.error("Failed to fetch page at skip=%d after %d retries", skip, MAX_RETRIES)
                    break

                results = data.get("results", [])
                if not results:
                    Actor.log.info("No more results at skip=%d", skip)
                    break

                for item in results:
                    if collected >= max_results:
                        break
                    try:
                        flat = _flatten_result(item)
                        await Actor.push_data(flat)
                        collected += 1
                        if collected % 10 == 0:
                            Actor.log.info("Pushed %d results so far", collected)
                    except Exception as exc:
                        Actor.log.warning("Error flattening result NPI=%s: %s", item.get("number"), exc)

                skip += len(results)

                # If the API returned fewer than requested, we've hit the end
                if len(results) < fetch_limit:
                    Actor.log.info("Reached end of results (got %d, asked %d)", len(results), fetch_limit)
                    break

        Actor.log.info("Done. Total results pushed: %d", collected)
