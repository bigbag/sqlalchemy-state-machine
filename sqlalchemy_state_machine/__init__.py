from dataclasses import dataclass
from typing import Any, List, Optional

from transitions import Machine


@dataclass
class StateConfig:
    initial: Any
    states: List[Any]
    transitions: Optional[List[List[Any]]]
    state_attribute: Optional[str] = "state"
    status_attribute: Optional[str] = "status"
    machine_name: Optional[str] = "machine"
    after_state_change: Optional[Any] = None


@dataclass
class StateMixin:
    state_config: StateConfig

    @property
    def state(self):
        return getattr(self, self.state_config.status_attribute)

    @state.setter
    def state(self, value):
        setattr(self, self.state_config.status_attribute, value)

    @classmethod
    def init_state_machine(cls, obj, *args, **kwargs):
        machine = Machine(
            model=obj,
            states=cls.state_config.states,
            transitions=cls.state_config.transitions,
            initial=getattr(obj, obj.state_config.status_attribute) or cls.state_config.initial,
            model_attribute=cls.state_config.state_attribute,
            after_state_change=cls.state_config.after_state_change,
        )

        setattr(obj, cls.state_config.machine_name, machine)
