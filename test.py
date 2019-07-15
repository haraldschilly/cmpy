# -*- coding: utf-8 -*-
"""
Created on 26 Mar 2019
author: Dylan

project: cmpy2
version: 1.0
"""
from itertools import product
from sciutils import eta, Plot
from cmpy import *
from cmpy.hubbard import *


def configure_s_basis(model, eps=0., t=1., spin=True):
    model.spin = spin
    model.add_s_atom(energy=eps)
    model.set_hopping(t, "s")


def configure_p3_basis(model, eps_p=0., t_pps=1., t_ppp=1., d=None, spin=True, soc=0., ordering="spin"):
    model.spin = spin
    model.add_p3_atom(energy=eps_p)

    d = np.ones(3) if d is None else np.asarray(d)
    t_direct = d ** 2 + (1 - d ** 2) * t_ppp
    model.set_hopping(t_direct[0], "p_x")
    model.set_hopping(t_direct[1], "p_y")
    model.set_hopping(t_direct[2], "p_z")

    model.set_hopping(d[0] * d[1] * (t_pps - t_ppp), "p_x", "p_y")
    model.set_hopping(d[1] * d[2] * (t_pps - t_ppp), "p_y", "p_z")
    model.set_hopping(d[2] * d[0] * (t_pps - t_ppp), "p_z", "p_x")

    model.sort_states(ordering)
    model.set_soc(soc)


def configure_sp3_basis(model, eps_s=0.,  eps_p=0., t_sss=1., t_sps=0., t_pps=1., t_ppp=1.,
                        d=None, spin=True, soc=0., ordering="spin"):
    model.spin = spin
    model.add_sp3_atom(energy=[eps_s, eps_p, eps_p, eps_p])

    d = np.ones(3) if d is None else np.asarray(d)
    t_direct = d ** 2 + (1 - d ** 2) * t_ppp
    model.set_hopping(t_sss, "s")
    model.set_hopping(t_direct[0], "p_x")
    model.set_hopping(t_direct[1], "p_y")
    model.set_hopping(t_direct[2], "p_z")

    model.set_hopping(d[0] * t_sps, "s", "p_x")
    model.set_hopping(d[1] * t_sps, "s", "p_y")
    model.set_hopping(d[2] * t_sps, "s", "p_z")
    model.set_hopping(d[0] * d[1] * (t_pps - t_ppp), "p_x", "p_y")
    model.set_hopping(d[1] * d[2] * (t_pps - t_ppp), "p_y", "p_z")
    model.set_hopping(d[2] * d[0] * (t_pps - t_ppp), "p_z", "p_x")

    model.sort_states(ordering)
    model.set_soc(soc)


def main():
    # model = Siam(eps=2, v=5, mu=0)
    # ham = model.hamiltonian()
    # ham.show()

    model = TbDevice(np.eye(2))
    configure_p3_basis(model, soc=2)
    model.build((5, 1))
    model.load_lead()

    ham = model.hamiltonian()
    ham.show()
    omegas, trans = model.transmission_curve()
    Plot.quickplot(omegas.real, trans)


if __name__ == "__main__":
    main()
