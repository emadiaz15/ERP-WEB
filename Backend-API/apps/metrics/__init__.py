__all__ = ["MetricParameter"]


def __getattr__(name: str):
	if name == "MetricParameter":
		from .models import MetricParameter  # Lazy import to avoid app loading side-effects
		return MetricParameter
	raise AttributeError(f"module 'apps.metrics' has no attribute '{name}'")
