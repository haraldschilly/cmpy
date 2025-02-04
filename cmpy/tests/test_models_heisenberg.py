# coding: utf-8
#
# This code is part of cmpy.
#
# Copyright (c) 2022, Dylan Jones

from hypothesis import given, strategies as st
import numpy as np
from numpy.testing import assert_array_equal
from cmpy import kron, sigz, sigp, sigm
from cmpy.models import HeisenbergModel
from lattpy import simple_chain


def xxz_hamiltonian(num_sites, j=1.0, jz=1.0):
    parts = [np.eye(2) for _ in range(num_sites - 1)]
    s_zz = 0.5 * kron(sigz, sigz)
    s_pmmp = 0.5 * (kron(sigp, sigm) + kron(sigm, sigp))

    ham = np.zeros((2**num_sites, 2**num_sites), dtype=np.complex128)
    for i in range(num_sites - 1):
        parts[i] = j / 2 * s_pmmp + jz * s_zz
        ham += kron(parts)
        parts[i] = np.eye(2)
    return ham.real


@given(st.integers(3, 5))
def test_hamiltonian_1d(num_sites):
    latt = simple_chain()
    latt.build(num_sites, relative=True)
    model = HeisenbergModel(latt, j=1.0, jz=1.0)
    ham = model.hamiltonian()
    expected = xxz_hamiltonian(num_sites, model.j, model.jz)
    assert_array_equal(expected, ham)
