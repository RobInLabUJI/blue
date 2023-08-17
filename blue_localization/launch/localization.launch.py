# Copyright 2023, Evan Palmer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
)
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    """Generate a launch description for the localization package.

    Returns:
        The localization ROS 2 launch description.
    """
    args = [
        DeclareLaunchArgument(
            "localization_config_filepath",
            default_value=None,
            description="The path to the localization configuration YAML file.",
        ),
        DeclareLaunchArgument(
            "ekf_config_filepath",
            default_value=None,
            description="The path to the EKF configuration YAML file.",
        ),
        DeclareLaunchArgument(
            "estimator",
            default_value="ardusub_ekf",
            choices=["ardusub_ekf", "blue_ekf", "all"],
            description="The state estimator to use for localization.",
        ),
        DeclareLaunchArgument(
            "sources",
            default_value="['qualisys_mocap']",
            description=(
                "The localization sources to stream from. Multiple sources can"
                " be loaded at once. If no sources need to be launched, then this can"
                " be set to an empty list."
            ),
        ),
        DeclareLaunchArgument(
            "localizers",
            default_value="['gazebo_localizer']",
            description=(
                "The localizers to collect state information from. Multiple"
                " localizers can be loaded at once. If no localizers need to be"
                " launched, then this can be set to an empty list."
            ),
        ),
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description=("Use the simulated Gazebo clock."),
        ),
    ]

    includes = [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [FindPackageShare("blue_localization"), "ekf.launch.py"]
                )
            ),
            launch_arguments={
                "config_filepath": LaunchConfiguration("ekf_config_filepath"),
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }.items(),
            condition=IfCondition(
                PythonExpression(
                    ["'", LaunchConfiguration("estimator"), "' in ['all', 'blue_ekf']"]
                )
            ),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [FindPackageShare("blue_localization"), "sources.launch.py"]
                )
            ),
            launch_arguments={
                "config_filepath": LaunchConfiguration("localization_config_filepath"),
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [FindPackageShare("blue_localization"), "localizers.launch.py"]
                )
            ),
            launch_arguments={
                "config_filepath": LaunchConfiguration("localization_config_filepath"),
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            }.items(),
        ),
    ]

    return LaunchDescription(args + includes)
