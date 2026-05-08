# MOC - Business

> Map of Content for Business CRM data
> Generated: 2026-05-08 | 0 records, 0 active deals, 0 high priority

[[business/_index|Business Data Overview]]

---

## By Industry

---

## Dataview: Active Deals

```dataview
TABLE deal_status as "Status", deal_deadline as "Deadline", industry
FROM "business/crm"
WHERE deal_status != null AND deal_status != "StandBy" AND deal_status != "Отказано"
SORT deal_deadline ASC
LIMIT 15
```

## Dataview: High Priority

```dataview
TABLE industry, status, deal_status
FROM "business/crm"
WHERE priority = "High"
SORT deal_status DESC
LIMIT 20
```

## Dataview: By Industry

```dataview
TABLE WITHOUT ID
  industry as "Industry",
  length(rows) as "Count"
FROM "business/crm"
GROUP BY industry
SORT length(rows) DESC
```

## Dataview: By Status

```dataview
TABLE WITHOUT ID
  status as "Status",
  length(rows) as "Count"
FROM "business/crm"
GROUP BY status
SORT length(rows) DESC
```

## Dataview: Recently Updated

```dataview
TABLE industry, status, priority
FROM "business/crm"
SORT file.mtime DESC
LIMIT 20
```
