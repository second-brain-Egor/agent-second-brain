#!/usr/bin/env python3
"""Бэктест возврата DASH к 60-секундной средней на секундных OHLC-барах."""

from __future__ import annotations

import argparse
import gzip
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class Params:
    band_pct: float
    retrace: float
    stop_extra_pct: float
    hold_sec: int


def read_ticks(path: Path) -> pd.DataFrame:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as source:
        frame = pd.read_csv(source, usecols=["timestamp_ms", "price", "quantity"])
    frame["second"] = frame["timestamp_ms"] // 1000
    frame["notional"] = frame["price"] * frame["quantity"]
    bars = frame.groupby("second", sort=True).agg(
        open=("price", "first"), high=("price", "max"), low=("price", "min"),
        close=("price", "last"), volume=("quantity", "sum"), notional=("notional", "sum")
    )
    return bars.reset_index()


def simulate(bars: pd.DataFrame, p: Params, cost_pct: float) -> dict:
    window: deque[tuple[int, float, float]] = deque()
    sum_volume = 0.0
    sum_notional = 0.0
    center = upper = lower = None
    last_calc = -10**18
    position = None
    trades = []

    for row in bars.itertuples(index=False):
        second = int(row.second)
        volume = float(row.volume)
        notional = float(row.notional)
        window.append((second, volume, notional))
        sum_volume += volume
        sum_notional += notional
        while window and window[0][0] < second - 59:
            _, old_volume, old_notional = window.popleft()
            sum_volume -= old_volume
            sum_notional -= old_notional

        # Центр для текущей секунды считаем только по уже завершённым секундам:
        # текущие high/low/close ещё не могли быть известны при выставлении ордера.
        prior_volume = sum_volume - volume
        prior_notional = sum_notional - notional
        if position is None and second - last_calc >= 5 and len(window) >= 31 and prior_volume > 0:
            new_center = prior_notional / prior_volume
            if center is None or abs(new_center / center - 1) >= 0.0015:
                center = new_center
                upper = center * (1 + p.band_pct / 100)
                lower = center * (1 - p.band_pct / 100)
            last_calc = second

        if position is None and center is not None:
            hit_long = row.low <= lower
            hit_short = row.high >= upper
            if hit_long and hit_short:
                continue  # порядок внутри секунды неизвестен — неоднозначную свечу пропускаем
            if hit_long:
                entry = lower
                position = {
                    "side": "long", "entry": entry, "entry_second": second,
                    "target": entry + (center - entry) * p.retrace,
                    "stop": entry * (1 - p.stop_extra_pct / 100),
                }
            elif hit_short:
                entry = upper
                position = {
                    "side": "short", "entry": entry, "entry_second": second,
                    "target": entry - (entry - center) * p.retrace,
                    "stop": entry * (1 + p.stop_extra_pct / 100),
                }
            continue

        if position is None:
            continue

        side = position["side"]
        age = second - position["entry_second"]
        if side == "long":
            stop_hit = row.low <= position["stop"]
            target_hit = row.high >= position["target"]
        else:
            stop_hit = row.high >= position["stop"]
            target_hit = row.low <= position["target"]

        reason = exit_price = None
        if stop_hit:  # консервативно: при двух касаниях внутри секунды сначала стоп
            reason, exit_price = "stop", position["stop"]
        elif target_hit:
            reason, exit_price = "target", position["target"]
        elif age >= p.hold_sec:
            reason, exit_price = "time", float(row.close)

        if reason:
            gross = ((exit_price / position["entry"] - 1) if side == "long"
                     else (position["entry"] / exit_price - 1)) * 100
            net = gross - cost_pct
            trades.append((second, side, reason, gross, net))
            position = None
            center = upper = lower = None
            last_calc = second

    if not trades:
        return {"trades": 0, "win_rate": 0, "net_sum": 0, "net_avg": 0, "profit_factor": 0,
                "targets": 0, "stops": 0, "timeouts": 0, "max_drawdown": 0}
    result = pd.DataFrame(trades, columns=["second", "side", "reason", "gross", "net"])
    equity = result["net"].cumsum()
    drawdown = equity - equity.cummax().clip(lower=0)
    gains = result.loc[result.net > 0, "net"].sum()
    losses = -result.loc[result.net < 0, "net"].sum()
    return {
        "trades": len(result), "win_rate": (result.net > 0).mean() * 100,
        "net_sum": result.net.sum(), "net_avg": result.net.mean(),
        "profit_factor": gains / losses if losses else 999.0,
        "targets": (result.reason == "target").sum(), "stops": (result.reason == "stop").sum(),
        "timeouts": (result.reason == "time").sum(), "max_drawdown": drawdown.min(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--cost-pct", type=float, default=0.10,
                        help="Комиссии и проскальзывание за полный круг, в процентах")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    paths = sorted(list(args.data_dir.glob("trades_*.csv")) + list(args.data_dir.glob("trades_*.csv.gz")))
    paths = [path for path in paths if args.start <= path.name[7:17] <= args.end]
    if not paths:
        raise SystemExit("Нет файлов за выбранный период")
    bars = pd.concat([read_ticks(path) for path in paths], ignore_index=True).sort_values("second")

    # Небольшой целевой перебор: меняем по одному параметру вокруг базы и
    # добавляем разумные сочетания. Это быстрее полного декартова перебора и
    # снижает риск выбрать случайно переоптимизированный вариант.
    base = Params(0.8, 0.5, 0.8, 60)
    candidates = {base}
    for band in (0.5, 0.6, 0.8, 1.0, 1.2):
        candidates.add(Params(band, 0.5, 0.8, 60))
    for retrace in (0.25, 0.5, 0.75, 1.0):
        candidates.add(Params(0.8, retrace, 0.8, 60))
    for stop_extra in (0.4, 0.6, 0.8, 1.0):
        candidates.add(Params(0.8, 0.5, stop_extra, 60))
    for hold in (30, 60, 120):
        candidates.add(Params(0.8, 0.5, 0.8, hold))
    for band in (0.6, 1.0):
        for retrace in (0.25, 0.75):
            for stop_extra in (0.6, 1.0):
                candidates.add(Params(band, retrace, stop_extra, 60))
    variants = [{**params.__dict__, **simulate(bars, params, args.cost_pct)}
                for params in sorted(candidates, key=lambda x: tuple(x.__dict__.values()))]
    results = pd.DataFrame(variants).sort_values(["net_sum", "profit_factor"], ascending=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False)
    print(f"Период: {args.start} — {args.end}; секундных баров: {len(bars):,}; вариантов: {len(results)}")
    print(results.head(20).to_string(index=False))
    baseline = results[(results.band_pct == 0.8) & (results.retrace == 0.5) &
                       (results.stop_extra_pct == 0.8) & (results.hold_sec == 60)]
    print("\nБазовый вариант:\n" + baseline.to_string(index=False))


if __name__ == "__main__":
    main()
