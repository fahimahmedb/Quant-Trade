"""Quant: a persistent autonomous quantitative system.

Read ``QUANT_NORTH_STAR.md`` before extending this package. The subpackages map
one-to-one onto the North-Star planes:

``quant.state``/``quant.events``/``quant.clock``   Control Plane
``quant.dataplane``                                Data Plane
``quant.factory``                                  Research Factory
``quant.desk``                                     Capital Desk
``quant.book``                                     Persistent Book
``quant.learning``                                 Learning / Memory
``quant.status``                                   Status surface (observer only)
"""

__all__ = ["clock", "events", "paths", "state"]
