import unittest

import numpy

from theano import function,config
import theano.tensor as tensor
#from theano.tensor import matrix,max_and_argmax,MaaxAndArgmax,neg
from theano.tensor.elemwise import CAReduce
from theano.tests import unittest_tools as utt


class T_max_and_argmax(unittest.TestCase):
    def test_optimization(self):
        #If we use only the max output, we should replace this op with a faster one.
        data = numpy.asarray(numpy.random.rand(2,3),dtype=config.floatX)
        n = tensor.matrix()

        f = function([n], tensor.max_and_argmax(n,0)[0])
        topo = f.maker.env.toposort()
        assert len(topo)==1
        assert isinstance(topo[0].op, CAReduce)

        f = function([n], tensor.max_and_argmax(n,0))
        topo = f.maker.env.toposort()
        assert len(topo)==1
        assert isinstance(topo[0].op, tensor.MaxAndArgmax)


class T_min_max(unittest.TestCase):
    def setUp(self):
        utt.seed_rng()

    def test_optimization_max(self):
        data = numpy.asarray(numpy.random.rand(2,3),dtype=config.floatX)
        n = tensor.matrix()

        f = function([n],tensor.max(n,0))
        topo = f.maker.env.toposort()
        assert len(topo)==1
        assert isinstance(topo[0].op,CAReduce)
        f(data)


        f = function([n],tensor.max(-n,0))
        topo = f.maker.env.toposort()
        assert len(topo)==2
        assert topo[0].op==tensor.neg
        assert isinstance(topo[1].op,CAReduce)
        f(data)

        f = function([n],-tensor.max(n,0))
        topo = f.maker.env.toposort()
        assert len(topo)==2
        assert isinstance(topo[0].op,CAReduce)
        assert topo[1].op==tensor.neg
        f(data)

        f = function([n],-tensor.max(-n,0))
        topo = f.maker.env.toposort()
        assert len(topo)==1
        assert isinstance(topo[0].op,CAReduce)#min
        f(data)

    def test_optimization_min(self):
        data = numpy.asarray(numpy.random.rand(2,3),dtype=config.floatX)
        n = tensor.matrix()

        f = function([n],tensor.min(n,0))
        topo = f.maker.env.toposort()
        assert len(topo)==1
        assert isinstance(topo[0].op,CAReduce)
        f(data)

        #test variant with neg to make sure we optimize correctly
        f = function([n],tensor.min(-n,0))
        topo = f.maker.env.toposort()
        assert len(topo)==2
        assert isinstance(topo[0].op,CAReduce)#max
        assert topo[1].op==tensor.neg
        f(data)

        f = function([n],-tensor.min(n,0))
        topo = f.maker.env.toposort()
        assert len(topo)==2
        assert topo[0].op==tensor.neg
        assert isinstance(topo[1].op,CAReduce)#max
        f(data)

        f = function([n],-tensor.min(-n,0))
        topo = f.maker.env.toposort()
        assert len(topo)==1
        assert isinstance(topo[0].op,CAReduce)#max
        f(data)
