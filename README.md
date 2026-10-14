# eaw-portal-data

## whosout.json
Feed for the **Who's Out Today / Birthdays** cards on the EAW hub. Written by the Who's Out updater from the Outlook calendar "EAW Time Off Requests". Do not edit by hand.
Names, dates and request type only (e.g. "ANGELA OFF - Vacation"). **Never put comments or reasons in this file** — this repository is public.
Each event is `[subject, start, end, allDay]`, same shape the hub already uses. All-day events end at midnight *after* the last day out.
