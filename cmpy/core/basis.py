# coding: utf-8
"""
Created on 07 Jul 2020
Author: Dylan Jones
"""
import abc
import numpy as np
from dataclasses import dataclass
from collections import defaultdict
from itertools import product

__BITORDER__ = -1

BITS = 4
DTYPE = np.int16

UP, DN = +1, -1

EMPTY = "."
UP_CHAR = "↑"
DN_CHAR = "↓"
UD_CHAR = "⇅"  # "d"
SPIN_CHARS = {0: EMPTY, UP: UP_CHAR, DN: DN_CHAR, 2: UD_CHAR}


def set_global_bitnum(bits):
    global BITS
    BITS = bits


def set_global_dtype(dtype):
    global DTYPE
    DTYPE = dtype


def spinstate_label(spinstate, sigma, digits=None, bra=False, ket=True):
    spinchar = UP_CHAR if sigma == UP else DN_CHAR
    digits = digits if digits is not None else BITS
    min_digits = len(bin(spinstate)[2:])
    num_chars = max(min_digits, digits)
    chars = list()
    for i in range(num_chars):
        char = spinchar if spinstate >> i & 1 else EMPTY
        chars.append(char)
    label = "".join(chars)[::-__BITORDER__]
    if bra:
        label = f"⟨{label}|"
    elif ket:
        label = f"|{label}⟩"
    return label


def state_label(up_num, dn_num, digits=None, bra=False, ket=True):
    digits = digits if digits is not None else BITS
    min_digits = max(len(bin(up_num)[2:]), len(bin(dn_num)[2:]))
    num_chars = max(min_digits, digits)
    chars = list()
    for i in range(num_chars):
        u = up_num >> i & 1
        d = dn_num >> i & 1
        if u and not d:
            char = UP_CHAR
        elif not u and d:
            char = DN_CHAR
        else:
            char = SPIN_CHARS[u + d]
        chars.append(char)
    label = "".join(chars)[::-__BITORDER__]
    if bra:
        label = f"⟨{label}|"
    elif ket:
        label = f"|{label}⟩"
    return label


def binstr(num, digits=None):
    """ Returns the binary representation of an integer.

    Parameters
    ----------
    num: int
        The number to convert.
    digits: int, optional
        Minimum number of digits used. The default is the global value `BITS`.
    """
    fill = digits if digits is not None else BITS
    return f"{num:0{fill}b}"[::__BITORDER__]


def binarr(num, digits=None, dtype=None):
    """ Returns the bits of an integer as a binary array.

    Parameters
    ----------
    num: int or Spinstate
        The number representing the binary state.
    digits: int, optional
        Minimum number of digits used. The default is the global value `BITS`.
    dtype: int or str, optional
        An optional datatype-parameter. The default is the global value `DTYPE`.

    Returns
    -------
    binarr: np.ndarray
    """
    fill = digits if digits is not None else BITS
    return np.fromiter(f"{num:0{fill}b}"[::__BITORDER__], dtype=dtype or DTYPE)


class Binary(int):

    @property
    def int(self):
        return int(self)

    @property
    def bin(self):
        return bin(self)

    def binstr(self, digits=None):
        """ Returns the binary representation of the state """
        return binstr(self, digits)

    def binarr(self, digits=None, dtype=None):
        """ Returns the bits of an integer as a binary array. """
        return binarr(self, digits, dtype)

    def count(self, value=1):
        return bin(self).count(str(value))

    def get(self, bit):
        return int(self & (1 << bit))

    def flip(self, bit):
        return self.__class__(self ^ (1 << bit))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.binstr()})"

    def __str__(self):
        return self.binstr()

    # -------------- Math operators -------------

    def __add__(self, other):
        return self.__class__(super().__add__(other))

    def __radd__(self, other):
        return self.__class__(super().__radd__(other))

    def __sub__(self, other):
        return self.__class__(super().__sub__(other))

    def __rsub__(self, other):
        return self.__class__(super().__rsub__(other))

    def __mul__(self, other):
        return self.__class__(super().__mul__(other))

    def __rmul__(self, other):
        return self.__class__(super().__rmul__(other))

    # -------------- Binary operators -------------

    def __invert__(self):
        return self.__class__(super().__invert__())

    def __and__(self, other):
        return self.__class__(super().__and__(other))

    def __or__(self, other):
        return self.__class__(super().__or__(other))

    def __xor__(self, other):
        return self.__class__(super().__xor__(other))

    def __lshift__(self, other):
        return self.__class__(super().__lshift__(other))

    def __rshift__(self, other):
        return self.__class__(super().__rshift__(other))


# =========================================================================
# Fock-State for one spin
# =========================================================================


def overlap(num1, num2, digits=None, dtype=None):
    """ Computes the overlap of two integers and returns the results as a binary array.

    Parameters
    ----------
    num1: int or Spinstate
        The integer representing the first binary state.
    num2: int or Spinstate
        The integer representing the second binary state.
    digits: int, optional
        Minimum number of digits used. The default is the global value `BITS`.
    dtype: int or str, optional
        An optional datatype-parameter. The default is the global value `DTYPE`.

    Returns
    -------
    binarr: np.ndarray
    """
    return binarr(num1 & num2, digits, dtype)


def occupations(num, digits=None, dtype=None):
    """ Returns the site occupations of a state as a binary array.

    Parameters
    ----------
    num: int or Spinstate
        The number representing the binary state.
    digits: int, optional
        Minimum number of digits used. The default is the global value `BITS`.
    dtype: int or str, optional
        An optional datatype-parameter. The default is the global value `DTYPE`.

    Returns
    -------
    binarr: np.ndarray
    """
    return binarr(num, digits, dtype)


def create(num, pos):
    """ Creates a particle at `pos` if possible and returns the new state.

    Parameters
    ----------
    num: int or Spinstate
        The number representing the binary state.
    pos: int
        The index of the state element.

    Returns
    -------
    new: int or None
    """
    op = 1 << pos
    if not op & num:
        return num ^ op
    return None


def annihilate(num, pos):
    """ Annihilates a particle at `pos` if possible and returns the new state.

    Parameters
    ----------
    num: int or Spinstate
        The number representing the binary state.
    pos: int
        The index of the state element.

    Returns
    -------
    new: int or None
    """
    op = 1 << pos
    if op & num:
        return num ^ op
    return None


class SpinState(Binary):

    def binstr(self, digits=None):
        """ Returns the binary representation of the state """
        return binstr(self, digits)

    def binarr(self, digits=None, dtype=None):
        """ Returns the bits of the integer as a binary array. """
        return binarr(self, digits, dtype)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.binstr()})"

    def __str__(self):
        return self.binstr()

    @property
    def n(self):
        """int: Total occupation of the state"""
        return bin(self).count("1")

    def occ(self, pos):
        """ Returns the occupation at index `pos`."""
        return self & (1 << pos)

    def occupations(self, dtype=None):
        """ Returns the site occupations of a state as a binary array. """
        return occupations(self, dtype=dtype)

    def overlap(self, other, dtype=None):
        """ Computes the overlap with another state and returns the results as a binary array. """
        return overlap(self, other, dtype=dtype)

    def create(self, pos):
        """ Creates a particle at `pos` if possible and returns the new state.

        Parameters
        ----------
        pos: int
            The index of the state element.
        """
        return self.__class__(create(self, pos))

    def annihilate(self, pos):
        """ Annihilates a particle at `pos` if possible and returns the new state.

        Parameters
        ----------
        pos: int
            The index of the state element.
        """
        return self.__class__(annihilate(self, pos))


def create_spinstates(num_sites):
    """ Creates all possible `SpinState`s for the given number of sites.

    Parameters
    ----------
    num_sites: int
        The number of sites of the system.

    Returns
    -------
    spinstates: list of SpinState
    """
    # Set length of binary representation
    global BITS
    BITS = num_sites
    # create states
    max_int = int("1" * num_sites, base=2)
    return [SpinState(num) for num in range(max_int + 1)]


@dataclass
class State:

    __slots__ = ['up', 'dn']

    up: int or SpinState
    dn: int or SpinState

    def label(self, digits=None, bra=False, ket=True):
        return state_label(self.up, self.dn, digits, bra, ket)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.up}, {self.dn})"

    def __str__(self):
        return f"{self.__class__.__name__}: {self.label()}"


# =========================================================================
# Fock-Basis and Basis-Sectors
# =========================================================================


class StateContainer(abc.ABC):

    def __init__(self, num_sites):
        self.num_sites = num_sites
        super().__init__()

    @property
    @abc.abstractmethod
    def states(self):
        pass

    @property
    @abc.abstractmethod
    def size(self):
        pass

    @property
    def shape(self):
        size = self.size
        return size, size

    @property
    def labels(self):
        return self.get_labels()

    @abc.abstractmethod
    def get_label(self, state, bra=False, ket=False):
        pass

    def get_labels(self, bra=False, ket=False):
        return [self.get_label(s, bra, ket) for s in self.states]

    def __repr__(self):
        return f"{self.__class__.__name__}(sites: {self.num_sites}, size: {self.size})"

    def __iter__(self):
        return iter(self.states)


class SpinSector(StateContainer):

    __slots__ = ['num_sites', 'n', 'sigma', 'spinstates']

    def __init__(self, num_sites, n, states, sigma=UP):
        super().__init__(num_sites)
        self.n = n
        self.sigma = sigma
        self.spinstates = states

    @property
    def states(self):
        return self.spinstates

    @property
    def size(self):
        return len(self.spinstates)

    def get_label(self, state, bra=False, ket=False):
        return spinstate_label(state, self.sigma, self.num_sites, bra, ket)


class BasisSector(StateContainer):

    __slots__ = ['num_sites', 'n_up', 'n_dn', 'up_states', 'dn_states']

    def __init__(self, num_sites, n_up, n_dn, up_states, dn_states):
        super().__init__(num_sites)
        self.n_up = n_up
        self.n_dn = n_dn
        self.up_states = up_states
        self.dn_states = dn_states

    @property
    def states(self):
        for up, dn in product(self.up_states, self.dn_states):
            yield State(up, dn)

    @property
    def size(self):
        return len(self.up_states) * len(self.dn_states)

    @property
    def num_up_states(self):
        return len(self.up_states)

    @property
    def num_dn_states(self):
        return len(self.dn_states)

    @property
    def filling(self):
        return self.n_up, self.n_dn

    def get_label(self, state, bra=False, ket=False):
        return state_label(state.up, state.dn, self.num_sites, bra, ket)

    def get_state_index(self, idx_up, idx_dn):
        return idx_up * self.size + idx_dn

    def get_spin_states(self, state_idx):
        idx_up = state_idx // self.size
        idx_dn = state_idx % self.size
        return self.up_states[idx_up], self.dn_states[idx_dn]

    def state_arrays(self, dtype=DTYPE):
        up_states = np.asarray(self.up_states, dtype=dtype)
        dn_states = np.asarray(self.dn_states, dtype=dtype)
        return up_states, dn_states


class FockBasis(StateContainer):

    def __init__(self, num_sites=0):
        super().__init__(num_sites)
        self._size = 0
        self._spinstates = list()
        self._sectors = defaultdict
        self._fillings = list()

        if num_sites:
            self.init_basis(num_sites)

    def init_basis(self, num_sites):
        spinstates = list(create_spinstates(num_sites))
        sectors = defaultdict(list)
        for state in spinstates:
            sectors[state.n].append(state)
        num_spinstates = len(spinstates)

        self.num_sites = num_sites
        self._size = num_spinstates * num_spinstates
        self._spinstates = spinstates
        self._sectors = sectors
        self._fillings = list(self._sectors.keys())

    @property
    def fillings(self):
        return self._fillings

    @property
    def states(self):
        for up, dn in product(self._spinstates, repeat=2):
            yield State(up, dn)

    @property
    def size(self):
        return self._size

    def iter_fillings(self, repeat=2):
        return product(self._fillings, repeat=repeat)

    def iter_sectors(self):
        for n_up, n_dn in self.iter_fillings(2):
            yield self.get_sector(n_up, n_dn)

    def get_label(self, state, bra=False, ket=False):
        return state_label(state.up, state.dn, self.num_sites, bra, ket)

    def state_index(self, idx_up, idx_dn):
        return idx_up * self.size + idx_dn

    def get_spinstates(self, n=None):
        return self._sectors.get(n, self._spinstates)

    def get_spin_sector(self, n=None, sigma=UP):
        states = self.get_spinstates(n)
        return SpinSector(self.num_sites, n, states, sigma)

    def get_sector(self, n_up=None, n_dn=None, sector=None):
        if (n_up is None) and (n_dn is None) and (sector is not None):
            return sector
        up_states = self.get_spinstates(n_up)
        dn_states = self.get_spinstates(n_dn)
        return BasisSector(self.num_sites, n_up, n_dn, up_states, dn_states)

    def get_next_sector(self, n_up=None, n_dn=None, sector=None, sigma=UP, delta=1):
        if sector is not None:
            n_up, n_dn = sector.filling
        if sigma == UP:
            n_up += delta
        else:
            n_dn += delta
        if (n_up not in self.fillings) or (n_dn not in self.fillings):
            return None
        return self.get_sector(n_up, n_dn)


def main():
    basis = FockBasis(2)
    sector = basis.get_sector(1, 1)
    for s in sector.states:
        print(s)


if __name__ == "__main__":
    main()
