'''
This python file implements the smo algorithm to support svm algorithms
@author: Jiang Qinhong
@email: mylivejiang@gmail.com
'''
import numpy as np
import numbers


class SVM:
    """
    This svm classifier class
    """
    def __init__(self, C=1.0, toler=0.001, maxIter=300, kernel='rbf', gamma = 'auto'):
        """
        :param X: the input x data, which is (m , n)
        :param y: the corresponding label, which is (m,)
        :param C: the C in svm, to control the algorithm. note larger C will lead to more support vectors
        :param toler: the toler to bound whether to do the the job
        :param maxIter: max iteration
        :param kernel: the kernel function
        """
        self._C = C
        self._tol = toler
        self._maxIter = maxIter
        self._eps = 0.001
        # our kernel. now only support 'linear' and 'rbf' kernel
        if kernel != 'rbf' or kernel != 'linear':
            raise NameError('Unsupported kernel. be linear or rbf')
        self._kernel = kernel
        # the gamma is only used for rbf kernel. if it is auto. then use gamma = 1 / fearture_size
        if isinstance(gamma, numbers.Number):
            self._gamma = gamma
        elif gamma != 'auto':
            raise NameError("Unsupported gamma. be float number or 'auto' type")



    def kernel(self, x1, x2):
        """
        kernel function
        :param x1: input x1
        :param x2: input x2
        :return: the computed kernel function value
        """
        # the linear kernel
        if self._kernel == 'linear':
            return x1.T * x2

        # the rbf gaussian kernel. default with
        elif self._kernel == 'rbf':
            delta = x1 - x2
            k = delta.T * delta
            return np.exp(k / (-1 * 2 * self._gamma))


    def learned_func(self, x):
        """
        the learned function. which is the hypethsis of the seperating plane
        :param x: input x
        :return: the value of g(x) = \sum_i^{n}(alpha_i * y_i * k(x_i, x)) + b
        """
        result = 0
        for i in range(0, self._m):
            result += self._alphas[i, 0] * self._y[i] * self.kernel(self._X[i, :], x)
        result += self._b
        return result

    def getE(self, i):
        """
        This is the function to get Ei. it can be computed or using the cached value
        :param i: indicates to get
        :return:
        """
        # if alpha is unbounded. then it's error is cached. just get it out
        # else we should compute it
        alpha = self._alphas[i]
        if (alpha > 0) and (alpha < self._C):
            return self._eCache[i]
        else:
            return self.learned_func(self._X[i, :]) - self._y[i]


    def examine(self, i):
        """
        the inner loop to do the job
        :param i: the first choosen alpha
        :return: 1 indicate success, 0 fail
        """
        # first check whether alpha1 is legal.
        y1 = self._y[i]
        alpha1 = self._alphas[i]
        E1 = self.getE(i)
        r1 = y1 * E1
        # judge if we can go on with this i
        if (r1 < -self._tol and alpha1 < self._C)  or (r1 > self._tol and alpha1 > 0):
            # now with alpha1, we can go on with alpha2 with index i2.
            # 3 conditions here

            # 1st choose the max step we can get in the unbounded points
            #--------------------- 1st get the max of step -------------------------------
            unbounded_index = ((self._alphas > 0) & (self._alphas < self._C)).nonzero()
            i2 = -1
            maxdeltaE = 0
            for index in unbounded_index:
                if index == i:
                    continue
                E_index = self._eCache[index]
                deltaE = abs(E1 - E_index)
                if deltaE > maxdeltaE:
                    maxdeltaE = deltaE
                    i2 = index
            if i2 >= 0:
                if self.takestep(i, i2):
                    return 1

            #-------------------------1st not work, work through all the unbounded points--------------
            # we shuffle the list first
            np.random.shuffle(unbounded_index)
            for index in unbounded_index:
                if self.takestep(i, index):
                    return 1

            #------------------------both above not work, so we just loop all the training points---------
            # note we have go through the unbounded examples, so just go through the bounded ones
            bound_index = [index for index in np.arange(self._m) if index not in unbounded_index]
            for index in bound_index:
                if self.takestep(i, index):
                    return 1

        # we are not go in this i, or all the i2 failed for this i
        return 0


    def takestep(self, i1, i2):
        """
        this is the main function. to take a step for the alpha1 and alpha2. if success, it will return 1.
        otherwise, it returns 0. besides it will update the b and error cache
        :param i1: the 1st lagrange multipliers
        :param i2: the 2nd lagrange multipliers
        :return: 1 indicate success, 0 fail
        """
        # first make sure i1 and i2 not equal
        if i1 == i2:
            return 0
        # get alpha1, y1, E1, alpha2, y2, E2
        alpha1_old = self._alphas[i1]
        y1 = self._y[i1]
        E1 = self.getE(i1)
        alpha2_old = self._alphas[i2]
        y2 = self._y[i2]
        E2 = self.getE(i2)


        # compute L and H
        H = L = 0
        if y1 == y2:
            H = min(self._C, alpha1_old + alpha2_old)
            L = max(0, alpha1_old + alpha2_old - self._C)
        else:
            H = min(self._C, self._C + alpha2_old - alpha1_old)
            L = max(0, alpha2_old - alpha1_old)
        if H==L:
            return 0

        # get k11, k12 and k22. and get eta to judge
        k11 = self.kernel(self._X[i1, :], self._X[i1, :])
        k22 = self.kernel(self._X[i2, :], self._X[i2, :])
        k12 = self.kernel(self._X[i1, :], self._X[i2, :])
        eta = k11 + k22 - 2*k12
        if (eta > 0):
            # most case it will larger than zero. it mecer's condtion is satisfied
            alpha2_new = alpha2_old + (y2 * (E1 - E2) / eta)
            if alpha2_new > H:
                alpha2_new = H
            if alpha2_new < L:
                alpha2_new = L
        else:
            c1 = eta / 2
            c2 = y2 * (E1 - E2) - eta * alpha2_old
            Lobj = c1 * L * L + c2 * L
            Hobj = c1 * H * H + c2 * H
            if Lobj > Hobj + self._eps:
                alpha2_new = L
            elif Lobj < Hobj - self._eps:
                alpha2_new = H
            else:
                alpha2_new = alpha2_old

        # step too small
        if np.abs(alpha2_new - alpha2_old) < self._eps * (alpha2_new + alpha2_old + self._eps):
            return 0

        # update alpha1_old
        alpha1_new = alpha1_old + y1 * y2 * (alpha2_old - alpha2_new)
        if (alpha1_new < 0):
            alpha2_new += y1 * y2 * alpha1_new
            alpha1_new = 0
        elif (alpha1_new > self._C):
            alpha2_new += y1 * y2 * (alpha1_new - self._C)
            alpha1_new = self._C


        # update alpha
        self._alphas[i1] = alpha1_new
        self._alphas[i2] = alpha2_new

        # update the b
        b1 = -E1 - y1 * k11 * (alpha1_new - alpha1_old) - y2 * k12 * (alpha2_new - alpha2_old) + self._b
        b2 = -E2 - y1 * k12 * (alpha1_new - alpha1_old) - y2 * k22 * (alpha2_new - alpha2_old) + self._b
        if alpha1_new > 0 and alpha1_old < self._C:
            self._b = b1
        elif alpha2_new > 0 and alpha2_new < self._C:
            self._b = b2
        else:
            self._b = (b1 + b2) / 2

        # update the error cache, for those unbounded points
        unbounded_index = ((self._alphas > 0) & (self._alphas < self._C)).nonzero()

        #--- left todo ---









    def fit(self, X, y):
        """
        the fit function. used to train the svm model. using SMO algorithm
        :param X:
        :param y:
        :return:
        """
        # set necessary data.
        self._X = X
        self._y = y
        [m, n] = X.size()
        assert m == len(y), "The training data and label size not equal! ({} vs {})".format(m, len(y))
        self._m = m
        # the error cache to store E. Note here, we only store E for
        # those alpha that are unbounded (0< alpha < C).
        self._eCache = np.zeros((m, 1))
        # the params of our model. alpha and b, which will be initialized to zero
        self._alphas = np.zeros((m, 1), dtype=np.float32)
        self._b = 0.0
        if self._gamma == 'auto':
            self._gamma = 1.0 / n


        # below is the main proceture to do the traning job
        # note it is actually the outer-loop to choose alpha1
        examine_all = True
        num_changed = 0
        iters = 0
        while (iters < self._maxIter) and (examine_all or num_changed > 0):
            num_changed = 0
            if examine_all:
                for i in range(self._m):
                    num_changed += self.examine(i)
            else:
                # loop only those unbounded
                unbounded_index = ((self._alphas > 0) & (self._alphas < self._C)).nonzero()
                for i in unbounded_index:
                    num_changed += self.examine(i)
            iters += 1
            if examine_all:
                examine_all = False
            elif num_changed == 0:
                examine_all = True
            print 'Iteration {}'.format(iters)












