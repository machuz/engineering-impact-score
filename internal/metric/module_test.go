package metric

import "testing"

// Convention-aware resolution: a path whose first component is a known
// monorepo dir collapses to "<conventionDir>/<child>", anchoring module
// identity to a real project boundary instead of an arbitrary depth.
func TestModuleResolver_ConventionHit(t *testing.T) {
	r := NewModuleResolver(nil) // default convention set
	cases := []struct {
		path string
		want string
	}{
		{"services/ace/backend/internal/x.go", "services/ace"},
		{"services/true/frontend/src/App.tsx", "services/true"},
		{"packages/ui/src/Button.tsx", "packages/ui"},
		{"apps/web/main.go", "apps/web"},
		{"modules/auth/jwt.go", "modules/auth"},
		{"libs/core/util.go", "libs/core"},
	}
	for _, c := range cases {
		if got := r.ModuleOf(c.path); got != c.want {
			t.Errorf("ModuleOf(%q) = %q, want %q", c.path, got, c.want)
		}
	}
}

// Non-convention paths fall back to the conservative 2-component module —
// intentionally shallower than the historical 3-layer split so module
// metrics and Breadth don't inflate on deep trees.
func TestModuleResolver_NonConventionFallback(t *testing.T) {
	r := NewModuleResolver(nil)
	cases := []struct {
		path string
		want string
	}{
		{"a/b/c/d.go", "a/b"}, // 4-deep: was "a/b/c" under 3-layer
		{"internal/metric/survival.go", "internal/metric"},
		{"src/components/forms/Input.tsx", "src/components"},
	}
	for _, c := range cases {
		if got := r.ModuleOf(c.path); got != c.want {
			t.Errorf("ModuleOf(%q) = %q, want %q", c.path, got, c.want)
		}
	}
}

// Short paths must not panic and must collapse sanely: a 2-component dir
// stays whole, a root-level file resolves to ".".
func TestModuleResolver_ShortPaths(t *testing.T) {
	r := NewModuleResolver(nil)
	cases := []struct {
		path string
		want string
	}{
		{"a/b.go", "a"},     // dir is "a" (1 component)
		{"main.go", "."},    // root-level file: dir is "."
		{"a/b/c.go", "a/b"}, // dir is "a/b" (exactly 2)
		{"", "."},           // empty path: filepath.Dir("") == "."
	}
	for _, c := range cases {
		if got := r.ModuleOf(c.path); got != c.want {
			t.Errorf("ModuleOf(%q) = %q, want %q", c.path, got, c.want)
		}
	}
}

// A custom convention set REPLACES the default — "services" is no longer a
// convention dir, and the new "domains" dir is.
func TestModuleResolver_CustomConventionReplacesDefault(t *testing.T) {
	r := NewModuleResolver([]string{"domains"})

	// "domains" is now a convention dir.
	if got := r.ModuleOf("domains/payment/charge.go"); got != "domains/payment" {
		t.Errorf("custom convention: ModuleOf(domains/...) = %q, want domains/payment", got)
	}
	// "services" is NOT in the custom set → plain 2-layer fallback.
	if got := r.ModuleOf("services/ace/backend/internal/x.go"); got != "services/ace" {
		// 2-layer fallback of "services/ace/backend/internal" is "services/ace"
		t.Errorf("custom convention: ModuleOf(services/...) = %q, want services/ace (fallback)", got)
	}
	// A deep non-convention path still collapses to 2 components.
	if got := r.ModuleOf("packages/ui/src/Button.tsx"); got != "packages/ui" {
		t.Errorf("custom convention: ModuleOf(packages/...) = %q, want packages/ui (fallback)", got)
	}
}

// Depth invariant: no matter how deep the path, a module is at most 2
// components — the historical 3-layer split is gone. This holds whether or
// not the path sits under a convention dir (both the convention rule and
// the fallback cap at 2). The convention set exists to anchor module
// identity to project boundaries and as a config-stable forward hook; it
// does not re-introduce depth.
func TestModuleResolver_DepthCappedAtTwo(t *testing.T) {
	withServices := NewModuleResolver([]string{"services"})
	noServices := NewModuleResolver([]string{"apps"}) // "services" not a convention dir here

	deep := "services/ace/backend/internal/metric/x.go"
	if got := withServices.ModuleOf(deep); got != "services/ace" {
		t.Errorf("convention path: ModuleOf(%q) = %q, want services/ace", deep, got)
	}
	if got := noServices.ModuleOf(deep); got != "services/ace" {
		t.Errorf("fallback path: ModuleOf(%q) = %q, want services/ace (still 2-layer)", deep, got)
	}
}

// Empty convention set falls back to the built-in default.
func TestNewModuleResolver_EmptyUsesDefault(t *testing.T) {
	rEmpty := NewModuleResolver(nil)
	rExplicit := NewModuleResolver(DefaultModuleConventionDirs)
	path := "packages/ui/src/Button.tsx"
	if rEmpty.ModuleOf(path) != rExplicit.ModuleOf(path) {
		t.Errorf("empty convention set must equal explicit default set")
	}
	if rEmpty.ModuleOf(path) != "packages/ui" {
		t.Errorf("default set must treat 'packages' as a convention dir")
	}
}
