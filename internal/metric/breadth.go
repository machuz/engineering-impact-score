package metric

// ComputeBreadth derives the per-author raw Breadth score from commit
// counts, choosing the counting unit (repo vs module) per analysis run.
//
// Why a single shared function: the analyzer and timeline pipelines used to
// each carry their own copy of the breadth loop. Two copies drift — a
// threshold change in one is silently missed in the other, and the same
// git history then yields different Breadth depending on which entry point
// observed it. EIS requires determinism (W-02): identical input must give
// identical output regardless of pipeline. Folding both into this one
// function makes drift structurally impossible.
//
// Parameters:
//   - authorRepoCommits:   author -> repo   -> commit count
//   - authorModuleCommits: author -> module -> commit count
//   - unit:       "auto" | "repo" | "module" (empty string == "auto")
//   - minCommits: minimum commits in a repo/module for it to count
//   - repoCount:  number of repos in this analysis run (drives "auto")
//
// Unit selection:
//   - "auto":   repoCount == 1 -> module unit (monorepo), else repo unit.
//   - "repo":   always repo unit.
//   - "module": always module unit.
//
// The unit is decided once per run, not per author, so every author in the
// same run is counted the same way and their Breadth scores stay comparable.
//
// Raw Breadth for an author is the number of distinct keys (repos or
// modules) in which that author has at least minCommits commits. Authors
// with a zero count are omitted from the result map (mirroring the prior
// behaviour where Breadth was only set when count > 0).
func ComputeBreadth(
	authorRepoCommits map[string]map[string]int,
	authorModuleCommits map[string]map[string]int,
	unit string,
	minCommits int,
	repoCount int,
) map[string]float64 {
	if minCommits < 1 {
		minCommits = 1
	}

	useModule := false
	switch unit {
	case "module":
		useModule = true
	case "repo":
		useModule = false
	default: // "auto" and any unrecognised value
		useModule = repoCount == 1
	}

	source := authorRepoCommits
	if useModule {
		source = authorModuleCommits
	}

	result := make(map[string]float64, len(source))
	for author, counts := range source {
		count := 0
		for _, c := range counts {
			if c >= minCommits {
				count++
			}
		}
		if count > 0 {
			result[author] = float64(count)
		}
	}
	return result
}
