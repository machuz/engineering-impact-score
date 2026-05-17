package metric

import (
	"path/filepath"
	"strings"
)

// DefaultModuleConventionDirs is the built-in set of monorepo-convention
// top-level directories. When a file path's FIRST component is one of
// these, the module is taken as its first 2 components (e.g.
// "services/ace"), anchoring module identity to a real project boundary
// instead of an arbitrary depth cut.
var DefaultModuleConventionDirs = []string{"services", "packages", "apps", "modules", "libs"}

// ModuleResolver maps a file path to a module identifier.
//
// Resolution is pure and deterministic (W-02 / W-03): the result depends
// only on (path, convention set). There is no package-level mutable state —
// a resolver is a value, constructed once from a convention set and threaded
// down to the metric functions that need it.
//
// Resolution rule:
//   - If the path's FIRST directory component is a known convention dir,
//     the module is its first 2 components: "<conventionDir>/<child>"
//     (e.g. "services/ace/backend/internal/x.go" -> "services/ace").
//   - Otherwise the module is the first 2 components of the path's dir
//     (e.g. "a/b/c/d.go" -> "a/b"). This conservative 2-layer default
//     yields fewer, larger modules than the historical 3-layer split, so
//     Breadth and module metrics don't inflate on deep trees.
//   - A dir with fewer than 2 components collapses to whatever components
//     exist (the whole dir, or "." for a root-level file).
type ModuleResolver struct {
	convention map[string]bool
}

// NewModuleResolver builds a resolver from a convention-dir set. When
// conventionDirs is empty, the built-in DefaultModuleConventionDirs is
// used; when non-empty it REPLACES the default set entirely.
func NewModuleResolver(conventionDirs []string) ModuleResolver {
	dirs := conventionDirs
	if len(dirs) == 0 {
		dirs = DefaultModuleConventionDirs
	}
	conv := make(map[string]bool, len(dirs))
	for _, d := range dirs {
		conv[d] = true
	}
	return ModuleResolver{convention: conv}
}

// ModuleOf returns the module identifier for a file path under this
// resolver's convention set. See ModuleResolver for the resolution rule.
func (r ModuleResolver) ModuleOf(path string) string {
	dir := filepath.Dir(path)
	parts := strings.Split(filepath.ToSlash(dir), "/")

	// Convention hit: first component is a known monorepo dir → 2 components.
	if len(parts) >= 2 && r.convention[parts[0]] {
		return parts[0] + "/" + parts[1]
	}

	// Default: conservative 2-component module.
	if len(parts) > 2 {
		parts = parts[:2]
	}
	return strings.Join(parts, "/")
}
