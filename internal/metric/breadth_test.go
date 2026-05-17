package metric

import "testing"

// repo-unit counting: count distinct repos where the author has >= minCommits.
func TestComputeBreadth_RepoUnit(t *testing.T) {
	repoCommits := map[string]map[string]int{
		// A reaches 3 repos at >=3 commits, plus one repo below threshold.
		"A": {"repo1": 5, "repo2": 3, "repo3": 9, "repo4": 1},
		// B reaches only 1 repo at >=3.
		"B": {"repo1": 4, "repo2": 2},
	}
	moduleCommits := map[string]map[string]int{} // unused for repo unit

	got := ComputeBreadth(repoCommits, moduleCommits, "repo", 3, 4)
	if got["A"] != 3 {
		t.Errorf("A repo-unit Breadth = %v, want 3", got["A"])
	}
	if got["B"] != 1 {
		t.Errorf("B repo-unit Breadth = %v, want 1", got["B"])
	}
}

// module-unit counting: count distinct modules where the author has >= minCommits.
func TestComputeBreadth_ModuleUnit(t *testing.T) {
	repoCommits := map[string]map[string]int{
		"A": {"monorepo": 50}, // single repo — repo unit would give 1
	}
	moduleCommits := map[string]map[string]int{
		"A": {"services/ace": 20, "services/true": 8, "packages/ui": 3, "apps/web": 2},
	}

	got := ComputeBreadth(repoCommits, moduleCommits, "module", 3, 1)
	// 3 modules at >=3 commits (ace, true, ui); apps/web has 2 → excluded.
	if got["A"] != 3 {
		t.Errorf("A module-unit Breadth = %v, want 3", got["A"])
	}
}

// auto: a single-repo run uses the module unit (monorepo case).
func TestComputeBreadth_AutoPicksModuleForSingleRepo(t *testing.T) {
	repoCommits := map[string]map[string]int{
		"A": {"monorepo": 30},
	}
	moduleCommits := map[string]map[string]int{
		"A": {"services/ace": 10, "services/true": 5},
	}
	got := ComputeBreadth(repoCommits, moduleCommits, "auto", 3, 1)
	// repoCount == 1 → module unit → 2 modules.
	if got["A"] != 2 {
		t.Errorf("auto/single-repo Breadth = %v, want 2 (module unit)", got["A"])
	}
}

// auto: a multi-repo run uses the repo unit.
func TestComputeBreadth_AutoPicksRepoForMultiRepo(t *testing.T) {
	repoCommits := map[string]map[string]int{
		"A": {"repo1": 10, "repo2": 5},
	}
	moduleCommits := map[string]map[string]int{
		// Module data exists but must be ignored when repoCount > 1.
		"A": {"m1": 4, "m2": 4, "m3": 4, "m4": 4},
	}
	got := ComputeBreadth(repoCommits, moduleCommits, "auto", 3, 3)
	// repoCount == 3 → repo unit → 2 repos, not 4 modules.
	if got["A"] != 2 {
		t.Errorf("auto/multi-repo Breadth = %v, want 2 (repo unit)", got["A"])
	}
}

// The minCommits threshold filters: a module with 2 commits is not counted
// at min=3, but is counted at min=2.
func TestComputeBreadth_MinCommitsThreshold(t *testing.T) {
	repoCommits := map[string]map[string]int{"A": {"mono": 9}}
	moduleCommits := map[string]map[string]int{
		"A": {"big": 5, "small": 2}, // "small" has exactly 2 commits
	}

	atThree := ComputeBreadth(repoCommits, moduleCommits, "module", 3, 1)
	if atThree["A"] != 1 {
		t.Errorf("min=3: Breadth = %v, want 1 (small excluded)", atThree["A"])
	}

	atTwo := ComputeBreadth(repoCommits, moduleCommits, "module", 2, 1)
	if atTwo["A"] != 2 {
		t.Errorf("min=2: Breadth = %v, want 2 (small now counted)", atTwo["A"])
	}
}

// An author with no repo/module reaching the threshold is omitted entirely
// (mirrors the prior "set only when count > 0" behaviour).
func TestComputeBreadth_ZeroCountOmitted(t *testing.T) {
	repoCommits := map[string]map[string]int{
		"A": {"repo1": 1, "repo2": 2}, // nothing reaches 3
	}
	got := ComputeBreadth(repoCommits, nil, "repo", 3, 2)
	if _, present := got["A"]; present {
		t.Errorf("A should be omitted (no repo at >=3 commits), got %v", got["A"])
	}
}

// The unit is a per-run decision: every author in one run is counted the
// same way, so a multi-repo run never silently switches some authors to
// module counting.
func TestComputeBreadth_UnitIsPerRunNotPerAuthor(t *testing.T) {
	repoCommits := map[string]map[string]int{
		"A": {"repo1": 5, "repo2": 5}, // 2 repos
		"B": {"repo1": 5},             // 1 repo
	}
	moduleCommits := map[string]map[string]int{
		"A": {"m1": 5, "m2": 5, "m3": 5},
		"B": {"m1": 5, "m2": 5, "m3": 5, "m4": 5},
	}
	got := ComputeBreadth(repoCommits, moduleCommits, "auto", 3, 2)
	// repoCount == 2 → repo unit for BOTH authors.
	if got["A"] != 2 {
		t.Errorf("A Breadth = %v, want 2 (repo unit applies to all)", got["A"])
	}
	if got["B"] != 1 {
		t.Errorf("B Breadth = %v, want 1 (repo unit applies to all)", got["B"])
	}
}
