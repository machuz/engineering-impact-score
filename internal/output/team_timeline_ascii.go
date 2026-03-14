package output

import (
	"fmt"
	"strings"

	"github.com/fatih/color"
	"github.com/guptarohit/asciigraph"
	"github.com/machuz/engineering-impact-score/internal/timeline"
)

// PrintTeamTimelineASCII renders team timeline data as ASCII line charts.
func PrintTeamTimelineASCII(tl timeline.TeamTimeline) {
	fmt.Println()
	color.New(color.FgHiCyan, color.Bold).Printf("=== %s / %s -- Team Timeline ===\n", tl.TeamName, tl.Domain)

	// Build score average series
	avgTotalData := make([]float64, 0, len(tl.Periods))
	avgProdData := make([]float64, 0, len(tl.Periods))
	avgQualData := make([]float64, 0, len(tl.Periods))
	avgSurvData := make([]float64, 0, len(tl.Periods))
	avgDesignData := make([]float64, 0, len(tl.Periods))
	var labels []string

	for _, p := range tl.Periods {
		avgTotalData = append(avgTotalData, p.AvgTotal)
		avgProdData = append(avgProdData, p.AvgProduction)
		avgQualData = append(avgQualData, p.AvgQuality)
		avgSurvData = append(avgSurvData, p.AvgSurvival)
		avgDesignData = append(avgDesignData, p.AvgDesign)
		labels = append(labels, p.Label)
	}

	// Score averages chart
	color.New(color.FgWhite, color.Bold).Println("\nScore Averages:")

	data := [][]float64{avgTotalData, avgProdData, avgQualData, avgSurvData, avgDesignData}

	chart := asciigraph.PlotMany(data,
		asciigraph.Height(15),
		asciigraph.SeriesColors(
			asciigraph.Blue,
			asciigraph.Green,
			asciigraph.Yellow,
			asciigraph.Red,
			asciigraph.Cyan,
		),
		asciigraph.Caption(buildLabelAxis(labels)),
	)
	fmt.Println(chart)

	// Legend
	fmt.Printf("  %s  %s  %s  %s  %s\n",
		color.BlueString("AvgTotal"),
		color.GreenString("AvgProduction"),
		color.YellowString("AvgQuality"),
		color.RedString("AvgSurvival"),
		color.CyanString("AvgDesign"),
	)

	// Classification summary
	fmt.Println()
	color.New(color.FgWhite, color.Bold).Println("Classification:")
	classAxes := []struct {
		name string
		get  func(timeline.TeamPeriodSnapshot) string
	}{
		{"Character", func(p timeline.TeamPeriodSnapshot) string { return p.Character }},
		{"Structure", func(p timeline.TeamPeriodSnapshot) string { return p.Structure }},
		{"Culture", func(p timeline.TeamPeriodSnapshot) string { return p.Culture }},
		{"Phase", func(p timeline.TeamPeriodSnapshot) string { return p.Phase }},
		{"Risk", func(p timeline.TeamPeriodSnapshot) string { return p.Risk }},
	}
	for _, ax := range classAxes {
		var vals []string
		for _, p := range tl.Periods {
			v := ax.get(p)
			if v == "" {
				v = "-"
			}
			vals = append(vals, v)
		}
		fmt.Printf("  %-12s %s\n", ax.name+":", strings.Join(vals, " -> "))
	}

	// Transitions
	if len(tl.Transitions) > 0 {
		fmt.Println()
		color.New(color.FgWhite, color.Bold).Println("Transitions:")
		for _, t := range tl.Transitions {
			fmt.Printf("  [%s] %s: %s %s %s\n",
				t.AtPeriod, t.Axis, t.From,
				color.HiYellowString("->"),
				t.To,
			)
		}
	}

	fmt.Println()
}
