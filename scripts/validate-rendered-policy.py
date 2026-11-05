#!/usr/bin/env python3
"""Admission-style checks on rendered Kubernetes manifests (cluster-free)."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Any, Iterable

import yaml

WORKLOAD_KINDS = frozenset(
    {"Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob", "Service"}
)
POD_OWNER_KINDS = frozenset({"Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"})
REQUIRED_LABEL = "app.kubernetes.io/name"
PART_OF_LABEL = "app.kubernetes.io/part-of"
FLOATING_IMAGE = re.compile(r":latest([@]|$)")


def load_documents(stream: str) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for document in yaml.safe_load_all(stream):
        if document:
            documents.append(document)
    return documents


def pod_specs(document: dict[str, Any]) -> Iterable[dict[str, Any]]:
    kind = document.get("kind")
    if kind in {"Deployment", "StatefulSet", "DaemonSet"}:
        yield document["spec"]["template"]["spec"]
    elif kind == "Job":
        yield document["spec"]["template"]["spec"]
    elif kind == "CronJob":
        yield document["spec"]["jobTemplate"]["spec"]["template"]["spec"]


def check_document(document: dict[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    kind = document.get("kind")
    name = document.get("metadata", {}).get("name", "<unnamed>")

    if kind in WORKLOAD_KINDS:
        labels = document.get("metadata", {}).get("labels") or {}
        if REQUIRED_LABEL not in labels:
            errors.append(
                f"{source}: {kind}/{name} missing metadata label {REQUIRED_LABEL}"
            )
        if PART_OF_LABEL not in labels:
            errors.append(
                f"{source}: {kind}/{name} missing metadata label {PART_OF_LABEL}"
            )

    if kind == "Service":
        for port in document.get("spec", {}).get("ports") or []:
            target = port.get("targetPort")
            if target is None:
                errors.append(
                    f"{source}: Service/{name} port {port.get('name')} "
                    "must set targetPort explicitly"
                )

    if kind not in POD_OWNER_KINDS:
        return errors

    for pod_spec in pod_specs(document):
        if pod_spec.get("automountServiceAccountToken") is not False:
            errors.append(
                f"{source}: {kind}/{name} must set "
                "automountServiceAccountToken: false on the pod spec"
            )
        for container in pod_spec.get("containers") or []:
            image = container.get("image", "")
            if FLOATING_IMAGE.search(image):
                errors.append(
                    f"{source}: {kind}/{name} container {container.get('name')} "
                    f"uses a floating image tag: {image}"
                )
            resources = container.get("resources") or {}
            for scope in ("requests", "limits"):
                block = resources.get(scope) or {}
                if not block.get("cpu") or not block.get("memory"):
                    errors.append(
                        f"{source}: {kind}/{name} container {container.get('name')} "
                        f"missing resources.{scope}.cpu/memory"
                    )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="render label for error messages")
    args = parser.parse_args()

    rendered = sys.stdin.read()
    errors: list[str] = []
    for document in load_documents(rendered):
        errors.extend(check_document(document, args.source))

    if errors:
        for message in errors:
            print(message, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
