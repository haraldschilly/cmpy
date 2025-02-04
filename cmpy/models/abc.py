# coding: utf-8
#
# This code is part of cmpy.
#
# Copyright (c) 2022, Dylan Jones

"""Base objects for condensed matter models."""

import json
from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import MutableMapping
from typing import Any, Dict, Optional, List, Iterator
from cmpy.basis import Basis, SpinBasis
from cmpy.operators import HamiltonOperator


class ModelParameters(MutableMapping):
    """Parameter class for storing parameters of physical models.

    The parameters can be accessed as attributes or dict-entries.
    This class is usually used as a base-class for model-classes.
    """

    def __init__(self, **params):
        """Initializes the ModelParameters-instance.

        Parameters
        ----------
        **params: Initial parameters.
        """
        MutableMapping.__init__(self)
        self.__params__ = OrderedDict(params)

    @property
    def params(self) -> Dict[str, Any]:
        """dict: Returns a dictionary of all parameters."""
        return self.__params__

    def set_param(self, key: str, value: Any) -> None:
        """Sets a parameter

        Parameters
        ----------
        key: str
            The name of the parameter.
        value: Any
            The value of the parameter.
        """
        self.__params__[key] = value

    def delete_param(self, key: str) -> None:
        """Deletes a parameter with the given name

        Parameters
        ----------
        key: str
            The name of the parameter to delete.
        """
        del self.__params__[key]

    def rename_param(self, key: str, new_key: str) -> None:
        """Renames an existing parameter.

        Parameters
        ----------
        key: str
            The current name of the parameter.
        new_key: str
            The new name of the parameter.
        """
        self.__params__[new_key] = self.__params__[key]
        del self.__params__[key]

    def __len__(self) -> int:
        """Number of parameters."""
        return len(self.__params__)

    def __getitem__(self, key: str) -> Any:
        """Make parameters accessable as dictionary items."""
        return self.__params__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Make parameters accessable as dictionary items."""
        self.__params__[key] = value

    def __delitem__(self, key: str) -> None:
        del self.__params__[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__params__)

    def __getattr__(self, key: str) -> Any:
        """Make parameters accessable as attributes."""
        key = str(key)
        if not key.startswith("__") and key in self.__params__.keys():
            return self.__params__[key]
        else:
            return super().__getattribute__(key)

    def __setattr__(self, key: str, value: Any) -> None:
        """Make parameters accessable as attributes."""
        key = str(key)
        if not key.startswith("__") and key in self.__params__.keys():
            self.__params__[key] = value
        else:
            super().__setattr__(key, value)

    def __dict__(self):
        return self.__params__

    def key(self, decimals=None, delim="; "):
        strings = list()
        for k, v in self.__params__.items():
            if decimals is not None and isinstance(v, (int, float)):
                v = f"{v:.{decimals}f}"
            strings.append(f"{k}={v}")
        return delim.join(strings)

    def json(self):
        return json.dumps(self.__params__)

    def pformat(self):
        return ", ".join([f"{k}={v}" for k, v in self.__params__.items()])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self.__params__)})"

    def __str__(self) -> str:
        return self.pformat()


class AbstractModel(ModelParameters, ABC):
    """Abstract base class for model classes.

    The AbstractModel-class derives from ModelParameters.
    All parameters are accessable as attributes or dictionary-items.
    """

    def __init__(self, **params):
        """Initializes the AbstractModel-instance with the given initial parameters.

        Parameters
        ----------
        **params: Initial parameters of the model.
        """
        ModelParameters.__init__(self, **params)
        ABC.__init__(self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({ModelParameters.__str__(self)})"

    def hamiltonian(self, *args, **kwargs):
        pass


class AbstractSpinModel(AbstractModel):
    """Abstract base class for spin-models (e.g. Ising or Heisenberg)."""

    def __init__(self, num_sites: Optional[int] = 0, **params):
        super(AbstractModel, self).__init__(**params)
        self.basis: SpinBasis = SpinBasis()
        self.init_basis(num_sites)

    @property
    def num_sites(self) -> int:
        return self.basis.num_sites

    @property
    def spins(self) -> List[int]:
        return self.basis.spins

    def init_basis(self, num_sites: int, init_sectors: bool = None):
        self.basis.init(num_sites, init_sectors)

    def get_states(self, s: float = None):
        return self.basis.get_states(s)

    @abstractmethod
    def _hamiltonian_data(self, states):
        pass

    def hamiltonian_data(self, states):
        rows, cols, data = list(), list(), list()
        for row, col, val in self._hamiltonian_data(states):
            rows.append(row)
            cols.append(col)
            data.append(val)
        return data, (rows, cols)

    def hamilton_operator(self, s=None, states=None, dtype=None):
        if states is None:
            states = self.get_states(s)
        size = len(states)
        data, indices = self.hamiltonian_data(states)
        return HamiltonOperator(size, data, indices, dtype=dtype)

    def hamiltonian(self, s=None, states=None, dtype=None):
        hamop = self.hamilton_operator(s, states, dtype)
        return hamop.array()


class AbstractManyBodyModel(AbstractModel):
    """Abstract base class for model classes with a state basis.

    The AbstractModel-class derives from ModelParameters.
    All parameters are accessable as attributes or dictionary-items.
    """

    def __init__(self, num_sites: Optional[int] = 0, **params):
        super(AbstractModel, self).__init__(**params)
        self.basis: Basis = Basis()
        self.init_basis(num_sites)

    @property
    def num_sites(self) -> int:
        return self.basis.num_sites

    @property
    def fillings(self) -> List[int]:
        return self.basis.fillings

    def init_basis(self, num_sites, init_sectors=None):
        self.basis.init(num_sites, init_sectors)

    def iter_fillings(self):
        return self.basis.iter_fillings()

    def iter_sectors(self):
        return self.basis.iter_sectors()

    def get_sector(self, n_up=None, n_dn=None):
        return self.basis.get_sector(n_up, n_dn)

    @abstractmethod
    def _hamiltonian_data(self, up_states, dn_states):
        pass

    def hamiltonian_data(self, up_states, dn_states):
        rows, cols, data = list(), list(), list()
        for row, col, val in self._hamiltonian_data(up_states, dn_states):
            rows.append(row)
            cols.append(col)
            data.append(val)
        return data, (rows, cols)

    def hamilton_operator(self, n_up=None, n_dn=None, sector=None, dtype=None):
        if sector is None:
            sector = self.basis.get_sector(n_up, n_dn)
        up_states, dn_states = sector.up_states, sector.dn_states
        size = len(up_states) * len(dn_states)
        data, indices = self.hamiltonian_data(up_states, dn_states)
        return HamiltonOperator(size, data, indices, dtype=dtype)

    def hamiltonian(self, n_up=None, n_dn=None, sector=None, dtype=None):
        hamop = self.hamilton_operator(n_up, n_dn, sector, dtype)
        return hamop.array()
