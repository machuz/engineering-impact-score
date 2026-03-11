package metric

import (
	"math"
	"time"

	"github.com/machuz/engineering-impact-score/internal/git"
)

func CalcSurvival(blameLines []git.BlameLine, tau float64) map[string]float64 {
	now := time.Now()
	result := make(map[string]float64)

	for _, bl := range blameLines {
		daysAlive := now.Sub(bl.CommitterTime).Hours() / 24
		if daysAlive < 0 {
			daysAlive = 0
		}
		weight := math.Exp(-daysAlive / tau)
		result[bl.Author] += weight
	}

	return result
}
