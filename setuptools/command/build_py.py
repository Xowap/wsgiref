from distutils.command.build_py import build_py as _build_py
from distutils.util import convert_path
from glob import glob
import os.path

class build_py(_build_py):

    def initialize_options(self):
        _build_py.initialize_options(self)
        self.package_data = self.distribution.package_data

    def run(self):
        if not self.py_modules and not self.packages:
            return

        if self.py_modules:
            self.build_modules()

        if self.packages:
            self.build_packages()
            self.build_package_data()

        self.byte_compile(_build_py.get_outputs(self,include_bytecode=0))

    def build_package_data(self):
        lastdir = None
        for package, package_dir, outdir, files in self.get_package_data():
            for file in files:
                outfile = os.path.join(outdir,file)
                self.mkpath(os.path.dirname(outfile))
                self.copy_file(
                    os.path.join(package_dir,file), outfile
                )

    def get_outputs(self, include_bytecode=1):
        return _build_py.get_outputs(include_bytecode) + [
            os.path.join(outdir,file)
                for package,package_dir,outdir,files in self.get_package_data()
                    for file in files
        ]

    def get_package_data(self):
        data = []
        for package in self.packages:
            package_dir = self.get_package_dir(package)
            outdir = os.path.join(
                *([self.build_lib]+package.split('.'))
            )
            plen = len(package_dir)+1
            files = [
                file[plen:] for file in self.find_package_files(
                    package, package_dir
                )
            ]
            data.append( (package, package_dir, outdir, files) )
        return data                

    def find_package_files(self, package, package_dir):

        globs = self.package_data.get('',[])+self.package_data.get(package,[])

        files = []

        for pattern in globs:
            files.extend(
                glob(os.path.join(package_dir, convert_path(pattern)))
            )

        return files



























