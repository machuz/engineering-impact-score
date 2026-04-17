package scorer

import "testing"

// baseStableModule returns a ModuleScore that satisfies the Vitality=Stable
// preconditions (high Stability, plenty of blame lines, has active commits).
// Individual tests flip fields to check classification transitions.
func baseStableModule() ModuleScore {
	return ModuleScore{
		Module:           "pkg/sample",
		Stability:        95, // low change pressure
		ChangeAbsorption: 80, // code survives well
		BlameLines:       500,
		ModuleCommits:    10,
		OwnerActive:      true,
		HasTestRatio:     true,
		TestFileRatio:    0.30, // healthy coverage
	}
}

func TestModuleVitality_StableWithTests(t *testing.T) {
	ms := baseStableModule()
	name, conf := classifyVitality(ms)
	if name != "Stable" {
		t.Errorf("well-tested stable module classified as %q (conf=%v), want Stable", name, conf)
	}
}

func TestModuleVitality_FragileWhenUntested(t *testing.T) {
	ms := baseStableModule()
	ms.TestFileRatio = 0.02 // almost no tests
	name, conf := classifyVitality(ms)
	if name != "Fragile" {
		t.Fatalf("untested stable module classified as %q (conf=%v), want Fragile", name, conf)
	}
	if conf < 0.70 || conf > 0.95 {
		t.Errorf("Fragile confidence = %v, want within [0.70, 0.95]", conf)
	}
}

func TestModuleVitality_FragileNoCoverageDataFallsBack(t *testing.T) {
	ms := baseStableModule()
	ms.HasTestRatio = false // pre-v2 repo: no manifest data
	ms.TestFileRatio = 0
	name, _ := classifyVitality(ms)
	if name != "Stable" {
		t.Errorf("without coverage data must fall back to Stable, got %q", name)
	}
}

// An actively-changing module must NOT be Fragile even if tests are missing.
func TestModuleVitality_ActiveWithoutTestsNotFragile(t *testing.T) {
	ms := baseStableModule()
	ms.Stability = 20       // lots of change pressure
	ms.ChangeAbsorption = 40
	ms.TestFileRatio = 0.02
	name, _ := classifyVitality(ms)
	if name == "Fragile" {
		t.Errorf("active-but-untested module wrongly flagged Fragile")
	}
}

// A module with no surviving code (low ChangeAbsorption) is not a fossil.
func TestModuleVitality_NoSurvivalNotFragile(t *testing.T) {
	ms := baseStableModule()
	ms.TestFileRatio = 0
	ms.ChangeAbsorption = 10 // code churn wiped old stuff
	name, _ := classifyVitality(ms)
	if name == "Fragile" {
		t.Errorf("short-lived code wrongly flagged Fragile")
	}
}

// A module with zero commits is Dead, not Fragile.
func TestModuleVitality_DeadBeatsFragile(t *testing.T) {
	ms := baseStableModule()
	ms.ModuleCommits = 0
	ms.OwnerActive = false
	ms.TestFileRatio = 0
	name, _ := classifyVitality(ms)
	if name != "Dead" {
		t.Errorf("zero-commit module classified as %q, want Dead", name)
	}
}

// IsAnomaly treats Fragile as a risk alongside Turbulent/Critical/Dead.
func TestModuleVitality_FragileIsAnomaly(t *testing.T) {
	ms := ModuleScore{Vitality: "Fragile"}
	if !ms.IsAnomaly() {
		t.Error("Fragile module must be flagged as anomaly")
	}
}
