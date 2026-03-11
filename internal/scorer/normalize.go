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

// NormalizeQuality is special: quality is already 0-100, but we still
// normalize relative to the max in the group for consistency
func NormalizeQuality(values map[string]float64) map[string]float64 {
	return Normalize(values)
}
