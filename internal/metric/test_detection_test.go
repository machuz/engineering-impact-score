package metric

import "testing"

func TestIsTestFile(t *testing.T) {
	cases := []struct {
		name string
		path string
		want bool
	}{
		{"go test", "internal/foo_test.go", true},
		{"go prod", "internal/foo.go", false},
		{"ts test", "src/foo.test.ts", true},
		{"ts spec", "src/foo.spec.ts", true},
		{"tsx test", "src/Page.test.tsx", true},
		{"ts prod", "src/foo.ts", false},
		{"py test_ prefix", "tests/test_user.py", true},
		{"py _test suffix", "app/user_test.py", true},
		{"py prod", "app/user.py", false},
		{"ruby spec", "spec/user_spec.rb", true},
		{"ruby prod", "app/user.rb", false},
		{"java FooTest", "src/main/java/UserTest.java", true},
		{"java TestFoo", "src/main/java/TestUser.java", true},
		{"java prod", "src/main/java/User.java", false},
		{"kotlin Test suffix", "src/UserTest.kt", true},
		{"scala Spec suffix", "src/UserSpec.scala", true},
		{"rust tests dir", "tests/integration.rs", true},
		{"__tests__ folder", "src/components/__tests__/Button.tsx", true},
		{"src/test/ path", "src/test/java/UserTest.java", true},
		{"nested test dir", "internal/lib/test/helpers.go", true},
		{"markdown doc", "README.md", false},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := IsTestFile(c.path); got != c.want {
				t.Errorf("IsTestFile(%q) = %v, want %v", c.path, got, c.want)
			}
		})
	}
}

func TestTestedSet_SiblingPair(t *testing.T) {
	files := []string{
		"pkg/user.go",
		"pkg/user_test.go",
		"pkg/billing.go", // no sibling test
	}
	ts := BuildTestedSet(files)
	if !ts.IsTested("pkg/user.go") {
		t.Error("user.go must be tested (sibling pair)")
	}
	if !ts.IsTested("pkg/user_test.go") {
		t.Error("test file itself must count as tested")
	}
	// billing.go has no sibling, but module fallback: same dir has user_test.go
	// → tested via Rule 3.
	if !ts.IsTested("pkg/billing.go") {
		t.Error("billing.go should be tested via module fallback")
	}
}

func TestTestedSet_ModuleFallback(t *testing.T) {
	files := []string{
		"api/handler.go",
		"api/router.go",
		"api/router_test.go", // covers router, modulé has one test
		"legacy/old.go",       // no test anywhere in legacy/
	}
	ts := BuildTestedSet(files)
	if !ts.IsTested("api/router.go") {
		t.Error("router.go tested via sibling")
	}
	if !ts.IsTested("api/handler.go") {
		t.Error("handler.go tested via module fallback")
	}
	if ts.IsTested("legacy/old.go") {
		t.Error("legacy/old.go has no test — must be untested")
	}
}

func TestTestedSet_CrossLanguage(t *testing.T) {
	files := []string{
		"backend/user.py",
		"backend/test_user.py",
		"frontend/src/Button.tsx",
		"frontend/src/Button.test.tsx",
		"untested/forgotten.go",
	}
	ts := BuildTestedSet(files)
	if !ts.IsTested("backend/user.py") {
		t.Error("py sibling pair failed")
	}
	if !ts.IsTested("frontend/src/Button.tsx") {
		t.Error("tsx sibling pair failed")
	}
	if ts.IsTested("untested/forgotten.go") {
		t.Error("untested file mistakenly marked tested")
	}
}

func TestTestedSet_Ratio(t *testing.T) {
	files := []string{"a.go", "a_test.go", "b.go", "c.go"}
	ts := BuildTestedSet(files)
	if ts.TotalFiles != 4 || ts.TotalTestFiles != 1 {
		t.Errorf("counts off: total=%d tests=%d", ts.TotalFiles, ts.TotalTestFiles)
	}
	if ts.TestFileRatio != 0.25 {
		t.Errorf("ratio = %v, want 0.25", ts.TestFileRatio)
	}
}

func TestTestedSet_NilReceiver(t *testing.T) {
	var ts *TestedSet
	if ts.IsTested("anything") {
		t.Error("nil receiver must return false")
	}
}

func TestTestedSet_EmptyRepo(t *testing.T) {
	ts := BuildTestedSet(nil)
	if ts == nil {
		t.Fatal("should not return nil for empty input")
	}
	if ts.TotalFiles != 0 {
		t.Errorf("TotalFiles = %d, want 0", ts.TotalFiles)
	}
	if ts.IsTested("foo.go") {
		t.Error("empty repo: everything is untested")
	}
}

func TestTestedSet_ModuleTestRatio(t *testing.T) {
	files := []string{
		// api/: 2 prod + 1 test (ratio ≈ 0.33)
		"api/handler.go",
		"api/router.go",
		"api/router_test.go",
		// legacy/: 3 prod, no tests (ratio = 0)
		"legacy/a.go",
		"legacy/b.go",
		"legacy/c.go",
	}
	ts := BuildTestedSet(files)

	apiRatio, ok := ts.ModuleTestRatio("api")
	if !ok {
		t.Fatal("api module missing from ratio map")
	}
	if apiRatio < 0.33 || apiRatio > 0.34 {
		t.Errorf("api ratio = %v, want ≈0.333", apiRatio)
	}

	legacyRatio, ok := ts.ModuleTestRatio("legacy")
	if !ok {
		t.Fatal("legacy module missing from ratio map")
	}
	if legacyRatio != 0 {
		t.Errorf("legacy ratio = %v, want 0", legacyRatio)
	}

	if _, ok := ts.ModuleTestRatio("nonexistent"); ok {
		t.Error("nonexistent module should return (0, false)")
	}
}
