"""Fit a small legal-masked draft head on disjoint GameVersion 58 rounds.

The replay extractor preserves the draft clock, but BASIC cannot read it and
all commanded examples in the initial dataset have the full clock remaining.
This trainer therefore uses only the first 32, live-observable features.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

N_CLASSES = 10
N_FEATURES = 32


def load_examples(paths: list[Path], expert_ids: set[str]) -> list[dict]:
    examples = [row for path in paths for row in json.loads(path.read_text())]
    selected = [row for row in examples if row["player_id"] in expert_ids]
    for row in selected:
        if len(row["features"]) != 33 or len(row["legal_mask"]) != N_CLASSES:
            raise ValueError("expected the exact v58 draft-example schema")
        if row["legal_mask"][row["choice"]] != 1:
            raise ValueError("observed choice is illegal")
    return selected


def arrays(examples: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([row["features"][:N_FEATURES] for row in examples], dtype=float),
        np.asarray([row["legal_mask"] for row in examples], dtype=bool),
        np.asarray([row["choice"] for row in examples], dtype=int),
    )


def probabilities(x: np.ndarray, mask: np.ndarray, weights: np.ndarray) -> np.ndarray:
    logits = x @ weights[:-1] + weights[-1]
    logits = np.where(mask, logits, -1e9)
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(shifted) * mask
    return exp / exp.sum(axis=1, keepdims=True)


def metrics(probs: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    return {
        "top1": float(np.mean(np.argmax(probs, axis=1) == labels)),
        "nll": float(
            np.mean(-np.log(np.maximum(probs[np.arange(len(labels)), labels], 1e-12)))
        ),
    }


def train(
    train_rows: list[dict],
    validation_rows: list[dict],
    *,
    learning_rate: float = 0.25,
    l2: float = 0.001,
    epochs: int = 2000,
) -> tuple[np.ndarray, dict]:
    if not train_rows or not validation_rows:
        raise ValueError("both train and held-out validation examples are required")
    x, mask, labels = arrays(train_rows)
    vx, vmask, vlabels = arrays(validation_rows)
    design = np.column_stack((x, np.ones(len(x))))
    weights = np.zeros((N_FEATURES + 1, N_CLASSES), dtype=float)
    best_weights = weights.copy()
    best_epoch = 0
    best_nll = float("inf")
    for epoch in range(1, epochs + 1):
        probs = probabilities(x, mask, weights)
        grad = probs.copy()
        grad[np.arange(len(labels)), labels] -= 1
        weights -= learning_rate * (design.T @ grad / len(labels) + l2 * weights)
        if epoch % 25 == 0 or epoch == epochs:
            score = metrics(probabilities(vx, vmask, weights), vlabels)["nll"]
            if score < best_nll:
                best_nll, best_epoch, best_weights = score, epoch, weights.copy()

    counts = np.bincount(labels, minlength=N_CLASSES).astype(float) + 1
    baseline = np.broadcast_to(counts, vmask.shape) * vmask
    baseline /= baseline.sum(axis=1, keepdims=True)
    report = {
        "schema": "gota-v58-draft-observable-32-v1",
        "train_examples": len(train_rows),
        "validation_examples": len(validation_rows),
        "best_epoch_by_validation_nll": best_epoch,
        "baseline": metrics(baseline, vlabels),
        "draft_head": metrics(probabilities(vx, vmask, best_weights), vlabels),
        "train": metrics(probabilities(x, mask, best_weights), labels),
    }
    return best_weights, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, nargs="+", required=True)
    parser.add_argument("--validation", type=Path, nargs="+", required=True)
    parser.add_argument("--leaderboard", type=Path, required=True)
    parser.add_argument("--expert-count", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    leaders = json.loads(args.leaderboard.read_text())["top"]
    expert_ids = {row["player_id"] for row in leaders[: args.expert_count]}
    train_rows = load_examples(args.train, expert_ids)
    validation_rows = load_examples(args.validation, expert_ids)
    train_episodes = {row["source_episode_id"] for row in train_rows}
    validation_episodes = {row["source_episode_id"] for row in validation_rows}
    if train_episodes & validation_episodes:
        raise ValueError("training and validation share an episode")
    weights, report = train(train_rows, validation_rows)
    report.update(
        {
            "expert_player_ids": sorted(expert_ids),
            "train_files": [str(path) for path in args.train],
            "validation_files": [str(path) for path in args.validation],
            "train_episode_count": len(train_episodes),
            "validation_episode_count": len(validation_episodes),
        }
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez(args.output, weights=weights, schema=report["schema"])
    report_path = args.output.with_suffix(".json")
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
