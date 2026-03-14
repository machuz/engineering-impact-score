package output

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/machuz/engineering-impact-score/internal/timeline"
	chart "github.com/wcharczuk/go-chart/v2"
	"github.com/wcharczuk/go-chart/v2/drawing"
)

var sanitizeRe = regexp.MustCompile(`[^a-zA-Z0-9_-]+`)

func sanitizeFilename(s string) string {
	s = strings.TrimSpace(s)
	s = sanitizeRe.ReplaceAllString(s, "-")
	s = strings.Trim(s, "-")
	if s == "" {
		s = "unknown"
	}
	return s
}

// seriesConfig defines the 5 score dimensions to chart.
type seriesConfig struct {
	Name  string
	Color drawing.Color
}

var scoreSeries = []seriesConfig{
	{"Total", drawing.Color{R: 74, G: 144, B: 217, A: 255}},
	{"Production", drawing.Color{R: 80, G: 200, B: 120, A: 255}},
	{"Quality", drawing.Color{R: 255, G: 179, B: 71, A: 255}},
	{"Survival", drawing.Color{R: 155, G: 89, B: 182, A: 255}},
	{"Design", drawing.Color{R: 26, G: 188, B: 156, A: 255}},
}

// WriteTimelineSVG generates SVG chart files for each author and team timeline.
// It writes files into dir and returns the list of generated file paths.
func WriteTimelineSVG(dir string, domainTimelines []DomainTimelineData, teamTimelines []timeline.TeamTimeline) ([]string, error) {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, fmt.Errorf("create output directory: %w", err)
	}

	var generated []string

	// Author charts: one SVG per author per domain
	for _, dt := range domainTimelines {
		for _, tl := range dt.Timelines {
			if len(tl.Periods) == 0 {
				continue
			}

			fname := fmt.Sprintf("%s-%s.svg", sanitizeFilename(dt.DomainName), sanitizeFilename(tl.Author))
			fpath := filepath.Join(dir, fname)

			title := fmt.Sprintf("%s - %s", tl.Author, dt.DomainName)
			if err := writeAuthorSVG(fpath, title, tl.Periods); err != nil {
				return generated, fmt.Errorf("write SVG %s: %w", fname, err)
			}
			generated = append(generated, fpath)
		}
	}

	// Team charts: one SVG per team per domain
	for _, tl := range teamTimelines {
		if len(tl.Periods) == 0 {
			continue
		}

		fname := fmt.Sprintf("team-%s-%s.svg", sanitizeFilename(tl.TeamName), sanitizeFilename(tl.Domain))
		fpath := filepath.Join(dir, fname)

		title := fmt.Sprintf("Team %s - %s", tl.TeamName, tl.Domain)
		if err := writeTeamSVG(fpath, title, tl.Periods); err != nil {
			return generated, fmt.Errorf("write SVG %s: %w", fname, err)
		}
		generated = append(generated, fpath)
	}

	return generated, nil
}

func writeAuthorSVG(path, title string, periods []timeline.AuthorPeriod) error {
	labels := make([]string, len(periods))
	values := make([][]float64, len(scoreSeries))
	for i := range scoreSeries {
		values[i] = make([]float64, len(periods))
	}

	for i, p := range periods {
		labels[i] = p.Label
		values[0][i] = p.Total
		values[1][i] = p.Production
		values[2][i] = p.Quality
		values[3][i] = p.Survival
		values[4][i] = p.Design
	}

	return writeSVGChart(path, title, labels, values)
}

func writeTeamSVG(path, title string, periods []timeline.TeamPeriodSnapshot) error {
	labels := make([]string, len(periods))
	values := make([][]float64, len(scoreSeries))
	for i := range scoreSeries {
		values[i] = make([]float64, len(periods))
	}

	for i, p := range periods {
		labels[i] = p.Label
		values[0][i] = p.AvgTotal
		values[1][i] = p.AvgProduction
		values[2][i] = p.AvgQuality
		values[3][i] = p.AvgSurvival
		values[4][i] = p.AvgDesign
	}

	return writeSVGChart(path, title, labels, values)
}

func writeSVGChart(path, title string, labels []string, values [][]float64) error {
	n := len(labels)
	if n == 0 {
		return nil
	}

	// Build X values as indices
	xValues := make([]float64, n)
	for i := range xValues {
		xValues[i] = float64(i)
	}

	// Build custom ticks for X axis
	ticks := make([]chart.Tick, n)
	for i, label := range labels {
		ticks[i] = chart.Tick{
			Value: float64(i),
			Label: label,
		}
	}

	// Build series
	var series []chart.Series
	for si, sc := range scoreSeries {
		series = append(series, chart.ContinuousSeries{
			Name: sc.Name,
			Style: chart.Style{
				StrokeColor: sc.Color,
				StrokeWidth: 2.5,
				DotColor:    sc.Color,
				DotWidth:    4,
			},
			XValues: xValues,
			YValues: values[si],
		})
	}

	graph := chart.Chart{
		Title: title,
		TitleStyle: chart.Style{
			FontSize:  14,
			FontColor: drawing.Color{R: 51, G: 51, B: 51, A: 255},
		},
		Width:  800,
		Height: 400,
		Background: chart.Style{
			FillColor: drawing.ColorWhite,
			Padding: chart.Box{
				Top:    40,
				Left:   10,
				Right:  10,
				Bottom: 10,
			},
		},
		Canvas: chart.Style{
			FillColor: drawing.ColorWhite,
		},
		XAxis: chart.XAxis{
			Name: "Period",
			NameStyle: chart.Style{
				FontSize:  11,
				FontColor: drawing.Color{R: 102, G: 102, B: 102, A: 255},
			},
			Style: chart.Style{
				FontSize:  10,
				FontColor: drawing.Color{R: 102, G: 102, B: 102, A: 255},
			},
			Ticks: ticks,
			GridMajorStyle: chart.Style{
				StrokeColor: drawing.Color{R: 230, G: 230, B: 230, A: 255},
				StrokeWidth: 1,
			},
		},
		YAxis: chart.YAxis{
			Name: "Score",
			NameStyle: chart.Style{
				FontSize:  11,
				FontColor: drawing.Color{R: 102, G: 102, B: 102, A: 255},
			},
			Style: chart.Style{
				FontSize:  10,
				FontColor: drawing.Color{R: 102, G: 102, B: 102, A: 255},
			},
			Range: &chart.ContinuousRange{Min: 0, Max: 100},
			GridMajorStyle: chart.Style{
				StrokeColor: drawing.Color{R: 230, G: 230, B: 230, A: 255},
				StrokeWidth: 1,
			},
		},
		Series: series,
	}

	graph.Elements = []chart.Renderable{
		chart.LegendLeft(&graph, chart.Style{
			FontSize:  10,
			FontColor: drawing.Color{R: 51, G: 51, B: 51, A: 255},
			FillColor: drawing.ColorWhite,
		}),
	}

	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()

	return graph.Render(chart.SVG, f)
}
