from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

setup(
    name = "midcrypt",
    ext_modules = cythonize([Extension("midcrypt", sources=["midcrypt.pyx", "midcrypt_cpp.cpp"], language="c++")]) 
)
