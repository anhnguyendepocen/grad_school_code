################################################################################
### EECS 545, problem set 3 functions
################################################################################

################################################################################
### 1: Load packages
################################################################################

# Import necessary packages
import numpy as np

################################################################################
### 2: Define functions
################################################################################

################################################################################
### 2.1: Problem 1
################################################################################


# Define a function to calculate the effective degrees of freedom associated
# with a given ridge penalty weight lambda
def effdf(X, l):
    """ Calculate effective degrees of freedom for ridge regression

    Inputs
    sigma: Standard deviations of input features, d by 1 vector
    l: Ridge regression penalty weight, scalar

    Outputs
    effdf: Effective degrees of freedom, scalar
    """
    d = X.shape[0]

    I = np.identity(d)

    I[0,0] = 0

    effdf = np.trace(X.T @ np.linalg.inv(X @ X.T + l * I) @ X)

    # Return the result
    return effdf


# Define regularized least squares estimator
def regls(y_tr, X_tr, l=10, y_te=None, X_te=None, demean=True, sdscale=True):
    """ Implements regularized least squares (ridge regression)

    Inputs
    y_tr: Training data responses, n_tr by 1 vector
    X_tr: Training data features, d by n_tr matrix
    l: Regularized least squares penalty, scalar
    y_te: Test data responses, n_te by 1 vector. If provided, the function will
          calculate the mean squared error on the test data. (Requires that X_te
          is also provided.)
    X_te: Test data features, d by n_te matrix. If provided, the function will
          calculate predicted values based on these features.
    demean: Boolean. If True, the function de-means any training and test
            features, using the mean of the training data.
    sdscale: Boolean. If True, the function scales any training and test
             features by the inverse of the standard deviation of the training
             features. (This happens after de-meaning, if demean is also True.)

    Outputs
    w_hat: Estimated coefficients, d by 1 vector
    y_hat: Predicted responses, n_te by 1 vector (if X_te was provided)
    mse: Mean squared error, scalar (if y_te and X_te were provided)

    Notes
    The intercept is not penalized
    """
    # Get number of features d and number of instances in the training data n_tr
    d, n_tr = X_tr.shape

    # Demean the training features, if desired
    if demean:
        ones_tr = np.ones(shape=(n_tr,1))
        mu_X_tr = (X_tr @ ones_tr) / n_tr  # It's useful to have this for later
        X_tr = X_tr - mu_X_tr @ ones_tr.T

    # Scale the training features by the inverse of their standard deviation, if
    # desired
    if sdscale:
        sigma_X_tr = np.diag(1 / np.std(X_tr, axis=1))
        X_tr = sigma_X_tr @ X_tr

    # Add intercept to the training features
    X_tr = np.concatenate((np.ones(shape=(1,n_tr)), X_tr), axis=0)

    # Set up a modified identity matrix with the first element set to zero,
    # starting with just an identity matrix
    I_check = np.identity(d+1)

    # Set its first element to zero
    I_check[0,0] = 0

    # Get the estimates, solving a system of linear equations instead of
    # calculating the inverse (since I'm not trying to get standard errors)
    w_hat = np.linalg.solve(X_tr @ X_tr.T + l * I_check, X_tr @ y_tr)

    # Check whether test data features were provided
    if X_te is not None:
        # If so, get number of instances in the test data
        n_te = X_te.shape[1]

        # Demean test data if desired, using training data feature means
        if demean:
            ones_te = np.ones(shape=(n_te,1))
            X_te = X_te - mu_X_tr @ ones_te.T

        # Scale test data if desired, using inverse training data standard
        # deviations
        if sdscale:
            X_te = sigma_X_tr @ X_te

        # Add intercept to the test features
        X_te = np.concatenate((np.ones(shape=(1,n_te)), X_te), axis=0)

        # Get predicted responses
        y_hat = (X_te.T @ w_hat)

        # Check whether test data responses were provided
        if y_te is not None:
            # If so, calculate MSE
            mse = (y_te - y_hat).T @ (y_te - y_hat) / n_te

            # Return the estimated coefficients, predictions, and MSE
            return w_hat, y_hat, mse[0,0]
        else:
            # Return the estimated coefficients and predictions
            return w_hat, y_hat
    else:
        # Return the estimated coefficients
        return w_hat

################################################################################
### 2.2: Problem 2
################################################################################


# Define a function which calculates the OLS gradient
def ols_gradient(y, X, w):
    """ Calculates OLS gradient

    Inputs
    y: n by 1 vector, responses
    X: d by n matrix, features
    w: d by 1 vector, weights

    Outputs
    J: d by 1 vector, gradient
    """
    # Calculate gradient
    J = -2 * X @ (y - X.T @ w)

    # Return the result
    return J


# Define a function to calculate the OLS MSE (average squared residual)
def ols_mse(y, X, w, demean=False, sdscale=False, addicept=False):
    """ Calculates OLS mean squared error

    Inputs
    y: n by 1 vector, responses
    X: d by n matrix, features
    w: d by 1 vector, weights
    demean: Boolean, if True, the features will be de-meaned
    sdscale: Boolean, if True, the features will be scaled by their inverse
             standard deviation
    addicept: Boolean, if True, an intercept will be added to the features

    Outputs
    mse: Scalar, mean squared error
    """
    # Get the number of instances n
    n = X.shape[1]

    # Demean the training features, if desired
    if demean:
        ones = np.ones(shape=(n,1))
        mu_X = (X @ ones) / n
        X = X - mu_X @ ones.T

    # Scale the training features by the inverse of their standard deviation, if
    # desired
    if sdscale:
        sigma_X = np.diag(1 / np.std(X, axis=1))
        X = sigma_X @ X

    # Check whether an intercept needs to be added
    if addicept:
        # Add intercept to the training features
        X = np.concatenate((np.ones(shape=(1,n)), X), axis=0)

    # Calculate MSE
    mse = (y - X.T @ w).T @ (y - X.T @ w) / n

    # Return the result
    return mse[0,0]


# Define a function to implement gradient descent
def graddesc(y_tr, X_tr, y_te=None, X_te=None, w0=None, gradient=ols_gradient,
             eta=.05, avggrad=True, K=500, demean=True, sdscale=True,
             objfun=ols_mse):
    """ Implements gradient descent

    Inputs
    y_tr: n_tr by 1 vector, training responses
    X_tr: d by n_tr matrix, training features
    y_te: n_te by 1 vector, test responses
    X_te: d by n_te matrix, test features
    w0: d by 1 vector, initial weights. If None, uses vecrtor of zeros.
    gradient: Function, has to be such that gradient(y, X, w) returns the
              gradient
    eta: Scalar, step size
    avggrad: Boolean, if True, the update divides the step size eta by the
             number of instances in the training data
    K: Integer, number of gradient descent iterations
    demean: Boolean, if True, features will be de-meaned (using the training
            means)
    sdscale: Boolean, if True, features will be scaled by the inverse of their
             standard deviation (using the training standard deviation)
    objfun: Function, has to be such that objfun(y, X, w) returns the objective
            function

    Outputs
    w_hat: d+1 by 1 vector, updated weights
    L_tr: List, i-th element is the objective function value at the i-th
          iteration, in the training data
    y_hat: n_te by 1 vector, predicted responses
    L_te: Scalar, objective function value at w_hat in the test data

    Notes
    Adds an intercept to the features
    """
    # Get the number of features d and number of instances n
    d, n_tr = X_tr.shape

    # Check whether the initial weights are None
    if w0 is None:
        # If so, use a vector of zeros
        w0 = np.zeros(shape=(d+1, 1))

    # Demean the training features, if desired
    if demean:
        ones = np.ones(shape=(n_tr,1))
        mu_X_tr = (X_tr @ ones) / n_tr
        X_tr = X_tr - mu_X_tr @ ones.T

    # Scale the training features by the inverse of their standard deviation, if
    # desired
    if sdscale:
        sigma_X_tr = np.diag(1 / np.std(X_tr, axis=1))
        X_tr = sigma_X_tr @ X_tr

    # Add intercept to the training features
    X_tr = np.concatenate((np.ones(shape=(1, n_tr)), X_tr), axis=0)

    # Set up list of objective functions, starting with the value at w0
    L_tr = [objfun(y_tr, X_tr, w0)]

    # Go through all gradient descent iterations
    for i in range(K):
        # Calculate gradient
        J = gradient(y_tr, X_tr, w0)

        # Check whether to updated based on the average gradient
        if avggrad:
            # Do the GD update, dividing the step size by n_tr
            w_hat = w0 - (eta / n_tr) * J
        else:
            # Do the GD update, using the step size as is
            w_hat = w0 - eta * J

        # Add objective function at this iteration to the list
        L_tr.append(objfun(y_tr, X_tr, w_hat))

        # Set initial weights for the next iteration
        w0 = w_hat

    # Check whether test data features were provided
    if X_te is not None:
        # If so, get number of instances in the test data
        n_te = X_te.shape[1]

        # Demean test data if desired, using training data feature means
        if demean:
            ones_te = np.ones(shape=(n_te, 1))
            X_te = X_te - mu_X_tr @ ones_te.T

        # Scale test data if desired, using inverse training data standard
        # deviations
        if sdscale:
            X_te = sigma_X_tr @ X_te

        # Add intercept to the test features
        X_te = np.concatenate((np.ones(shape=(1, n_te)), X_te), axis=0)

        # Get predicted responses
        y_hat = (X_te.T @ w_hat)

        # Check whether test data responses were provided
        if y_te is not None:
            # If so, calculate MSE
            L_te = objfun(y_te, X_te, w_hat)

            # Return the estimated coefficients, objective function values,
            # predictions, and MSE
            return w_hat, L_tr, y_hat, L_te
        else:
            # Return the estimated coefficients, objective function values, and
            # predictions
            return w_hat, L_tr, y_hat
    else:
        # Return the estimated coefficients and objective function values
        return w_hat, L_tr


# Define a function to implement gradient descent
def stochgraddesc(y_tr, X_tr, y_te=None, X_te=None, w0=None,
                  gradient=ols_gradient, eta=.0005, K=500, demean=True,
                  sdscale=True, objfun=ols_mse):
    """ Implements stochastic gradient descent

    Inputs
    y_tr: n_tr by 1 vector, training responses
    X_tr: d by n_tr matrix, training features
    y_te: n_te by 1 vector, test responses
    X_te: d by n_te matrix, test features
    w0: d by 1 vector, initial weights. If None, uses vecrtor of zeros.
    gradient: Function, has to be such that gradient(y, X, w) returns the
              gradient
    eta: Scalar, step size
    K: Integer, number of stochastic gradient descent epochs
    demean: Boolean, if True, features will be de-meaned (using the training
            means)
    sdscale: Boolean, if True, features will be scaled by the inverse of their
             standard deviation (using the training standard deviation)
    objfun: Function, has to be such that objfun(y, X, w) returns the objective
            function

    Outputs
    w_hat: d+1 by 1 vector, updated weights
    L_tr: List, i-th element is the objective function value at the i-th
          iteration, in the training data
    y_hat: n_te by 1 vector, predicted responses
    L_te: Scalar, objective function value at w_hat in the test data

    Notes
    Adds an intercept to the features
    """
    # Get the number of features d and number of instances n
    d, n_tr = X_tr.shape

    # Check whether the initial weights are None
    if w0 is None:
        # If so, use a vector of zeros
        w0 = np.zeros(shape=(d+1, 1))

    # Demean the training features, if desired
    if demean:
        ones = np.ones(shape=(n_tr,1))
        mu_X_tr = (X_tr @ ones) / n_tr
        X_tr = X_tr - mu_X_tr @ ones.T

    # Scale the training features by the inverse of their standard deviation, if
    # desired
    if sdscale:
        sigma_X_tr = np.diag(1 / np.std(X_tr, axis=1))
        X_tr = sigma_X_tr @ X_tr

    # Add intercept to the training features
    X_tr = np.concatenate((np.ones(shape=(1, n_tr)), X_tr), axis=0)

    # Set up list of objective functions, starting with the value at w0
    L_tr = [objfun(y_tr, X_tr, w0)]

    # Go through all epochs
    for k in range(K):
        # Draw a vector of indices (this implements SGD without replacement)
        idx = np.random.permutation(n_tr)

        # Go through the randomly permuted indices
        for j in idx:
            # Calculate gradient for the drawn instance
            J = gradient(y_tr[j:j+1, :], X_tr[:, j:j+1], w0)

            # Do the SGD update, using the step size as is
            w_hat = w0 - eta * J

            # Add objective function at this iteration to the list
            L_tr.append(objfun(y_tr, X_tr, w_hat))

            # Set initial weights for the next iteration
            w0 = w_hat

    # Check whether test data features were provided
    if X_te is not None:
        # If so, get number of instances in the test data
        n_te = X_te.shape[1]

        # Demean test data if desired, using training data feature means
        if demean:
            ones_te = np.ones(shape=(n_te, 1))
            X_te = X_te - mu_X_tr @ ones_te.T

        # Scale test data if desired, using inverse training data standard
        # deviations
        if sdscale:
            X_te = sigma_X_tr @ X_te

        # Add intercept to the test features
        X_te = np.concatenate((np.ones(shape=(1, n_te)), X_te), axis=0)

        # Get predicted responses
        y_hat = (X_te.T @ w_hat)

        # Check whether test data responses were provided
        if y_te is not None:
            # If so, calculate MSE
            L_te = objfun(y_te, X_te, w_hat)

            # Return the estimated coefficients, objective function values,
            # predictions, and MSE
            return w_hat, L_tr, y_hat, L_te
        else:
            # Return the estimated coefficients, objective function values, and
            # predictions
            return w_hat, L_tr, y_hat
    else:
        # Return the estimated coefficients and objective function values
        return w_hat, L_tr

################################################################################
### 2.4: Problem 4
################################################################################


# Define a function to do a coordinate descent update for ridge regression along
# a given dimension i
def cdupdate_ridge(i, y, X, w, l=100, freeicept=True):
    """ Does a single coordinate descent update for ridge regression

    Inputs
    i: Scalar, dimension in which to update
    y: n by 1 vector, responses
    X: d by n matrix, features
    w: d by 1 vector, weights
    l: Scalar, penalty term weight
    freeicept: Boolean, if True, intercept will not be penalized

    Outputs
    w: d by 1 vector, updated weights
    """
    # Get the i-th feature. Due to Numpy's indexing conventions, X[i:i+1, :]
    # gets the i-th row of X only, but as a row vector (rather than as a one
    # dimensional array). I just add the transpose because I prefer working with
    # column vectors.
    xi = X[i:i+1, :].T

    # Calculate two times the sum of squares for this feature
    ai = 2 * xi.T @ xi

    # Set the i-th element of the weights vector to zero
    w[i,0] = 0

    # Calculate predicted responses based on all other weights
    yhat = X.T @ w

    # Calculate pseudo-covariance between the i-th feature and the predictions
    # ignoring the i-th weight
    ci = 2 * xi.T @ (y - yhat)

    # Check whether the intercept should be penalized
    if freeicept and i == 0:
        # If not, and if this is the intercept, ignore the penalty weight in the
        # update
        w[i, 0] = ci / ai
    else:
        # Otherwise, incorporate the penalty weight
        w[i, 0] = ci / (ai + 2 * l)

    # Return the new weights vector
    return w


# Define a function to implement the coordinate descent algorithm
def coorddesc(y_tr, X_tr, w0=None, l=100, update_i=cdupdate_ridge, K=300,
              demean=True, sdscale=True, objfun=ols_mse):
    """ Implements coordinate descent
    y_tr: n_tr by 1 vector, training data labels
    X_tr: d by n_tr matrix, training data features
    w0: d by 1 vector, initial weights. If None, uses a zero vector to
        initialize.
    l: Scalar, penalty term weight
    update: Function, must be such that update(i, y, X, w) returns an updated
            vector of weights
    K: Scalar, number of SGD epochs
    demean: Boolean, if True, demeans the features
    sdscale: Boolean, if True, scales feature by the inverse of the standard
             deviation
    objfun: Function, must be such that objfun(y, X, w) returns the value of the
            objective function

    Outputs
    w_hat: d by 1 vector, estimated weights
    w_tr: d by K+1 matrix, learned weights across iterations
    L_tr: List, objective function at each iteration
    """
    # Get the number of features d and number of instances n
    d, n_tr = X_tr.shape

    # Check whether the initial weights are None
    if w0 is None:
        # If so, use a vector of zeros
        w0 = np.zeros(shape=(d+1, 1))

    # Demean the training features, if desired
    if demean:
        ones = np.ones(shape=(n_tr,1))
        mu_X_tr = (X_tr @ ones) / n_tr
        X_tr = X_tr - mu_X_tr @ ones.T

    # Scale the training features by the inverse of their standard deviation, if
    # desired
    if sdscale:
        sigma_X_tr = np.diag(1 / np.std(X_tr, axis=1))
        X_tr = sigma_X_tr @ X_tr

    # Add intercept to the training features
    X_tr = np.concatenate((np.ones(shape=(1, n_tr)), X_tr), axis=0)

    # Set up list of objective functions, starting with the value at w0
    L_tr = [objfun(y_tr, X_tr, w0)]

    # Set up a matrix of weights across iterations
    w_tr = np.empty(shape=(d+1, K+1))

    # Add initial weights to the matrix of weights
    w_tr[:,0] = w0[:,0]

    # Go through all cordinate descent iterations
    for k in range(K):
        # Figure out which dimension needs to be updated (the second part of
        # this line subtracts the number of epochs from the iteration number,
        # which gives the current dimension, noting that the 0-th dimension is
        # the intercept)
        i = np.int(k - np.floor(k / (d+1)) * (d+1))

        # Get updated weights
        w_hat = update_i(i=i, y=y_tr, X=X_tr, w=w0)

        # Add objective function at this iteration to the list
        L_tr.append(objfun(y_tr, X_tr, w_hat))

        # Add weights to the array of weights
        w_tr[:,k+1] = w_hat[:,0]

        # Set initial weights for the next iteration
        w0 = w_hat

    # Return the estimated coefficients and objective function values
    return w_hat, w_tr, L_tr
