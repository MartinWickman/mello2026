#!/usr/bin/env python3
"""Mello 2026 - Vote tallying and validation script.

Reads a Google Forms TSV export and produces:
- Validation of all ballots
- Ranked results with tiebreakers
- Champion (10p) and hater (1p) info per song
- Destination assignments (Final / Andra Chansen / Eliminated)
"""

import csv
import sys
from collections import defaultdict

VALID_POINTS = {1, 2, 3, 4, 5, 6, 8, 10}
EXPECTED_SUM = sum(VALID_POINTS)  # 39


def parse_tsv(filepath):
    """Parse Google Forms TSV and return song names, voters list."""
    with open(filepath, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)

    # Extract song names from header columns (between Timestamp and "Säg nåt smart")
    songs = []
    song_cols = []
    for i, col in enumerate(header):
        if col.startswith("Lyssna"):
            # Extract "Song / Band" from "Lyssna, njut och rösta!  [Song / Band]"
            name = col.split("[")[1].rstrip("]")
            songs.append(name)
            song_cols.append(i)

    # Find name column
    name_col = None
    for i, col in enumerate(header):
        if "namn" in col.lower():
            name_col = i
            break

    # Parse votes
    voters = []
    with open(filepath, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # skip header
        for row in reader:
            if not row or not row[0].strip():
                continue
            name = row[name_col].strip() if name_col and name_col < len(row) else "Unknown"
            points = []
            for col_idx in song_cols:
                val = row[col_idx].strip().replace(" p", "").replace("p", "")
                points.append(int(val))
            voters.append({"name": name, "points": points})

    return songs, voters


def validate(songs, voters):
    """Validate all ballots. Returns list of error strings (empty = all good)."""
    errors = []
    for v in voters:
        name = v["name"]
        pts = v["points"]
        pts_set = set(pts)

        if len(pts) != len(songs):
            errors.append(f"{name}: voted on {len(pts)} songs, expected {len(songs)}")

        if pts_set != VALID_POINTS:
            missing = VALID_POINTS - pts_set
            extra = pts_set - VALID_POINTS
            if missing:
                errors.append(f"{name}: missing point values {sorted(missing)}")
            if extra:
                errors.append(f"{name}: invalid point values {sorted(extra)}")

        if len(pts) != len(pts_set):
            dupes = [p for p in VALID_POINTS if pts.count(p) > 1]
            errors.append(f"{name}: duplicate points {dupes}")

        if sum(pts) != EXPECTED_SUM:
            errors.append(f"{name}: sum is {sum(pts)}, expected {EXPECTED_SUM}")

    return errors


def tally(songs, voters):
    """Compute totals, rankings, champions, haters."""
    num_songs = len(songs)
    totals = [0] * num_songs
    champions = defaultdict(list)  # song_idx -> [voter names]
    haters = defaultdict(list)     # song_idx -> [voter names]

    for v in voters:
        for i, pts in enumerate(v["points"]):
            totals[i] += pts
            if pts == 10:
                champions[i].append(v["name"])
            if pts == 1:
                haters[i].append(v["name"])

    # Build results list
    results = []
    for i in range(num_songs):
        # Count votes at each point level for tiebreaking (descending: 10, 8, 6, 5, 4, 3, 2, 1)
        vote_counts = {}
        for p in sorted(VALID_POINTS, reverse=True):
            vote_counts[p] = sum(1 for v in voters if v["points"][i] == p)

        results.append({
            "song": songs[i],
            "total": totals[i],
            "champions": champions[i],
            "haters": haters[i],
            "vote_counts": vote_counts,
            "index": i,
        })

    # Sort: by total descending, then tiebreak by most 10s, most 8s, etc.
    def sort_key(r):
        tiebreak = tuple(r["vote_counts"][p] for p in sorted(VALID_POINTS, reverse=True))
        return (r["total"], tiebreak)

    results.sort(key=sort_key, reverse=True)

    # Assign positions (handle ties)
    pos = 1
    for i, r in enumerate(results):
        if i > 0 and sort_key(results[i]) == sort_key(results[i - 1]):
            r["position"] = results[i - 1]["position"]
        else:
            r["position"] = pos
        pos += 1

    # Assign destinations: 1-2 Final, 3-4 Andra Chansen, 5+ Eliminated
    for i, r in enumerate(results):
        rank = i + 1  # 1-based rank after tiebreaking
        if rank <= 2:
            r["destination"] = "FINAL"
        elif rank <= 4:
            r["destination"] = "ANDRA CHANSEN"
        else:
            r["destination"] = "Eliminated"

    return results


def print_results(songs, voters, results):
    """Print formatted results."""
    print(f"{'='*60}")
    print(f"MELLO 2026 - RESULTS ({len(voters)} voters, {len(songs)} songs)")
    print(f"{'='*60}\n")

    # Results table
    print(f"{'#':<4} {'Song':<40} {'Pts':>4}  {'10p':>3}  {'Destination':<15}  Champions (10p) / Haters (1p)")
    print("-" * 110)

    for r in results:
        champs = ", ".join(r["champions"]) if r["champions"] else "None"
        haters_str = ", ".join(r["haters"]) if r["haters"] else "None"
        num_10s = r["vote_counts"][10]
        print(
            f"{r['position']:<4} {r['song']:<40} {r['total']:>4}  {num_10s:>3}  "
            f"{r['destination']:<15}  10p: {champs} | 1p: {haters_str}"
        )

    # Voter summary
    print(f"\n{'='*60}")
    print("VOTER VALIDATION")
    print(f"{'='*60}")
    for v in voters:
        print(f"  {v['name']:<25} sum={sum(v['points'])}  points={v['points']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python tally.py <path-to-tsv>")
        sys.exit(1)

    filepath = sys.argv[1]
    songs, voters = parse_tsv(filepath)

    # Validate
    errors = validate(songs, voters)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        print()

    # Tally and display
    results = tally(songs, voters)
    print_results(songs, voters, results)

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
