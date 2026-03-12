package output

import (
	"fmt"
	"sort"
	"strings"

	"github.com/fatih/color"
	"github.com/machuz/engineering-impact-score/internal/team"
)

// PrintTeamTable renders team results with bar charts to the terminal.
func PrintTeamTable(teams []team.TeamResult) {
	for _, tr := range teams {
		printTeamHeader(tr)
		printTeamClassification(tr)
		printAxisAverages(tr)
		printDistribution("Role", tr.RoleDist, tr.MemberCount)
		printDistribution("Style", tr.StyleDist, tr.MemberCount)
		printDistribution("State", tr.StateDist, tr.MemberCount)
		printTeamHealth(tr)
		printStructureMetrics(tr)
		fmt.Println()
	}
}

func printTeamHeader(tr team.TeamResult) {
	fmt.Println()
	if tr.TotalMemberCount > tr.MemberCount {
		color.New(color.FgHiCyan, color.Bold).Printf(
			"═══ %s / %s (%d active / %d total, %d repos) ═══\n",
			tr.Name, tr.Domain, tr.MemberCount, tr.TotalMemberCount, tr.RepoCount,
		)
	} else {
		color.New(color.FgHiCyan, color.Bold).Printf(
			"═══ %s / %s (%d members, %d repos) ═══\n",
			tr.Name, tr.Domain, tr.MemberCount, tr.RepoCount,
		)
	}
	fmt.Println()
}

func printTeamClassification(tr team.TeamResult) {
	c := tr.Classification
	labelFmt := color.New(color.FgHiBlue, color.Bold).SprintfFunc()
	confFmt := color.New(color.FgHiBlack).SprintfFunc()

	// Character as headline
	charStr := formatCharacterLabel(c.Character)
	fmt.Printf("  %s\n", charStr)

	// 4-axis breakdown
	structStr := formatLabel(c.Structure, labelFmt, confFmt)
	cultureStr := formatLabel(c.Culture, labelFmt, confFmt)
	phaseStr := formatLabel(c.Phase, labelFmt, confFmt)
	riskStr := formatRiskLabel(c.Risk)

	fmt.Printf("  Structure: %s\n", structStr)
	fmt.Printf("  Culture:   %s\n", cultureStr)
	fmt.Printf("  Phase:     %s\n", phaseStr)
	fmt.Printf("  Risk:      %s\n\n", riskStr)
}

func formatCharacterLabel(l team.TeamLabel) string {
	if l.Name == "" || l.Name == "—" {
		return "—"
	}
	nameFmt := color.New(color.FgHiYellow, color.Bold)
	confFmt := color.New(color.FgHiBlack)
	return fmt.Sprintf("★ %s %s", nameFmt.Sprint(l.Name), confFmt.Sprintf("(%.2f)", l.Confidence))
}

func formatLabel(l team.TeamLabel, labelFmt, confFmt func(string, ...interface{}) string) string {
	if l.Name == "" || l.Name == "—" {
		return "—"
	}
	return fmt.Sprintf("%s %s", labelFmt("%s", l.Name), confFmt("(%.2f)", l.Confidence))
}

func formatRiskLabel(l team.TeamLabel) string {
	if l.Name == "" || l.Name == "—" {
		return "—"
	}
	var c *color.Color
	switch l.Name {
	case "Healthy":
		c = color.New(color.FgHiGreen, color.Bold)
	default:
		c = color.New(color.FgHiRed, color.Bold)
	}
	confFmt := color.New(color.FgHiBlack).SprintfFunc()
	return fmt.Sprintf("%s %s", c.Sprint(l.Name), confFmt("(%.2f)", l.Confidence))
}

func printAxisAverages(tr team.TeamResult) {
	color.New(color.FgWhite, color.Bold).Println("Axis Averages:")

	axes := []struct {
		name string
		val  float64
	}{
		{"Production", tr.AvgProduction},
		{"Quality", tr.AvgQuality},
		{"Survival", tr.AvgSurvival},
		{"RobustSurv", tr.AvgRobustSurvival},
		{"DormantSurv", tr.AvgDormantSurvival},
		{"Design", tr.AvgDesign},
		{"Breadth", tr.AvgBreadth},
		{"DebtCleanup", tr.AvgDebtCleanup},
		{"Indisp", tr.AvgIndispensability},
		{"Total", tr.AvgTotal},
	}

	for _, a := range axes {
		if a.val == 0 && (a.name == "RobustSurv" || a.name == "DormantSurv") {
			continue // skip pressure axes if not available
		}
		bar := renderBar(a.val, 20)
		c := scoreColor(a.val)
		fmt.Printf("  %-12s %s %s\n", a.name, bar, c.Sprintf("%.1f", a.val))
	}
	fmt.Println()
}

func printDistribution(label string, dist map[string]int, total int) {
	if len(dist) == 0 {
		return
	}

	color.New(color.FgWhite, color.Bold).Printf("%s Distribution:\n", label)

	type kv struct {
		key   string
		count int
	}
	var sorted []kv
	for k, v := range dist {
		sorted = append(sorted, kv{k, v})
	}
	sort.Slice(sorted, func(i, j int) bool { return sorted[i].count > sorted[j].count })

	for _, item := range sorted {
		pct := float64(item.count) / float64(total) * 100
		barLen := int(pct / 100 * 20)
		if barLen < 1 && item.count > 0 {
			barLen = 1
		}
		bar := color.New(color.FgHiBlue).Sprint(strings.Repeat("█", barLen)) +
			color.New(color.FgHiBlack).Sprint(strings.Repeat("░", 20-barLen))
		fmt.Printf("  %-12s %s  %d (%.0f%%)\n", item.key, bar, item.count, pct)
	}
	fmt.Println()
}

func printTeamHealth(tr team.TeamResult) {
	color.New(color.FgWhite, color.Bold).Println("Team Health:")

	h := tr.Health
	axes := []struct {
		name string
		val  float64
	}{
		{"Complement", h.Complementarity},
		{"Growth", h.GrowthPotential},
		{"Sustain", h.Sustainability},
		{"DebtBalance", h.DebtBalance},
		{"ProdDensity", h.ProductivityDensity},
		{"QualConsist", h.QualityConsistency},
	}

	for _, a := range axes {
		bar := renderBar(a.val, 20)
		c := healthColor(a.val)
		fmt.Printf("  %-12s %s %s\n", a.name, bar, c.Sprintf("%.0f/100", a.val))
	}

	// Risk ratio: inverse coloring (lower is better)
	riskBar := renderBarInverse(h.RiskRatio, 20)
	riskColor := riskLevelColor(h.RiskRatio)
	fmt.Printf("  %-12s %s %s\n", "RiskRatio", riskBar, riskColor.Sprintf("%.0f%%", h.RiskRatio))
	fmt.Println()
}

func printStructureMetrics(tr team.TeamResult) {
	h := tr.Health
	if h.AAR == 0 && h.AnchorDensity == 0 && h.ArchitectureCoverage == 0 {
		return
	}

	color.New(color.FgWhite, color.Bold).Println("Structure Metrics:")

	// AAR
	architects := tr.RoleDist["Architect"]
	anchors := tr.RoleDist["Anchor"]
	aarLabel := formatAAR(h.AAR)
	aarColor := aarScoreColor(h.AAR)
	fmt.Printf("  %-12s %s  (%d Architect / %d Anchor)\n",
		"AAR", aarColor.Sprint(aarLabel), architects, anchors)

	// Anchor Density
	densityPct := h.AnchorDensity * 100
	bar := renderBar(densityPct, 20)
	fmt.Printf("  %-12s %s %.0f%%\n", "AnchorDens", bar, densityPct)

	// Architecture Coverage
	covPct := h.ArchitectureCoverage * 100
	bar2 := renderBar(covPct, 20)
	fmt.Printf("  %-12s %s %.0f%%\n", "ArchCover", bar2, covPct)
}

func formatAAR(aar float64) string {
	if aar == 0 {
		return "N/A (no Architect)"
	}
	if aar < 0 {
		return "∞ (no Anchor)"
	}
	return fmt.Sprintf("%.2f", aar)
}

func aarScoreColor(aar float64) *color.Color {
	switch {
	case aar < 0:
		return color.New(color.FgHiRed, color.Bold) // no anchor = danger
	case aar >= 0.3 && aar <= 0.8:
		return color.New(color.FgHiGreen, color.Bold) // ideal range
	case aar > 0 && aar < 0.3:
		return color.New(color.FgHiYellow) // maintenance heavy
	case aar > 0.8 && aar <= 2.0:
		return color.New(color.FgHiYellow) // balanced-ish
	case aar > 2.0:
		return color.New(color.FgHiRed) // architecture heavy
	default:
		return color.New(color.FgWhite) // no architect
	}
}

func renderBar(val float64, width int) string {
	filled := int(val / 100 * float64(width))
	if filled > width {
		filled = width
	}
	if filled < 0 {
		filled = 0
	}
	return color.New(color.FgHiGreen).Sprint(strings.Repeat("█", filled)) +
		color.New(color.FgHiBlack).Sprint(strings.Repeat("░", width-filled))
}

func renderBarInverse(val float64, width int) string {
	filled := int(val / 100 * float64(width))
	if filled > width {
		filled = width
	}
	if filled < 0 {
		filled = 0
	}
	return color.New(color.FgHiRed).Sprint(strings.Repeat("█", filled)) +
		color.New(color.FgHiBlack).Sprint(strings.Repeat("░", width-filled))
}

func scoreColor(v float64) *color.Color {
	switch {
	case v >= 80:
		return color.New(color.FgHiMagenta, color.Bold)
	case v >= 60:
		return color.New(color.FgHiGreen, color.Bold)
	case v >= 40:
		return color.New(color.FgHiYellow)
	default:
		return color.New(color.FgWhite)
	}
}

func healthColor(v float64) *color.Color {
	switch {
	case v >= 70:
		return color.New(color.FgHiGreen, color.Bold)
	case v >= 50:
		return color.New(color.FgHiYellow)
	case v >= 30:
		return color.New(color.FgYellow)
	default:
		return color.New(color.FgHiRed)
	}
}

func riskLevelColor(v float64) *color.Color {
	switch {
	case v >= 50:
		return color.New(color.FgHiRed, color.Bold)
	case v >= 25:
		return color.New(color.FgYellow)
	default:
		return color.New(color.FgHiGreen)
	}
}
