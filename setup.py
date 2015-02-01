from setuptools import find_packages, setup
setup(name='HApi_raspberry_client',
      version='0.1',
      description='Client for HApi',
      url='http://github.com/storborg/funniest',
      author='Youenn PENNARUN',
      author_email='youenn.pennarun@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['tests', 'tests.*']),
      zip_safe=False,
      include_package_data=True,
      install_requires=['apscheduler', 'pyalsaaudio', 'python-dateutil', 'pytz', 'psutil', 'pyspotify==2.0.0b4'])