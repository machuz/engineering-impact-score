package metric

import (
	"path/filepath"
	"strings"

	"github.com/machuz/engineering-impact-score/internal/git"
)

type ModuleRisk struct {
	Module    string
	TopAuthor string
	Share     float64
	Level     string // "CRITICAL" or "HIGH"
}

func CalcIndispensability(blameLines []git.BlameLine, criticalThreshold, highThreshold float64) (map[string]float64, []ModuleRisk) {
	// Group blame lines by module (top-level directory)
	moduleAuthors := make(map[string]map[string]int) // module -> author -> count

	for _, bl := range blameLines {
		module := getModule(bl.Filename)
		if module == "" {
			continue
		}

		if _, ok := moduleAuthors[module]; !ok {
			moduleAuthors[module] = make(map[string]int)
		}
		moduleAuthors[module][bl.Author]++
	}

	// Calculate indispensability per author
	criticalModules := make(map[string]int)
	highModules := make(map[string]int)
	var risks []ModuleRisk

	for module, authors := range moduleAuthors {
		total := 0
		topAuthor := ""
		topCount := 0

		for author, count := range authors {
			total += count
			if count > topCount {
				topCount = count
				topAuthor = author
			}
		}

		if total == 0 {
			continue
		}

		share := float64(topCount) / float64(total)

		if share >= criticalThreshold {
			criticalModules[topAuthor]++
			risks = append(risks, ModuleRisk{
				Module:    module,
				TopAuthor: topAuthor,
				Share:     share,
				Level:     "CRITICAL",
			})
		} else if share >= highThreshold {
			highModules[topAuthor]++
			risks = append(risks, ModuleRisk{
				Module:    module,
				TopAuthor: topAuthor,
				Share:     share,
				Level:     "HIGH",
			})
		}
	}

	result := make(map[string]float64)
	allAuthors := make(map[string]bool)
	for a := range criticalModules {
		allAuthors[a] = true
	}
	for a := range highModules {
		allAuthors[a] = true
	}

	for author := range allAuthors {
		result[author] = float64(criticalModules[author])*1.0 + float64(highModules[author])*0.5
	}

	return result, risks
}

func getModule(filename string) string {
	parts := strings.Split(filepath.ToSlash(filename), "/")
	if len(parts) < 2 {
		return ""
	}
	// Use first two path components as module (e.g., "app/domain")
	if len(parts) >= 3 {
		return parts[0] + "/" + parts[1]
	}
	return parts[0]
}
