from setuptools import find_packages, setup

package_name = 'experiment_python'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kaibuchisoma',
    maintainer_email='72306@toyota.kosen-ac.jp',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
                'Drive_Controller = experiment_python.Drive_Controller:main',
                'Collect_Controller = experiment_python.Collect_Controller:main',
                'communicateWiFi_ESP32 = experiment_python.communicateWiFi_ESP32:main',
                'communicateWebSockets_ESP32 = experiment_python.communicateWebSockets_ESP32:main',
                'communicateWiFiUDP_ESP32 = experiment_python.communicateWiFiUDP_ESP32:main',
                'webserver = experiment_python.webserver:main',
                # 'communicate_ESP32 = experiment_python.communicate_ESP32:main',
        ],
    },
)