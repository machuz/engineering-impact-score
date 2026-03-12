package metric

import (
	"math"
	"time"

	"github.com/machuz/engineering-impact-score/internal/git"
)

// SurvivalResult holds both time-decayed and raw (non-decayed) blame counts.
type SurvivalResult struct {
	Decayed map[string]float64 // time-weighted survival
	Raw     map[string]float64 // raw blame line count (no decay)
}

func CalcSurvival(blameLines []git.BlameLine, tau float64, now time.Time) SurvivalResult {
	decayed := make(map[string]float64)
	raw := make(map[string]float64)

	for _, bl := range blameLines {
		raw[bl.Author]++

		daysAlive := now.Sub(bl.CommitterTime).Hours() / 24
		if daysAlive < 0 {
			daysAlive = 0
		}
		weight := math.Exp(-daysAlive / tau)
		decayed[bl.Author] += weight
	}

	return SurvivalResult{Decayed: decayed, Raw: raw}
}
