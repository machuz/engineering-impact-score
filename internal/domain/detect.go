package domain

import (
	"path/filepath"
	"strings"
)

// Domain represents a scoring domain (BE, FE, Infra, Firmware)
type Domain string

const (
	Backend  Domain = "Backend"
	Frontend Domain = "Frontend"
	Infra    Domain = "Infra"
	Firmware Domain = "Firmware"
	Unknown  Domain = "Unknown"
)

// AllDomains returns all known domains in display order
func AllDomains() []Domain {
	return []Domain{Backend, Frontend, Infra, Firmware}
}

// file extension -> domain mapping
var extDomain = map[string]Domain{
	// Backend
	".go":    Backend,
	".py":    Backend,
	".java":  Backend,
	".rb":    Backend,
	".rs":    Backend,
	".scala": Backend,
	".hs":    Backend,
	".ml":    Backend,
	".mli":   Backend,
	".php":   Backend,
	".cs":    Backend,
	".kt":    Backend,

	// Frontend
	".ts":     Frontend,
	".tsx":    Frontend,
	".js":     Frontend,
	".jsx":    Frontend,
	".vue":    Frontend,
	".svelte": Frontend,
	".css":    Frontend,
	".scss":   Frontend,
	".less":   Frontend,
	".html":   Frontend,

	// Infra
	".tf":     Infra,
	".hcl":    Infra,
	".yaml":   Infra,
	".yml":    Infra,
	".toml":   Infra,

	// Firmware
	".c":   Firmware,
	".h":   Firmware,
	".cpp": Firmware,
	".hpp": Firmware,
	".cc":  Firmware,
	".S":   Firmware,
	".s":   Firmware,
	".ld":  Firmware,
}

// DetectFromFiles determines the domain of a repo based on file extension distribution.
// Returns the domain with the highest file count.
func DetectFromFiles(files []string) Domain {
	counts := make(map[Domain]int)

	for _, f := range files {
		ext := strings.ToLower(filepath.Ext(f))
		if d, ok := extDomain[ext]; ok {
			counts[d]++
		}
	}

	if len(counts) == 0 {
		return Unknown
	}

	// Special case: .yaml/.yml files alone don't make it Infra.
	// Only classify as Infra if Infra has more files than BE+FE combined,
	// or if there are .tf/.hcl files present.
	if counts[Infra] > 0 {
		hasTerraform := false
		for _, f := range files {
			ext := strings.ToLower(filepath.Ext(f))
			if ext == ".tf" || ext == ".hcl" {
				hasTerraform = true
				break
			}
		}
		if !hasTerraform {
			// YAML/TOML only — likely config files, not an infra repo
			delete(counts, Infra)
		}
	}

	// Find domain with highest count
	var best Domain
	bestCount := 0
	for d, c := range counts {
		if c > bestCount {
			best = d
			bestCount = c
		}
	}

	return best
}

// MatchRepoPattern checks if a repo name matches a glob pattern
func MatchRepoPattern(repoName string, patterns []string) bool {
	for _, pattern := range patterns {
		matched, _ := filepath.Match(pattern, repoName)
		if matched {
			return true
		}
	}
	return false
}
