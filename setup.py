from setuptools import setup

setup(name='funtool-ipro-processes',
        version='0.0.25',
        description='Ipro processes to be used with the FUN Tool ',
        author='Active Learning Lab',
        author_email='pjanisiewicz@gmail.com',
        license='MIT',
        packages=[
            'funtool_ipro_processes',
            'funtool_ipro_processes.adaptors',
            'funtool_ipro_processes.reporters',
            'funtool_ipro_processes.state_measures'
        ],
        install_requires=[
            'funtool',
            'funtool-common-processes',
            'funtool-mysql-processes'
        ],
        classifiers=[ 
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4'
        ],  
        zip_safe=False)
