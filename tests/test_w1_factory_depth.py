"""Expose Wave-1 Factory regression tests to the repository's top-level CI discovery."""

from research.research_os.tests.test_w1_factory_economic_integration import W1FactoryEconomicIntegrationTests
from research.research_os.tests.test_w1_factory_experiment_bridge import BridgeTests
from research.research_os.tests.test_w1_factory_experiment_infrastructure import (
    OutcomeFirewallTests,
    PowerGeometryTests,
    RegistryBindingTests,
)
from research.research_os.tests.test_w1_factory_firewall_hardening import FirewallHardeningTests

__all__ = [
    "RegistryBindingTests",
    "PowerGeometryTests",
    "OutcomeFirewallTests",
    "BridgeTests",
    "W1FactoryEconomicIntegrationTests",
    "FirewallHardeningTests",
]
