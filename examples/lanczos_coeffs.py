# Copyright 2009--2014 Mark Dickinson.
#
# This file is part of the bigfloat module.
#
# The bigfloat module is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# The bigfloat module is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the bigfloat module.  If not, see <http://www.gnu.org/licenses/>.

# Computing the gamma function via Lanczos' formula
#
# See document at:
#
#  http://www.boost.org/doc/libs/1_40_0/libs/math/doc/sf_and_dist/html/math_toolkit/backgrounders/lanczos.html
#
# for more.  Note that the formula for a_0 on that page is invalid, involving
# a (-1)!.  But in general, the j=0 term of the sum for a_k is
# (k-1)!/(k)! = 1/k, and multiplying by k gives 0.

# The reference
#
# http://my.fit.edu/~gabdo/gamma.txt  (Paul Godfrey) gives instead
# the formulas:
#
# z! = sqrt(2*pi)*(z+g+1/2)^(z+1/2)*exp(-(z+g+1/2))*Ag(z)

# Ag(z) = 1/2*p(0) + z/(z+1)*p(1) + z*(z-1)/(z+1)/(z+2)*p(2) + ...

# p(k) = sum_{j=0}^k C(2k, 2j)*F(g, j)

# C(2k, 2j) : coefficients of the Chebyshev polynomials of the
# first kind.  (1, x, 2x^2-1, 4x^3-3x, ...).  Thus:
#
# C(0, 0) = 1
# C(2, 0) = -1, C(2, 2) = 2
# C(4, 0) = 1, C(4, 2) = -8, C(4, 4) = 8

# sequence A053120.
#
# if C(n, m) = coefficient of x**m in nth poly, then
#   C(n, 0) = (-1)**(n/2)   (n even)
#   C(n, m) = (-1)**((n+m)/2 + m) * (2**(m-1))*n*binomial((n+m)/2-1, m-1)/m

# Hence:
#
#  C(2k, 2j) = (-1)**(j+k) 2**(2j-1) 2k binomial(k+j-1, 2j-1) / (2j)
#            = (-1)**(j+k) 2**2j (k+j-1)! / (2j)! / (k-j)! * k
# absorbing the (2j)!/j!/2**(2j) from F(g, j) gives:
#            = (-1)**(j+k) (k+j-1)! * k / (k-j)! / j!

# Okay, so that works in


# F(g, j) = sqrt(2)/pi * (j-1/2)!*(j+g+1/2)^-(j+1/2)*exp(j+g+1/2)

# note that (j-1/2)! = (j-1/2)*(j-3/2)*...*(1/2) * sqrt(pi)
# = (2*j-1)*(2*j-3)*...*2 * sqrt(pi) / 2**j
# = (2*j)!/j!/2**(2j) * sqrt(pi)


from __future__ import division
from math import factorial
import bigfloat
from bigfloat import exp


def M(k, j):
    # returns an integer, the combinatorial coefficient in the
    # Lanczos formula.
    assert 0 <= j and 0 <= k
    if j == k == 0:
        return 1
    if j > k:
        return 0
    top = (-1)**(k+j) * factorial(j+k-1) * k
    bottom = factorial(k-j) * factorial(j)
    assert top % bottom == 0
    return top // bottom


def H(g, j):
    return exp(j+g+0.5) / (j+g+0.5)**(j+0.5)


def b(j, N):
    assert 0 <= j <= N-1
    coeffs = [1]
    facs = list(range(j, N-1)) + list(range(-1, -j-1, -1))
    for i in facs:
        # multiply by (z+i)
        times_z = [0] + coeffs
        times_i = [i*c for c in coeffs] + [0]
        coeffs = [a + b for a, b in zip(times_z, times_i)]
    assert len(coeffs) == N
    return coeffs


def Lg_num_coeffs(g, N):
    B = [b(j, N) for j in range(N)]
    MM = [[(M(k, j) if k == 0 else 2*M(k, j))
           for j in range(N)] for k in range(N)]
    # BTM has only integer entries
    BTM = [[sum(B[k][l] * MM[k][j] for k in range(N))
            for j in range(N)] for l in range(N)]

    HH = [H(g, j) for j in range(N)]
    coeffs = [sum(BTM[i][j] * HH[j] for j in range(N)) for i in range(N)]
    return coeffs


def Lg_den_coeffs(g, N):
    return b(0, N)


def L(g, z, N):
    num_coeffs = Lg_num_coeffs(g, N)
    den_coeffs = Lg_den_coeffs(g, N)

    num = 0.0
    for c in reversed(num_coeffs):
        num = num * z + c
    den = 0.0
    for c in reversed(den_coeffs):
        den = den * z + c
    return num/den


def gamma(z, g, N):
    return (z+g-0.5)**(z-0.5) / exp(z+g-0.5) * L(g, z, N)


# Now express everything as a rational function;  we want to be
# able to figure out the coefficient of p_j z^k in the numerator.
# Let's call this coefficient b(j, k).  It depends on N.
# b(j, N)[k] is the coefficient of p_j z^k in the numerator.
# except: b(0, N)[k] is the coefficient of p_0/2 z^k in the numerator.

p = 300  # bits of precision to use for computation
g = bigfloat.BigFloat(6.024680040776729583740234375)
N = 13

with bigfloat.precision(p):
    print("Numerator coefficients:")
    for c in Lg_num_coeffs(g, N):
        print(c)

    print("Denominator coefficients:")
    for c in Lg_den_coeffs(g, N):
        print(c)
