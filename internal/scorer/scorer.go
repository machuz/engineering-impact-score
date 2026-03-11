package scorer

import (
	"sort"

	"github.com/machuz/engineering-impact-score/internal/config"
	"github.com/machuz/engineering-impact-score/internal/metric"
)

type Result struct {
	Author           string
	Production       float64
	Quality          float64
	Survival         float64
	Design           float64
	Breadth          float64
	DebtCleanup      float64
	Indispensability float64
	Total            float64
	Archetype        string
}

func Score(raw *metric.RawScores, cfg *config.Config) []Result {
	// Normalize each axis
	normProd := Normalize(raw.Production)
	normQual := Normalize(raw.Quality)
	normSurv := Normalize(raw.Survival)
	normDesign := Normalize(raw.Design)
	normBreadth := Normalize(raw.Breadth)
	normDebt := NormalizeDebt(raw.DebtCleanup)
	normIndisp := Normalize(raw.Indispensability)

	// Collect all authors
	authors := raw.Authors()
	w := cfg.Weights

	var results []Result
	for _, author := range authors {
		r := Result{
			Author:           author,
			Production:       normProd[author],
			Quality:          normQual[author],
			Survival:         normSurv[author],
			Design:           normDesign[author],
			Breadth:          normBreadth[author],
			DebtCleanup:      normDebt[author],
			Indispensability: normIndisp[author],
		}

		r.Total = r.Production*w.Production +
			r.Quality*w.Quality +
			r.Survival*w.Survival +
			r.Design*w.Design +
			r.Breadth*w.Breadth +
			r.DebtCleanup*w.DebtCleanup +
			r.Indispensability*w.Indispensability

		r.Archetype = classifyArchetype(r)

		results = append(results, r)
	}

	// Sort by total descending
	sort.Slice(results, func(i, j int) bool {
		return results[i].Total > results[j].Total
	})

	return results
}

// NormalizeDebt handles debt cleanup specially: ratio values where >1 is good
func NormalizeDebt(values map[string]float64) map[string]float64 {
	return Normalize(values)
}
