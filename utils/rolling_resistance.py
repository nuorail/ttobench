import casadi as ca

def SauthoffCoefficients(numCoaches, mass, g=9.81):
    # input: velocity in km/h, mass in kg
    # output: force in kN

    v = ca.SX.sym('v')

    # specific rolling resistance (N/kN)
    srr = 1.9 + 0.0025*v + 4.8*((numCoaches + 2.7)/(mass*g*1e-3))*0.0145*((v+15)**2)

    # rolling resistance kN
    rr = srr*(mass*g*1e-3)*1e-3

    # casadi functions
    rrFun = ca.Function("rr", [v], [rr])
    rrFunJac = ca.Function("rrJac", [v], [ca.jacobian(rrFun(v), v)])
    rrFunHes = ca.Function("rrHes", [v], [ca.jacobian(rrFunJac(v), v)])

    # function evaluations to get coefficients
    rr0 = rrFun(0).full()[0][0]
    rr1 = rrFunJac(0).full()[0][0]
    rr2 = rrFunHes(0).full()[0][0]

    return rr0, rr1, rr2


if __name__ == '__main__':

    # example Stadler KISS
    print(SauthoffCoefficients(6, 297000))
