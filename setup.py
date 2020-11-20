import setuptools

setuptools.setup(
      name='KubunConfector',
      version='0.1.3-7',
      description='Kubun Data-Preparation Utility',
      author='Raphael Martin',
      author_email='raphael@kubun.io',
      url='https://github.com/ra-martin/KubunConfector',
      packages=['kubunconfector'],
      install_requires=['typeguard'],
      python_requires='>=3.8',
      setup_requires=['wheel']
)