package metric

import (
	"context"

	"github.com/machuz/engineering-impact-score/internal/git"
)

type DebtData struct {
	Generated map[string]int
	Cleaned   map[string]int
}

// ResolveFunc maps a git author name to its canonical name
type ResolveFunc func(string) string

func CalcDebt(ctx context.Context, repoPath string, fixCommits []git.Commit, maxSample int, debtThreshold int, resolve ResolveFunc) (map[string]float64, *DebtData) {
	generated := make(map[string]int)
	cleaned := make(map[string]int)

	if resolve == nil {
		resolve = func(s string) string { return s }
	}

	// Sample fix commits
	sample := fixCommits
	if len(sample) > maxSample {
		sample = sample[:maxSample]
	}

	for _, fc := range sample {
		fixer := resolve(fc.Author)

		// Get changed files
		files, err := git.DiffTreeFiles(ctx, repoPath, fc.Hash)
		if err != nil {
			continue
		}

		for _, f := range files {
			if f == "" {
				continue
			}
			// Blame at parent to find original authors
			authors, err := git.BlameFileAtParent(ctx, repoPath, fc.Hash, f)
			if err != nil {
				continue
			}

			for _, origAuthor := range authors {
				origAuthor = resolve(origAuthor)
				if origAuthor != fixer && origAuthor != "" {
					generated[origAuthor]++
					cleaned[fixer]++
				}
			}
		}
	}

	// Calculate ratios
	result := make(map[string]float64)

	// Collect all authors
	allAuthors := make(map[string]bool)
	for a := range generated {
		allAuthors[a] = true
	}
	for a := range cleaned {
		allAuthors[a] = true
	}

	for author := range allAuthors {
		gen := generated[author]
		cln := cleaned[author]
		total := gen + cln

		if total < debtThreshold {
			result[author] = 50 // neutral
			continue
		}

		maxGen := gen
		if maxGen == 0 {
			maxGen = 1
		}
		result[author] = float64(cln) / float64(maxGen)
	}

	return result, &DebtData{Generated: generated, Cleaned: cleaned}
}
