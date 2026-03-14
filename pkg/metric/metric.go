package metric

import "github.com/machuz/engineering-impact-score/internal/metric"

type RawScores = metric.RawScores
type SurvivalResult = metric.SurvivalResult
type ChangePressure = metric.ChangePressure
type DebtData = metric.DebtData
type ModuleRisk = metric.ModuleRisk
type VerboseFunc = metric.VerboseFunc

var (
	CalcProduction           = metric.CalcProduction
	CalcQuality              = metric.CalcQuality
	CalcSurvival             = metric.CalcSurvival
	CalcSurvivalWithPressure = metric.CalcSurvivalWithPressure
	CalcDesign               = metric.CalcDesign
	CalcDebt                 = metric.CalcDebt
	CalcIndispensability     = metric.CalcIndispensability
	CalcChangePressure       = metric.CalcChangePressure
	GetFixCommits            = metric.GetFixCommits
	IsExcluded               = metric.IsExcluded
	ModuleOf                 = metric.ModuleOf
	NewRawScores             = metric.NewRawScores
)
