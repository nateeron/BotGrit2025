import type { LineData, UTCTimestamp } from 'lightweight-charts'
import type { OhlcPoint } from '../services/api'

const toLineData = (
  data: number[],
  points: OhlcPoint[],
  offset: number,
): LineData<UTCTimestamp>[] =>
  data.map((value, idx) => ({
    time: points[idx + offset].time,
    value: Number(value.toFixed(4)),
  }))

export const calculateSMA = (
  data: OhlcPoint[],
  period: number,
): LineData<UTCTimestamp>[] => {
  if (period <= 1 || data.length < period) return []
  const result: number[] = []
  let sum = 0
  for (let i = 0; i < data.length; i += 1) {
    sum += data[i].close
    if (i >= period) {
      sum -= data[i - period].close
    }
    if (i >= period - 1) {
      result.push(sum / period)
    }
  }
  return toLineData(result, data, period - 1)
}

export const calculateEMA = (
  data: OhlcPoint[],
  period: number,
): LineData<UTCTimestamp>[] => {
  if (period <= 1 || data.length < period) return []
  const k = 2 / (period + 1)
  let ema = data
    .slice(0, period)
    .reduce((sum, item) => sum + item.close, 0) / period
  const values: number[] = [ema]
  for (let i = period; i < data.length; i += 1) {
    ema = data[i].close * k + ema * (1 - k)
    values.push(ema)
  }
  return toLineData(values, data, period - 1)
}

export const calculateBollingerBands = (
  data: OhlcPoint[],
  period: number,
  stdDev: number,
) => {
  if (period <= 1 || data.length < period) {
    return { upper: [], middle: [], lower: [] }
  }
  const middleRaw: number[] = []
  const stdRaw: number[] = []
  for (let i = 0; i <= data.length - period; i += 1) {
    const window = data.slice(i, i + period)
    const mean = window.reduce((sum, candle) => sum + candle.close, 0) / period
    const variance =
      window.reduce((sum, candle) => sum + (candle.close - mean) ** 2, 0) /
      period
    middleRaw.push(mean)
    stdRaw.push(Math.sqrt(variance))
  }
  const upper = middleRaw.map((value, idx) => value + stdRaw[idx] * stdDev)
  const lower = middleRaw.map((value, idx) => value - stdRaw[idx] * stdDev)
  return {
    upper: toLineData(upper, data, period - 1),
    middle: toLineData(middleRaw, data, period - 1),
    lower: toLineData(lower, data, period - 1),
  }
}

export const calculateRSI = (
  data: OhlcPoint[],
  period: number,
): LineData<UTCTimestamp>[] => {
  if (period <= 1 || data.length < period + 1) return []
  let gains = 0
  let losses = 0
  for (let i = 1; i <= period; i += 1) {
    const diff = data[i].close - data[i - 1].close
    if (diff >= 0) gains += diff
    else losses -= diff
  }
  gains /= period
  losses /= period
  const result: number[] = []
  const calcRS = (avgGain: number, avgLoss: number) =>
    avgLoss === 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss)

  result.push(calcRS(gains, losses))
  for (let i = period + 1; i < data.length; i += 1) {
    const diff = data[i].close - data[i - 1].close
    const gain = diff > 0 ? diff : 0
    const loss = diff < 0 ? -diff : 0
    gains = (gains * (period - 1) + gain) / period
    losses = (losses * (period - 1) + loss) / period
    result.push(calcRS(gains, losses))
  }
  return toLineData(result, data, period)
}

