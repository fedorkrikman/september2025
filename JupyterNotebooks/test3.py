import tensorflow as tf, pprint
info = tf.sysconfig.get_build_info()
print("Built for CUDA:", info.get("cuda_version"), "cuDNN:", info.get("cudnn_version"))