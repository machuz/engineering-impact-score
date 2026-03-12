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
	RawSurvival      float64 // normalized raw blame (no decay), used for archetype detection
	Design           float64
	Breadth          float64
	DebtCleanup      float64
	Indispensability float64
	Total            float64
	Archetype        string
}

func Score(raw *metric.RawScores, cfg *config.Config) []Result {
	// Production: absolute scale — raw.Production is already per-day rate
	// Score = min(per_day / production_daily_ref * 100, 100)
	normProd := make(map[string]float64)
	for author, perDay := range raw.Production {
		score := perDay / cfg.ProductionDailyRef * 100
		if score > 100 {
			score = 100
		}
		normProd[author] = score
	}
	normSurv := Normalize(raw.Survival)
	normDesign := Normalize(raw.Design)
	normIndisp := Normalize(raw.Indispensability)
	normRawSurv := Normalize(raw.RawSurvival)

	// Quality is already on 0-100 absolute scale (100 - fix_ratio), use directly
	// This makes Quality scores comparable across organizations
	normQual := raw.Quality

	// Breadth: relative scale — normalized within the group
	normBreadth := Normalize(raw.Breadth)

	// Debt is already on 0-100 scale, use directly
	normDebt := raw.DebtCleanup

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
			RawSurvival:      normRawSurv[author],
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
