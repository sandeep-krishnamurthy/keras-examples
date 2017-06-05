# keras-examples
Repository of Keras Examples
Credits - We use Keras Resnet builder code from - https://github.com/raghakot/keras-resnet/blob/master/resnet.py

# How to Run
1. Install Keras with MXNet backend - https://github.com/dmlc/keras/wiki/Installation
2. Install MXNet - http://mxnet.io/get_started/install.html
3. Install pre-requisites
```bash
$ pip install memory_profiler
```
4. Download the repository.

```bash
$ git clone --recursive https://github.com/sandeep-krishnamurthy/keras-examples/
```
5. Set the environment variables to describe your machine.

If you are running on a CPU machine
```bash
$ export KERAS_BACKEND=mxnet
$ export MXNET_KERAS_TEST_MACHINE=CPU
```

If you are running on a GPU machine

```bash
$ export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda/lib64/"
$ export KERAS_BACKEND=mxnet
$ export MXNET_KERAS_TEST_MACHINE=GPU
$ export GPU_NUM=16
```

4. Run Resnet Example

```bash
$ python test_cifar_resnet.py
```

5. Run MNIST MLP Example

```bash
$ python test_mnist_mlp.py
```
