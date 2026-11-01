"""Strategy registry (ROADMAP.md chapter 36).

Provides a centralized registry for strategy discovery, metadata,
and version management.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Type

from crypto_trading_lab.backtesting.engine import Strategy
from crypto_trading_lab.complexity_control import (
    StrategyComplexity,
    strategy_complexity_from_schema,
)
from crypto_trading_lab.strategy_parameters import (
    CombinationRule,
    ParameterError,
    ParameterSchema,
    ParameterSet,
)
from crypto_trading_lab.strategy_identity import IDENTITIES, StrategyIdentity


@dataclass(frozen=True)
class StrategyMetadata:
    """Metadata for a registered strategy (36.1)."""
    strategy_id: str
    name: str
    version: str
    author: str
    description: str
    created_at: datetime
    updated_at: datetime
    parameters_schema: Dict[str, Dict[str, Any]]
    tags: Set[str] = field(default_factory=set)
    dependencies: Set[str] = field(default_factory=set)
    min_data_requirements: Dict[str, Any] = field(default_factory=dict)
    #: Chapter 35 metrics, recorded per strategy version. ``None`` only for
    #: entries imported from a file written before the field existed.
    complexity: Optional[StrategyComplexity] = None
    #: Chapter 33.4: the typed, validated view of ``parameters_schema``.
    #: Its combination rules are Python callables, so they do not survive a
    #: JSON round trip; an imported entry is validated parameter by parameter
    #: only (see ``StrategyRegistry._load``).
    parameter_schema: Optional[ParameterSchema] = None
    #: Chapter 33.1: which kind of strategy this is (trend-following,
    #: mean-reversion, breakout, benchmark, baseline). Empty only for an entry
    #: imported from a file written before the field existed.
    category: str = ""


@dataclass
class StrategyRegistration:
    """Complete strategy registration record."""
    metadata: StrategyMetadata
    factory: Callable[..., Strategy]
    source_path: Optional[str] = None
    is_builtin: bool = False


def _fast_below_slow(values: Dict[str, Any]) -> Optional[str]:
    if values["fast"] >= values["slow"]:
        return (
            "fast must be smaller than slow; with fast >= slow the "
            "'fast' average is not faster and the crossover means nothing"
        )
    return None


def _oversold_below_overbought(values: Dict[str, Any]) -> Optional[str]:
    if values["oversold"] >= values["overbought"]:
        return (
            "oversold must be smaller than overbought; otherwise the entry "
            "and exit thresholds are inverted and every signal fires at once"
        )
    return None


#: The chapter 33.4 checks that no single parameter can express.
fast_below_slow = CombinationRule("fast < slow", _fast_below_slow)
oversold_below_overbought = CombinationRule(
    "oversold < overbought", _oversold_below_overbought
)


def _typed_schema_or_none(
    parameters_schema: Dict[str, Dict[str, Any]]
) -> Optional[ParameterSchema]:
    """The typed schema, or ``None`` when the stored one cannot be typed.

    A schema stored before chapter 33.4 may have no ``default``, which the
    typed model rejects by design (a parameter must declare one). Refusing to
    load the whole registry over that would be worse than falling back to the
    strategy's own checks, so the fallback is explicit here.
    """
    try:
        return ParameterSchema.from_mapping(parameters_schema)
    except ParameterError:
        return None


class StrategyRegistry:
    """
    Central registry for strategy management (Chapter 36).

    Provides:
    - Strategy discovery and registration
    - Version management
    - Parameter schema validation
    - Dependency tracking
    - Search and filtering
    """

    def __init__(self, storage_path: Optional[Path] = None, load: bool = True):
        self._strategies: Dict[str, StrategyRegistration] = {}
        self._storage_path = storage_path or Path.cwd() / "data" / "strategy_registry"
        # Building a registry is a read-only operation. The directory and the
        # JSON file are created only when something is actually mutated (see
        # `_save`). Before this guard, merely constructing the registry wrote
        # `data/strategy_registry/registry.json` into whatever directory the
        # process happened to be started from — including the source tree.
        self._persist = False
        self._load_builtin_strategies()
        if load:
            self._load()
        self._persist = True

    def _load_builtin_strategies(self) -> None:
        """Register built-in strategies."""
        from crypto_trading_lab.backtesting.engine import (
            MACrossoverStrategy, BuyAndHoldStrategy, NullStrategy, RSIStrategy, RollingHighLowBreakoutStrategy, BollingerBandsMeanReversionStrategy
        )

        builtins = [
            ("ma_crossover", MACrossoverStrategy, {
                "fast": {"type": "int", "min": 1, "max": 200, "default": 10, "description": "Fast SMA period"},
                "slow": {"type": "int", "min": 1, "max": 500, "default": 30, "description": "Slow SMA period"},
            }, {"rules": 2, "indicators": 2, "filters": 0, "conditions": 2},
             (fast_below_slow,)),
            ("buy_and_hold", BuyAndHoldStrategy, {},
             {"rules": 1, "indicators": 0, "filters": 0, "conditions": 0},
             ()),
            ("null_strategy", NullStrategy, {},
             {"rules": 0, "indicators": 0, "filters": 0, "conditions": 0},
             ()),
            ("rsi", RSIStrategy, {"period": {"type": "int", "min": 1, "max": 200, "default": 14, "description": "RSI period"}, "oversold": {"type": "int", "min": 1, "max": 99, "default": 30, "description": "Oversold level"}, "overbought": {"type": "int", "min": 2, "max": 99, "default": 70, "description": "Overbought level"}, "volume_filter_period": {"type": "int", "min": 0, "max": 200, "default": 0, "description": "Volume-filter SMA period (0 disables)"}, "trend_filter_period": {"type": "int", "min": 0, "max": 500, "default": 0, "description": "Trend-filter SMA period (0 disables)"}, "cooldown": {"type": "int", "min": 0, "max": 500, "default": 0, "description": "Candles to wait after an exit"}},
             # RSI + the volume average + the trend average; three filters:
             # volume, trend and the cooldown after an exit.
             {"rules": 2, "indicators": 3, "filters": 3, "conditions": 2},
             (oversold_below_overbought,)),
            ("breakout", RollingHighLowBreakoutStrategy, {"period": {"type": "int", "min": 2, "max": 500, "default": 20, "description": "Lookback bars for the rolling range"}},
             {"rules": 2, "indicators": 2, "filters": 0, "conditions": 2},
             ()),
            ("bollinger", BollingerBandsMeanReversionStrategy, {"period": {"type": "int", "min": 1, "max": 500, "default": 20, "description": "Bollinger SMA period"}, "k": {"type": "int", "min": 1, "max": 10, "default": 2, "description": "Number of standard deviations"}},
             {"rules": 2, "indicators": 3, "filters": 0, "conditions": 2},
             ()),
        ]

        for strategy_id, factory, params, structure, rules in builtins:
            # Chapter 33.1: name, version, author, description and category
            # come from the identity record, so the registry cannot invent a
            # name from the identifier ("ma_crossover" used to become
            # "Ma Crossover") or disagree with the docs.
            identity = IDENTITIES[strategy_id]
            self.register(
                strategy_id=strategy_id,
                factory=factory,
                name=identity.name,
                version=identity.version,
                author=identity.author,
                description=identity.description,
                category=identity.category,
                parameters_schema=params,
                structure=structure,
                combination_rules=rules,
                is_builtin=True,
            )

    def register(
        self,
        strategy_id: str,
        factory: Callable[..., Strategy],
        name: str,
        version: str,
        author: str,
        description: str,
        parameters_schema: Dict[str, Dict[str, Any]],
        tags: Set[str] = None,
        dependencies: Set[str] = None,
        min_data_requirements: Dict[str, Any] = None,
        source_path: str = None,
        is_builtin: bool = False,
        structure: Optional[Dict[str, int]] = None,
        combination_rules: Sequence[CombinationRule] = (),
        category: str = "",
    ) -> StrategyRegistration:
        """Register a new strategy.

        ``structure`` declares the counts chapter 35 asks for and that a
        parameter schema cannot express (rules, indicators, filters,
        conditions); the parameter count and the size of the parameter grid
        are derived from the schema itself. A strategy that declares nothing
        still gets a truthful record — with zeros where it declared nothing.

        ``combination_rules`` are the chapter 33.4 checks no single parameter
        can express (``fast < slow``). They run in :meth:`create_instance`,
        before the strategy is built.

        ``category`` is the chapter 33.1 classification. It is optional for
        strategies registered from code outside this package, which may not
        have been classified yet; the built-ins always declare one.
        """
        if strategy_id in self._strategies and self._strategies[strategy_id].metadata.is_builtin:
            raise ValueError(f"Cannot overwrite built-in strategy: {strategy_id}")

        parameter_schema = ParameterSchema.from_mapping(
            parameters_schema, rules=combination_rules
        )

        declared = dict(structure or {})
        complexity = strategy_complexity_from_schema(
            parameters_schema,
            rules=int(declared.get("rules", 0)),
            indicators=int(declared.get("indicators", 0)),
            filters=int(declared.get("filters", 0)),
            conditions=int(declared.get("conditions", 0)),
            model_complexity=int(declared.get("model_complexity", 0)),
            version=version,
        )

        now = datetime.now(timezone.utc)
        metadata = StrategyMetadata(
            strategy_id=strategy_id,
            name=name,
            version=version,
            author=author,
            description=description,
            tags=tags or set(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            parameters_schema=parameters_schema,
            dependencies=dependencies or set(),
            min_data_requirements=min_data_requirements or {},
            complexity=complexity,
            parameter_schema=parameter_schema,
            category=category,
        )

        registration = StrategyRegistration(
            metadata=metadata,
            factory=factory,
            source_path=source_path,
            is_builtin=is_builtin,
        )

        self._strategies[strategy_id] = registration
        self._save()
        return registration

    def get(self, strategy_id: str) -> Optional[StrategyRegistration]:
        """Get strategy by ID."""
        return self._strategies.get(strategy_id)

    def get_factory(self, strategy_id: str) -> Optional[Callable[..., Strategy]]:
        """Get strategy factory by ID."""
        reg = self._strategies.get(strategy_id)
        return reg.factory if reg else None

    def list_strategies(self, tags: Set[str] = None, author: str = None) -> List[StrategyMetadata]:
        """List strategies with optional filters."""
        results = []
        for reg in self._strategies.values():
            if tags and not tags.issubset(reg.metadata.tags):
                continue
            if author and reg.metadata.author != author:
                continue
            results.append(reg.metadata)
        return results

    def search(self, query: str) -> List[StrategyMetadata]:
        """Search strategies by name, description, or tags."""
        query_lower = query.lower()
        results = []
        for reg in self._strategies.values():
            if (query_lower in reg.metadata.name.lower() or
                query_lower in reg.metadata.description.lower() or
                any(query_lower in tag.lower() for tag in reg.metadata.tags)):
                results.append(reg.metadata)
        return results

    def create_instance(self, strategy_id: str, **params) -> Optional[Strategy]:
        """Create a strategy instance with parameters.

        Parameters are validated against the chapter 33.4 schema first —
        types are coerced, bounds are checked and invalid combinations are
        rejected — so a strategy never starts with values it cannot run.
        Missing parameters take their declared default.
        """
        factory = self.get_factory(strategy_id)
        if not factory:
            return None
        registration = self._strategies.get(strategy_id)
        schema = registration.metadata.parameter_schema if registration else None
        if schema is not None:
            params = schema.validate(params)
        return factory(**params)

    def parameter_set(
        self, strategy_id: str, **params
    ) -> Optional[ParameterSet]:
        """The validated, frozen parameters for a strategy version.

        The same gate :meth:`create_instance` uses, returned as an object
        whose ``signature()`` records exactly what ran (chapter 33.4).
        """
        registration = self._strategies.get(strategy_id)
        if registration is None:
            return None
        schema = registration.metadata.parameter_schema
        values = schema.validate(params) if schema is not None else dict(params)
        return ParameterSet(
            strategy_id=strategy_id,
            version=registration.metadata.version,
            values=values,
        )

    def update_metadata(self, strategy_id: str, **kwargs) -> bool:
        """Update strategy metadata."""
        reg = self._strategies.get(strategy_id)
        if not reg or reg.is_builtin:
            return False

        metadata = reg.metadata
        updates = {k: v for k, v in kwargs.items() if hasattr(metadata, k)}
        if not updates:
            return False

        # A new version may change the parameters, so the chapter 35 record
        # is recomputed: the structural counts it already declared are kept,
        # the parameter count, the grid and the version follow the update.
        schema = updates.get("parameters_schema", metadata.parameters_schema)
        version = updates.get("version", metadata.version)
        previous = metadata.complexity
        complexity = strategy_complexity_from_schema(
            schema,
            rules=previous.num_rules if previous else 0,
            indicators=previous.num_indicators if previous else 0,
            filters=previous.num_filters if previous else 0,
            conditions=previous.num_conditions if previous else 0,
            model_complexity=previous.model_complexity if previous else 0,
            version=version,
        )

        new_metadata = StrategyMetadata(
            strategy_id=metadata.strategy_id,
            name=updates.get("name", metadata.name),
            version=version,
            author=updates.get("author", metadata.author),
            description=updates.get("description", metadata.description),
            tags=updates.get("tags", metadata.tags),
            created_at=metadata.created_at,
            updated_at=datetime.now(timezone.utc),
            parameters_schema=schema,
            dependencies=updates.get("dependencies", metadata.dependencies),
            min_data_requirements=updates.get("min_data_requirements", metadata.min_data_requirements),
            complexity=complexity,
            parameter_schema=ParameterSchema.from_mapping(
                schema,
                rules=(
                    metadata.parameter_schema.rules
                    if metadata.parameter_schema is not None
                    else ()
                ),
            ),
            category=updates.get("category", metadata.category),
        )

        self._strategies[strategy_id] = StrategyRegistration(
            metadata=new_metadata,
            factory=reg.factory,
            source_path=reg.source_path,
            is_builtin=reg.is_builtin,
        )
        self._save()
        return True

    def unregister(self, strategy_id: str) -> bool:
        """Unregister a strategy (not builtin)."""
        reg = self._strategies.get(strategy_id)
        if not reg or reg.is_builtin:
            return False

        del self._strategies[strategy_id]
        self._save()
        return True

    def export_registry(self, path: Path) -> None:
        """Export registry to JSON file."""
        data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "strategies": []
        }
        for reg in self._strategies.values():
            data["strategies"].append({
                "metadata": {
                    "strategy_id": reg.metadata.strategy_id,
                    "name": reg.metadata.name,
                    "version": reg.metadata.version,
                    "author": reg.metadata.author,
                    "description": reg.metadata.description,
                    "category": reg.metadata.category,
                    "tags": list(reg.metadata.tags),
                    "created_at": reg.metadata.created_at.isoformat(),
                    "updated_at": reg.metadata.updated_at.isoformat(),
                    "parameters_schema": reg.metadata.parameters_schema,
                    "dependencies": list(reg.metadata.dependencies),
                    "min_data_requirements": reg.metadata.min_data_requirements,
                    "complexity": (
                        reg.metadata.complexity.to_dict()
                        if reg.metadata.complexity is not None
                        else None
                    ),
                },
                "is_builtin": reg.is_builtin,
                "source_path": reg.source_path,
            })
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def import_registry(self, path: Path) -> int:
        """Import strategies from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        for item in data.get("strategies", []):
            meta = item["metadata"]
            # Skip if builtin (can't overwrite)
            if self._strategies.get(meta["strategy_id"], None) and \
               self._strategies[meta["strategy_id"]].is_builtin:
                continue

            metadata = StrategyMetadata(
                strategy_id=meta["strategy_id"],
                name=meta["name"],
                version=meta["version"],
                author=meta["author"],
                description=meta["description"],
                tags=set(meta["tags"]),
                created_at=datetime.fromisoformat(meta["created_at"]),
                updated_at=datetime.fromisoformat(meta["updated_at"]),
                parameters_schema=meta["parameters_schema"],
                dependencies=set(meta["dependencies"]),
                min_data_requirements=meta["min_data_requirements"],
                complexity=(
                    StrategyComplexity.from_dict(meta["complexity"])
                    if meta.get("complexity")
                    else None
                ),
                # Combination rules are callables and JSON cannot carry them,
                # so an imported strategy is validated parameter by parameter
                # until the code that owns it registers it again. A stored
                # schema that declares no default (an older or hand-edited
                # file) cannot become a typed schema at all: it keeps
                # `parameter_schema=None` and the strategy's own checks apply,
                # instead of failing to load the whole registry.
                parameter_schema=_typed_schema_or_none(
                    meta["parameters_schema"]
                ),
                # A file written before chapter 33.1 has no category; an
                # empty one means "not classified", which is the truth.
                category=meta.get("category", ""),
            )
            # Note: factory not restored from JSON - must be re-registered
            self._strategies[meta["strategy_id"]] = StrategyRegistration(
                metadata=metadata,
                factory=None,
                source_path=item.get("source_path"),
                is_builtin=False,
            )
            count += 1
        self._save()
        return count

    def _save(self) -> None:
        """Save registry to disk.

        Does nothing while the registry is being built, so that constructing
        one never touches the filesystem.
        """
        if not self._persist or not self._storage_path:
            return
        path = self._storage_path / "registry.json"
        self.export_registry(path)

    def _load(self) -> None:
        """Load registry from disk.

        Built-in strategies keep the factories bound by
        `_load_builtin_strategies` (they are skipped on import). Strategies
        that were registered by other code come back as metadata only: a
        factory is a live Python callable and JSON cannot carry it, so
        `get_factory` returns ``None`` for them until the code that owns the
        strategy registers it again. `list_strategies` still reports them;
        callers that need to *run* one must check `get_factory` first.
        """
        path = self._storage_path / "registry.json"
        if not path.exists():
            return
        self.import_registry(path)


STRATEGY_REGISTRY_WARNING = (
    "Strategy registry manages strategy metadata and discovery. "
    "Strategy implementations must be registered separately with their factories. "
    "Built-in strategies cannot be overwritten."
)


__all__ = [
    "StrategyMetadata",
    "StrategyRegistration",
    "StrategyRegistry",
    "STRATEGY_REGISTRY_WARNING",
]
