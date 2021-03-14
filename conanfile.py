from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibtorchConan(ConanFile):
    name = "libtorch"
    description = "Tensors and Dynamic neural networks with strong GPU acceleration."
    license = "BSD-3-Clause"
    topics = ("conan", "libtorch", "pytorch", "machine-learning",
              "deep-learning", "neural-network", "gpu", "tensor")
    homepage = "https://pytorch.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "blas": ["eigen", "atlas", "openblas", "mkl", "veclib", "flame", "generic"], # generic means "whatever blas lib found"
        "aten_threading": ["native", "openmp", "tbb"],
        "with_cuda": [True, False],
        "with_cudnn": [True, False],
        "with_nvrtc": [True, False],
        "with_tensorrt": [True, False],
        "with_rocm": [True, False],
        "with_nccl": [True, False],
        "with_fbgemm": [True, False],
        "with_fakelowp": [True, False],
        "with_ffmpeg": [True, False],
        "with_gflags": [True, False],
        "with_leveldb": [True, False],
        "with_lmdb": [True, False],
        "with_metal": [True, False],
        "with_nnapi": [True, False],
        "with_nnpack": [True, False],
        "with_numa": [True, False],
        "observers": [True, False],
        "with_opencl": [True, False],
        "with_opencv": [True, False],
        "profiling": [True, False],
        "with_qnnpack": [True, False],
        "pytorch_qnnpack": [True, False],
        "with_redis": [True, False],
        "with_rocksdb": [True, False],
        "with_snpe": [True, False],
        "with_vulkan": [True, False],
        "vulkan_wrapper": [True, False],
        "vulkan_shaderc_runtime": [True, False],
        "vulkan_relaxed_precision": [True, False],
        "with_xnnpack": [True, False],
        "with_zmq": [True, False],
        "with_zstd": [True, False],
        "with_mkldnn": [True, False],
        "mkldnn_cblas": [True, False],
        "with_mpi": [True, False],
        "with_gloo": [True, False],
        "with_tensorpipe": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "blas": "openblas", # should be mkl on non mobile os
        "aten_threading": "native",
        "with_cuda": False,
        "with_cudnn": False,
        "with_nvrtc": False,
        "with_tensorrt": False,
        "with_rocm": False,
        "with_nccl": False,
        "with_fbgemm": False,
        "with_fakelowp": False,
        "with_ffmpeg": False,
        "with_gflags": False,
        "with_leveldb": False,
        "with_lmdb": False,
        "with_metal": True,
        "with_nnapi": False,
        "with_nnpack": False,
        "with_numa": False,
        "observers": False,
        "with_opencl": False,
        "with_opencv": False,
        "profiling": False,
        "with_qnnpack": False,
        "pytorch_qnnpack": False,
        "with_redis": False,
        "with_rocksdb": False,
        "with_snpe": False,
        "with_vulkan": False,
        "vulkan_wrapper": False,
        "vulkan_shaderc_runtime": False,
        "vulkan_relaxed_precision": False,
        "with_xnnpack": False,
        "with_zmq": False,
        "with_zstd": False,
        "with_mkldnn": False,
        "mkldnn_cblas": False,
        "with_mpi": False,
        "with_gloo": False,
        "with_tensorpipe": False,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os in ["Android", "iOS"]:
            self.options.blas = "eigen"
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_tensorpipe
        if self.settings.os != "iOS":
            del self.options.with_metal
        if self.settings.os != "Android":
            del self.options.with_nnapi
            del self.options.with_snpe
        if self.settings.os != "Linux":
            del self.options.with_numa

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.with_cuda:
            del self.options.with_cudnn
            del self.options.with_nvrtc
            del self.options.with_tensorrt
        if not (self.options.with_cuda or self.options.with_rocm):
            del self.options.with_nccl

    def requirements(self):
        self.requires("cpuinfo/cci.20201217")
        self.requires("eigen/3.3.9")
        self.requires("fmt/7.1.3")
        self.requires("onnx/1.8.1")
        self.requires("protobuf/3.15.5")
        self.requires("pthreadpool/cci.20210218") # only for qnnpack ?
        self.requires("pybind11/2.6.2")
        # self.requires("sleef/3.5.1")
        if self.options.blas == "openblas":
            self.requires("openblas/0.3.13")
        elif self.options.blas in ["atlas", "mkl", "veclib", "flame"]:
            raise ConanInvalidConfiguration("{} recipe not yet available in CCI".format(self.options.blas))
        if self.options.aten_threading == "tbb":
            self.requires("tbb/2020.3")
        if self.options.with_cuda:
            self.output.warn("cuda recipe not yet available in CCI, assuming that NVIDIA CUDA SDK is installed on your system")
        if self.options.with_cudnn:
            self.output.warn("cudnn recipe not yet available in CCI, assuming that NVIDIA CuDNN is installed on your system")
        if self.options.with_tensorrt:
            self.output.warn("tensorrt recipe not yet available in CCI, assuming that NVIDIA TensorRT SDK is installed on your system")
        if self.options.with_fbgemm:
            raise ConanInvalidConfiguration("fbgemm recipe not yet available in CCI")
            self.requires("fbgemm/cci.20210309")
        if self.options.with_gflags:
            self.requires("gflags/2.2.2")
        if self.options.with_nnpack:
            raise ConanInvalidConfiguration("nnpack recipe not yet available in CCI")
            self.requires("nnpack/xxxxx")
        if self.options.get_safe("with_numa"):
            self.requires("libnuma/2.0.14")
        if self.options.with_opencl:
            self.requires("opencl-headers/2020.06.16")
            self.requires("opencl-icd-loader/2020.06.16")
        if self.options.with_opencv:
            self.requires("opencv/4.5.1")
        if self.options.with_qnnpack:
            self.requires("fp16/cci.20200514")
            self.requires("fxdiv/cci.20200417")
            self.requires("psimd/cci.20200517")
        if self.options.with_redis:
            self.requires("hiredis/1.0.0")
        if self.options.with_rocksdb:
            self.requires("rocksdb/6.10.2")
        if self.options.with_xnnpack:
            raise ConanInvalidConfiguration("xnnpack recipe not yet available in CCI")
            self.requires("xnnpack/cci.20210310")
        if self.options.with_zmq:
            self.requires("zeromq/4.3.4")
        if self.options.with_zstd:
            self.requires("zstd/1.4.9")
        if self.options.with_mpi:
            self.requires("openmpi/4.1.0")
        if self.options.with_gloo:
            raise ConanInvalidConfiguration("gloo recipe not yet available in CCI")
        if self.options.get_safe("with_tensorpipe"):
            raise ConanInvalidConfiguration("tensorpipe recipe not yet available in CCI")
            self.requires("tensorpipe/cci.20210309")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pytorch-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        # Inject external fmt
        tools.replace_in_file(os.path.join(self._source_subfolder, "caffe2", "CMakeLists.txt"),
                              "fmt::fmt-header-only", "CONAN_PKG::fmt")
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "Dependencies.cmake"),
                              "add_subdirectory(${PROJECT_SOURCE_DIR}/third_party/fmt)", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "Dependencies.cmake"),
                              "set_target_properties(fmt-header-only PROPERTIES INTERFACE_COMPILE_FEATURES \"\")", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "torch", "CMakeLists.txt"),
                              "fmt::fmt-header-only", "CONAN_PKG::fmt")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ATEN_NO_TEST"] = True
        self._cmake.definitions["BUILD_BINARY"] = True
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["BUILD_CUSTOM_PROTOBUF"] = False
        self._cmake.definitions["BUILD_PYTHON"] = False
        self._cmake.definitions["BUILD_CAFFE2"] = True
        self._cmake.definitions["BUILD_CAFFE2_OPS"] = False
        self._cmake.definitions["BUILD_CAFFE2_MOBILE"] = False
        self._cmake.definitions["CAFFE2_LINK_LOCAL_PROTOBUF"] = False
        self._cmake.definitions["CAFFE2_USE_MSVC_STATIC_RUNTIME"] = False
        self._cmake.definitions["BUILD_TEST"] = False
        self._cmake.definitions["BUILD_STATIC_RUNTIME_BENCHMARK"] = False
        self._cmake.definitions["BUILD_MOBILE_BENCHMARKS"] = False
        self._cmake.definitions["BUILD_MOBILE_TEST"] = False
        self._cmake.definitions["BUILD_JNI"] = False
        self._cmake.definitions["BUILD_MOBILE_AUTOGRAD"] = False
        self._cmake.definitions["INSTALL_TEST"] = False
        self._cmake.definitions["USE_CPP_CODE_COVERAGE"] = False
        self._cmake.definitions["COLORIZE_OUTPUT"] = True
        self._cmake.definitions["USE_ASAN"] = False
        self._cmake.definitions["USE_TSAN"] = False
        self._cmake.definitions["USE_CUDA"] = self.options.with_cuda
        self._cmake.definitions["USE_ROCM"] = self.options.with_rocm
        self._cmake.definitions["CAFFE2_STATIC_LINK_CUDA"] = False
        self._cmake.definitions["USE_CUDNN"] = self.options.get_safe("with_cudnn", False)
        self._cmake.definitions["USE_STATIC_CUDNN"] = False
        self._cmake.definitions["USE_FBGEMM"] = self.options.with_fbgemm
        self._cmake.definitions["USE_FAKELOWP"] = self.options.with_fakelowp
        self._cmake.definitions["USE_FFMPEG"] = self.options.with_ffmpeg
        self._cmake.definitions["USE_GFLAGS"] = self.options.with_gflags
        self._cmake.definitions["USE_LEVELDB"] = self.options.with_leveldb
        self._cmake.definitions["USE_LITE_PROTO"] = False
        self._cmake.definitions["USE_LMDB"] = self.options.with_lmdb
        self._cmake.definitions["USE_METAL"] = self.options.get_safe("with_metal", False)
        self._cmake.definitions["USE_NATIVE_ARCH"] = False
        self._cmake.definitions["USE_NCCL"] = self.options.get_safe("with_nccl", False)
        self._cmake.definitions["USE_STATIC_NCCL"] = False
        self._cmake.definitions["USE_SYSTEM_NCCL"] = False
        self._cmake.definitions["USE_NNAPI"] = self.options.get_safe("with_nnapi", False)
        self._cmake.definitions["USE_NNPACK"] = self.options.with_nnpack
        self._cmake.definitions["USE_NUMA"] = self.options.get_safe("with_numa", False)
        self._cmake.definitions["USE_NVRTC"] = self.options.get_safe("with_nvrtc", False)
        self._cmake.definitions["USE_NUMPY"] = False
        self._cmake.definitions["USE_OBSERVERS"] = self.options.observers
        self._cmake.definitions["USE_OPENCL"] = self.options.with_opencl
        self._cmake.definitions["USE_OPENCV"] = self.options.with_opencv
        self._cmake.definitions["USE_OPENMP"] = self.options.aten_threading == "openmp"
        self._cmake.definitions["USE_PROF"] = self.options.profiling
        self._cmake.definitions["USE_QNNPACK"] = self.options.with_qnnpack
        self._cmake.definitions["USE_PYTORCH_QNNPACK"] = self.options.pytorch_qnnpack
        self._cmake.definitions["USE_REDIS"] = self.options.with_redis
        self._cmake.definitions["USE_ROCKSDB"] = self.options.with_rocksdb
        self._cmake.definitions["USE_SNPE"] = self.options.get_safe("with_snpe", False)
        self._cmake.definitions["USE_SYSTEM_EIGEN_INSTALL"] = True
        self._cmake.definitions["USE_TENSORRT"] = self.options.get_safe("with_tensorrt", False)
        self._cmake.definitions["USE_VULKAN"] = self.options.with_vulkan
        self._cmake.definitions["USE_VULKAN_WRAPPER"] = self.options.vulkan_wrapper
        self._cmake.definitions["USE_VULKAN_SHADERC_RUNTIME"] = self.options.vulkan_shaderc_runtime
        self._cmake.definitions["USE_VULKAN_RELAXED_PRECISION"] = self.options.vulkan_relaxed_precision
        self._cmake.definitions["USE_XNNPACK"] = self.options.with_xnnpack
        self._cmake.definitions["USE_ZMQ"] = self.options.with_zmq
        self._cmake.definitions["USE_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["USE_MKLDNN"] = self.options.get_safe("with_mkldnn", False)
        self._cmake.definitions["USE_MKLDNN_CBLAS"] = self.options.mkldnn_cblas
        self._cmake.definitions["USE_DISTRIBUTED"] = False
        self._cmake.definitions["USE_MPI"] = self.options.with_mpi
        self._cmake.definitions["USE_GLOO"] = self.options.with_gloo
        self._cmake.definitions["USE_TENSORPIPE"] = self.options.get_safe("with_tensorpipe", False)
        self._cmake.definitions["USE_TBB"] = self.options.aten_threading == "tbb"
        self._cmake.definitions["ONNX_ML"] = True
        self._cmake.definitions["HAVE_SOVERSION"] = True

        # FIXME: unvendor some dependencies if possible
        self._cmake.definitions["USE_SYSTEM_LIBS"] = False
        self._cmake.definitions["USE_SYSTEM_CPUINFO"] = True
        self._cmake.definitions["USE_SYSTEM_SLEEF"] = False
        self._cmake.definitions["USE_SYSTEM_GLOO"] = False
        self._cmake.definitions["USE_SYSTEM_FP16"] = True
        self._cmake.definitions["USE_SYSTEM_PTHREADPOOL"] = True
        self._cmake.definitions["USE_SYSTEM_PSIMD"] = True
        self._cmake.definitions["USE_SYSTEM_FXDIV"] = True
        self._cmake.definitions["USE_SYSTEM_BENCHMARK"] = False
        self._cmake.definitions["USE_SYSTEM_ONNX"] = True
        self._cmake.definitions["USE_SYSTEM_XNNPACK"] = True

        self._cmake.definitions["BUILDING_WITH_TORCH_LIBS"] = True
        self._cmake.definitions["BLAS"] = self._blas_cmake_option_value
        self._cmake.configure()
        return self._cmake

    @property
    def _blas_cmake_option_value(self):
        return {
            "eigen": "Eigen",
            "atlas": "ATLAS",
            "openblas": "OpenBLAS",
            "mkl": "MKL",
            "veclib": "vecLib",
            "flame": "FLAME",
            "generic": "Generic"
        }[str(self.options.blas)]

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
