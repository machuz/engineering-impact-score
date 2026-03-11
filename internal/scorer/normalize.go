package scorer

import "math"

func Normalize(values map[string]float64) map[string]float64 {
	maxVal := 0.0
	for _, v := range values {
		if v > maxVal {
			maxVal = v
		}
	}

	result := make(map[string]float64)
	for author, v := range values {
		if maxVal == 0 {
			result[author] = 0
		} else {
			result[author] = math.Min(v/maxVal*100, 100)
		}
	}
	return result
}
