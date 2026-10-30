# Estate NLP Extraction Schema

Version: 0.1
Status: Draft

## 1. Purpose

Define a common structured output contract for the
Persian real-estate NLP engine.

The schema must support:
- Real-estate listings
- Customer property requirements
- Natural-language conversations
- Offline CRM integration
- Future dataset annotation and model training

## 2. Core Principles

1. Preserve ambiguity instead of guessing.
2. Keep raw evidence separate from normalized values.
3. Missing information must not be interpreted as false.
4. Preserve multiple financial mentions with their semantic roles.
5. Keep source dataset labels available for traceability.
6. Never silently convert unknown currency units.
7. Extracted information represents text claims, not verified facts.

## 3. Document Types

- listing
- customer_requirement
- conversation
- unknown

## 4. Transaction Types

- sale
- rent
- temporary_rent
- presale
- partnership
- service
- unknown

## 5. Property Types

- apartment
- house
- villa
- land
- shop
- office
- workspace
- industrial
- suite
- other
- unknown

Original dataset labels must be preserved separately.

## 6. Field Result Contract

Every extracted field should support:

- value
- status
- evidence
- confidence

Allowed statuses:

- extracted
- not_found
- ambiguous
- conflict

Confidence must remain null until a calibrated
scoring method is implemented and evaluated.

## 7. Property Attributes

### Areas

- building_area_sqm
- land_area_sqm

### Rooms

Preserve these semantic categories:

- no_room
- one
- two
- three
- four
- five_or_more
- unknown

### Building

- floor
- total_floors
- units_per_floor
- construction_year
- is_rebuilt
- deed_type
- building_direction
- floor_material

### Features

- parking
- elevator
- warehouse
- balcony
- pool
- jacuzzi
- sauna
- water
- electricity
- gas
- heating
- cooling
- restroom
- security_guard

Boolean attributes must support true, false and unknown.

## 8. Financial Mentions

Financial values must be stored as separate mentions.

Supported semantic roles:

- asking_price
- budget
- deposit
- monthly_rent
- daily_rent
- weekend_rent
- price_per_sqm
- cost_per_extra_person
- unknown

Each financial mention should preserve:

- raw_value
- normalized_value
- currency
- period
- evidence
- semantic_role

Currency values:

- toman
- rial
- unspecified

No silent currency conversion is permitted.

## 9. Location

- city
- neighborhood

Original location slugs must remain accessible.

## 10. Rental Conditions

Include:

- allow_single_person

This field corresponds to the source dataset field
rent_to_single.

Unknown must remain distinct from false.

## 11. Evidence and Ambiguity

Each extracted value should preserve its supporting
text evidence.

Multiple candidate values must be retained when
the text does not support a unique interpretation.

Evidence offsets can be introduced after the
normalizer establishes a stable offset mapping.

## 12. Provenance

Keep the following metadata when available:

- source
- source_style
- source_row
- original dataset labels

## 13. Implementation Status

This document is a proposed contract.

No final JSON schema has been approved yet.
No extraction code has been implemented.

The next implementation stage will introduce
machine-readable schema validation and tests.