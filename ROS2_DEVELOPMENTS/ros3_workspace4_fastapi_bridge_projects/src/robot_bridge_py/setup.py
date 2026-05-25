from setuptools import find_packages, setup

package_name = 'robot_bridge_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        (
            'share/' + package_name,
            ['package.xml'],
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='karthik',
    maintainer_email='karthik@example.com',
    description='ROS2 Robot Bridge Publisher',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_publisher = robot_bridge_py.robot_publisher:main',
            'bridge_node = robot_bridge_py.bridge_node:main',
        ],
    },
)