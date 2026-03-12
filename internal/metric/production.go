package metric

import (
	"path/filepath"

	"github.com/machuz/engineering-impact-score/internal/git"
)

func CalcProduction(commits []git.Commit, excludePatterns []string) map[string]float64 {
	result := make(map[string]float64)

	for _, c := range commits {
		for _, fs := range c.FileStats {
			if IsExcluded(fs.Filename, excludePatterns) {
				continue
			}
			result[c.Author] += float64(fs.Insertions + fs.Deletions)
		}
	}

	return result
}

// IsExcluded checks if a filename matches any of the exclude patterns.
func IsExcluded(filename string, patterns []string) bool {
	for _, pattern := range patterns {
		matched, _ := filepath.Match(pattern, filename)
		if matched {
			return true
		}
		// Also check basename
		base := filepath.Base(filename)
		matched, _ = filepath.Match(pattern, base)
		if matched {
			return true
		}
	}
	return false
}
