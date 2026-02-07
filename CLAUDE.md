# Mello 2026 - Music Competition

## Overview
A music competition where participants vote on songs across multiple rounds.

## Voting Rules
- Each participant votes on all songs in a heat
- Points available: 1, 2, 3, 4, 5, 6, 8, and 10 (no 7 or 9)
- Each point value must be used exactly once per participant
- The sum of all points from one participant is always 39

## Data Format
- Results come as tab-separated (TSV) files exported from Google Forms
- Each row is a participant, columns are songs
- Points are formatted as "N p" (e.g., "6 p")
- Additional columns: Timestamp, a comment field ("Säg nåt smart"), and participant name ("Ditt namn")

## Validation Checks
When processing results, always verify:
1. Each participant uses every allowed point value exactly once (no duplicates)
2. Each participant's points sum to 39
3. Only valid point values are used (1, 2, 3, 4, 5, 6, 8, 10)

## Output
- Rank songs by total points
- Show which participants gave 10p to each song and also who gave 1p to each song
- Note any tiebreakers (more 10p votes wins ties)
- Flag any invalid ballots

## Tiebreaker Rules
- If songs are tied on total points for advancing positions, break ties by:
  1. Most number of 10-point votes
  2. If still tied, most number of 8-point votes
  3. Continue down through 6, 5, 4, 3, 2, 1 if needed

## Tallying Script
- `tally.py` in the project root handles vote parsing, validation, and ranking
- Usage: `python3 tally.py <path-to-tsv>`
- Always run this to verify calculations rather than doing mental math

## Competition Structure
- **4 heats** (deltävlingar), each with 8 songs
  - 1st and 2nd place → go directly to the Final
  - 3rd and 4th place → go to the Second Chance heat
- **Second Chance** (5th heat): 8 songs (3rd+4th from each of the 4 heats)
  - 1st and 2nd place → go to the Final
- **Final**: 10 songs total (2 from each heat + 2 from Second Chance)
