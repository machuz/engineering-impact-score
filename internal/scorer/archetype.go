package scorer

func classifyArchetype(r Result) string {
	high := func(v float64) bool { return v >= 60 }
	mid := func(v float64) bool { return v >= 30 && v < 60 }
	low := func(v float64) bool { return v < 30 }

	switch {
	// Architect: high production, survival, design, debt cleanup
	case high(r.Production) && high(r.Survival) && high(r.Design) && mid(r.DebtCleanup):
		return "Architect"
	case high(r.Production) && high(r.Survival) && high(r.Design):
		return "Architect"

	// Mass Producer: high production, low quality/survival/debt
	case high(r.Production) && low(r.Survival) && low(r.DebtCleanup):
		return "Mass Producer"
	case high(r.Production) && low(r.Survival):
		return "Mass Producer"

	// Solid Cleaner: mid+ production, high quality/survival/debt
	case high(r.Quality) && high(r.Survival) && high(r.DebtCleanup):
		return "Solid Cleaner"
	case mid(r.Quality) && mid(r.Survival) && high(r.DebtCleanup):
		return "Solid Cleaner"

	// Political: high breadth, low everything else
	case high(r.Breadth) && low(r.Production) && low(r.Design):
		return "Political"

	// Specialist: high in narrow area, low breadth
	case high(r.Survival) && low(r.Breadth):
		return "Specialist"

	// Growing: low production but good quality
	case low(r.Production) && high(r.Quality):
		return "Growing"

	// Solid: decent across the board but not extreme in any
	case mid(r.Production) && mid(r.Quality) && mid(r.Survival):
		return "Solid"

	default:
		if r.Total >= 40 {
			return "Solid"
		}
		return "—"
	}
}
