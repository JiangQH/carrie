import numpy as np
from carrie.layers.baselayer import BaseLayer
from carrie.utils.im2col import im2col, col2im

class BaseConvolution(BaseLayer):
    """
    this is the convolution layer
    """
    def __init__(self, name, kernel_width = 3, kernel_height = 3, kernel_num = 64,
                 pad = 1, stride = 1, w_std=None, b_val=0.1):
        """
        convolution layer params
        :param name: name of this layer
        :param kernel_width: the kernel width
        :param kernel_height: the kernel height
        :param kernel_num: kernel nums
        :param pad: padding to the input
        :param stride: the stride of kernels
        :param w_std: the std to init weight
        :param b_val: the init val of bias
        """
        super(BaseConvolution, self).__init__(name)
        assert kernel_width > 0 and kernel_height > 0
        assert kernel_num > 0 and pad > 1 and stride > 1
        self.kernel_width = kernel_width
        self.kernel_height = kernel_height
        self.kernel_num = kernel_num
        self.pad = pad
        self.stride = stride
        self.w_std = w_std
        self.b_val = b_val
        self.has_init = False


    def initJob(self, X):
        """
        init the weight and bias, note this will be called only once
        during the whole life of program
        :param X:
        :return:
        """
        if self.has_init:
            return
        # safely check
        assert len(X.shape) == 4, 'input shape not agree'
        input_channel = X.shape[1]
        input_height = X.shape[2]
        input_width = X.shape[3]

        # input agree
        assert (input_width + 2 * self.pad - self.kernel_width) % self.stride == 0, 'input and the pad, ' \
                                                                                    'stride not agree'
        assert (input_height + 2 * self.pad - self.kernel_height) % self.stride == 0, 'input and the pad, ' \
                                                                                      'stride not agree'

        # save the channel, so we can do safety check later for the weight
        self._input_channel = input_channel

        # the init job for weight and bias
        self.weights = np.random.randn((self.kernel_num, input_channel * self.kernel_height * self.kernel_width))
        self.bias = np.ones((self.kernel_num, 1)) * self.b_val
        self.dw = np.zeros_like(self.weights, dtype=np.float32)
        self.db = np.zeros_like(self.bias, dtype=np.float32)
        if self.w_std is None:
            print 'init convolution layer weights with default...'
            ns = self.kernel_num * input_channel * self.kernel_height * self.kernel_width
            self.weights *= np.sqrt(2.0 / ns)
        else:
            print 'init convolution layer weights with std'.format(self.w_std)
            self.weights *= self.w_std
        self.has_init = True


    def forward(self, X, y):
        """
        compute the output, using the kernel
        actually we do:
        compute im2col: stretch the input to a matrix, multiply it with weights, and reshape back to y
        :param X: the input ternsors, which should be (n, c, h, w)
        :return: the output convolutioned value, which should be (n, kernel_num, new_h, new_w)
        and new_h = (h + 2*padding - kernel_h) / stride + 1, same with width
        weight should be (k, input_channels, kernel_hegith, kernel_width)
        """
        # do the forward job, first is the safety check
        assert len(X.shape) == 4, 'input dim not agree'
        input_dim = X.shape[0]
        input_channel = X.shape[1]
        input_height = X.shape[2]
        input_width = X.shape[3]
        # input agree
        assert (input_width + 2 * self.pad - self.kernel_width) % self.stride == 0, 'input and the pad, ' \
                                                                                    'stride not agree'
        assert (input_height + 2 * self.pad - self.kernel_height) % self.stride == 0, 'input and the pad, ' \
                                                                                      'stride not agree'
        # channel must stay stable, not change
        assert input_channel == self._input_channel, 'input channel and weights not equal, {} vs {}'.format(
            input_channel, self._input_channel
        )

        # now do the forward job
        out_height = (input_height + 2 * self.pad - self.kernel_height) / self.stride + 1
        out_width = (input_width + 2 * self.pad - self.kernel_width) / self.stride + 1
        # get the im2col_data
        col = im2col(X, self.kernel_height, self.kernel_width, self.pad, self.stride)
        out = self.weights * col + self.bias
        out = out.reshape(self.kernel_num, out_height, out_width, input_dim)
        out = out.transpose(3, 0, 1, 2)
        return out



    def backward(self, y, X):
        """
        abstract the weight and bias update, only do the tiny x job
        1\ y with respect to x
        need the col to im trick
        :param Y:
        :return:
        """
        # with respect to x
        dout = y.transpose(1, 2, 3, 0).reshape(self.kernel_num, -1)
        dx_col = self.weights.T * dout
        dx = col2im(dx_col, X.shape, self.kernel_height, self.kernel_width, self.pad, self.stride)
        return dx





