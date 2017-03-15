from carrie.baselayer import BaseLayer
import numpy as np
class Convolution(BaseLayer):
    """
    this is the convolution layer
    """
    def __init__(self, kernel_width = 3, kernel_height = 3, kernel_num = 64,
                 pad = 1, stride = 1, w_std=None, b_val=0):
        """
        convolution layer params
        :param kernel_width: the kernel width
        :param kernel_height: the kernel height
        :param kernel_num: kernel nums
        :param pad: padding to the input
        :param stride: the stride of kernels
        :param w_std: the std to init weight
        :param b_val: the init val of bias
        """
        assert kernel_width > 0 and kernel_height > 0
        assert kernel_num > 0 and pad > 1 and stride > 1
        self.kernel_width = kernel_width
        self.kernel_height = kernel_height
        self.kernel_num = kernel_num
        self.pad = pad
        self.stride = stride
        self.w_std = w_std
        self.b_val = b_val


    def forward(self, X):
        """
        compute the output, using the kernel
        actually we do 2 things:
        1\ init the kernel weight, which should be (input_c, kernel_height, kernel_width)
        2\ compute im2col: stretch the input to a matrix
        :param X: the input ternsors, which should be (n, c, h, w)
        :return: the output convolutioned value, which should be (n, kernel_num, new_h, new_w)
        and new_h = (h + 2*padding - kernel_h) / stride + 1, same with width
        weight should be (k, input_channels, kernel_hegith, kernel_width)
        """

        # safely check
        assert len(X.shape) == 4
        input_channel = X.shape[1]
        input_nums = X.shape[0]
        input_height = X.shape[2]
        input_width = X.shape[3]

        # input agree
        assert (input_width + 2 * self.pad - self.kernel_width) % self.stride == 0
        assert  (input_height + 2 * self.pad - self.kernel_height) % self.stride == 0

        # weight init job
        self.weights = np.random.randn((self.kernel_num, input_channel, self.kernel_height,
                                        self.kernel_width))
        self.bias = np.ones((self.kernel_num, 1, 1, 1)) * self.b_val
        if self.w_std is None:
            print 'init convolution layer weights with default...'
            ns = self.kernel_num * input_channel * self.kernel_height * self.kernel_width
            self.weights *= np.sqrt(2.0 / ns)
        else:
            print 'init convolution layer weights with std'.format(self.w_std)
            self.weights *= self.w_std



        # do the im2col job

        #// todo


    def backward(self, Y):
        pass