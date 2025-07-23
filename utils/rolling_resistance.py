import casadi as ca

def Sauthoff_coefficients(numCoaches, mass, g=9.81):
    """
    F = r0 + r1*v + r2*v**2, with v in km/h and F in kN.

    Mass input in kg.
    """

    v = ca.SX.sym('v')

    # specific rolling resistance (N/kN)
    srr = 1.9 + 0.0025*v + 4.8*((numCoaches + 2.7)/(mass*g*1e-3))*0.0145*((v+15)**2)

    # rolling resistance kN
    rr = srr*(mass*g*1e-3)*1e-3

    # casadi functions
    rr_fun = ca.Function("rr", [v], [rr])
    rr_fun_jac = ca.Function("rrJac", [v], [ca.jacobian(rr_fun(v), v)])
    rr_fun_hes = ca.Function("rrHes", [v], [ca.jacobian(rr_fun_jac(v), v)])

    # function evaluations to get coefficients
    rr0 = float(rr_fun(0))
    rr1 = float(rr_fun_jac(0))
    rr2 = float(rr_fun_hes(0))

    return rr0, rr1, rr2


if __name__ == '__main__':

    # example Stadler KISS
    print(Sauthoff_coefficients(6, 297000))
