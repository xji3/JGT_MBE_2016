"""
Implement various strategies to compute functions related to matrix exponential.

Some of these do precalculations, so they are not pure functions.

"""
from __future__ import division, print_function

import numpy as np
import scipy.linalg
import scipy.sparse.linalg
from scipy.sparse import coo_matrix

__all__ = ['PadeExpm', 'EigenExpm', 'ActionExpm']


def create_sparse_rate_matrix(state_space_shape, row, col, rate):
    """
    Create the rate matrix.

    """
    # check conformability of input arrays
    ndim = len(state_space_shape)
    assert_equal(len(row.shape), 2)
    assert_equal(len(col.shape), 2)
    assert_equal(len(rate.shape), 1)
    assert_equal(row.shape[0], rate.shape[0])
    assert_equal(col.shape[0], rate.shape[0])
    assert_equal(row.shape[1], ndim)
    assert_equal(col.shape[1], ndim)

    # create the sparse Q matrix from the sparse arrays
    nstates = np.prod(state_space_shape)
    mrow = np.ravel_multi_index(row.T, state_space_shape)
    mcol = np.ravel_multi_index(col.T, state_space_shape)
    Q = coo_matrix((rate, (mrow, mcol)), (nstates, nstates))

    # get the dense array of exit rates, and set the diagonal
    exit_rates = Q.sum(axis=1).A.flatten()
    Q.setdiag(-exit_rates)

    return Q


def create_dense_rate_matrix(state_space_shape, row, col, rate):
    """
    Create the rate matrix.

    """
    return create_sparse_rate_matrix(state_space_shape, row, col, rate).A


class PadeExpm(object):
    """
    This requires lower memory than EigenExpm.
    The implementation is the simplest because it does not cache anything.

    """
    def __init__(self, state_space_shape, row, col, rate):
        self.Q = create_sparse_rate_matrix(state_space_shape, row, col, rate)

    def expm_mul(self, rate_scaling_factor, A):
        """
        Compute exp(Q * r) * A.

        """
        return scipy.linalg.expm(self.Q.A * rate_scaling_factor).dot(A)

    def rate_mul(self, rate_scaling_factor, PA):
        """
        Compute Q * r * PA.
        This is for gradient calculation.

        """
        return self.Q.dot(PA * rate_scaling_factor)


class EigenExpm(object):
    def __init__(self, state_space_shape, row, col, rate):
        self.Q = create_dense_rate_matrix(state_space_shape, row, col, rate)
        self.w, self.U = scipy.linalg.eig(self.Q)
        self.V = scipy.linalg.inv(self.U)

    def expm_mul(self, rate_scaling_factor, A):
        """
        Compute exp(Q * r) * A.

        """
        w_exp = np.exp(self.w * rate_scaling_factor)
        VA = self.V.dot(A)
        return (self.U * w_exp).dot(VA).real

    def rate_mul(self, rate_scaling_factor, PA):
        """
        Compute Q * r * PA.
        This is for gradient calculation.

        """
        return self.Q.dot(PA * rate_scaling_factor)


class ActionExpm(object):
    def __init__(self, state_space_shape, row, col, rate):
        self.Q = create_sparse_rate_matrix(state_space_shape, row, col, rate)

    def expm_mul(self, rate_scaling_factor, A):
        """
        Compute exp(Q * r) * A.

        """
        return scipy.sparse.linalg.expm_multiply(
                self.Q, A, start=rate_scaling_factor)

    def rate_mul(self, rate_scaling_factor, PA):
        """
        Compute Q * r * PA.
        This is for gradient calculation.

        """
        return self.Q.dot(PA * rate_scaling_factor)
